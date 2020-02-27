import os, textwrap, time
from datetime import datetime


class TestLogger:
    """
    Test logger object class. Formats, prints, and saves messages to local logs folder.
    """

    LOG_SAVE_PATH = 'tests/logs'                    # :str: Default log saving location.
    HEADER_SIZE = 60                                # :int: Length of the headers.
    WRAPPER = textwrap.TextWrapper(width=105)       # :TextWrapper: Maximum amount of characters per line.
    MAXIMUM_LOG_FILES_STORED = 5                    # :int: Maximum amount of stored log files.
    LOG_STORAGE = []                                # :list: Logs memory storage.
    TIMEZONE = 'UTC'
    ANSI = {                                        # :dict: ANSI decorations for terminal.
        'magenta': '\u001b[35m',
        'yellow': '\u001b[33m',
        'red': '\u001b[31m',
        'green': '\u001b[32m',
        'bg_green': '\u001b[42m',
        'bg_red': '\u001b[41m',
        'bold': '\u001b[1m',
        'underline': '\u001b[4m',
        'reversed': '\u001b[7m',
        'default': '\u001b[0m'
    }

    @classmethod
    def log_alert(cls, msg: str, print_on_screen: bool = True):
        """
        Logs default alert message.
        :param msg: Message to be logged.
        :param print_on_screen: Flags whether message is to be printed on screen of only on file.
        :return: void
        """

        yellow, reverse, default = cls.ANSI.get('yellow'), cls.ANSI.get('reversed'), cls.ANSI.get('default')
        msg = f"{yellow}{reverse}{cls.__get_now('%H:%M:%S')}{default}{yellow} {msg}{default}"
        cls.log(msg, print_on_screen)

    @classmethod
    def log_error(cls, msg: str, print_on_screen: bool = True):
        """
        Logs default error message.
        :param msg: Message to be logged.
        :param print_on_screen: Flags whether message is to be printed on screen of only on file.
        :return: void
        """

        red, reverse, default = cls.ANSI.get('red'), cls.ANSI.get('reversed'), cls.ANSI.get('default')
        msg = f"{red}{reverse}{cls.__get_now('%H:%M:%S')}{default}{red} {msg}{default}"
        cls.log(msg, print_on_screen)

    @classmethod
    def underline(cls, msg: str) -> str:
        """
        Formats provided string with underline.
        :param msg: Message to be formatted.
        :return: String containing formatted message.
        """

        return f"{cls.ANSI.get('underline')}{msg}{cls.ANSI.get('default')}"

    @classmethod
    def bold(cls, msg: str) -> str:
        """
        Formats provided string with bold.
        :param msg: Message to be formatted.
        :return: String containing formatted message.
        """

        return f"{cls.ANSI.get('bold')}{msg}{cls.ANSI.get('default')}"

    @classmethod
    def invert(cls, msg: str) -> str:
        """
        Formats provided string with inverted color.
        :param msg: Message to be formatted.
        :return: String containing formatted message.
        """

        return f"{cls.ANSI.get('invert')}{msg}{cls.ANSI.get('default')}"

    @classmethod
    def paint_status(cls, msg: str, success: bool) -> str:
        """
        Colors a given message green or red depending on success factor.
        :param msg: Message to be colored.
        :param success: Success factor.
        :return: String containing formatted message.
        """

        if success:
            return f"{cls.ANSI.get('green')}{msg}{cls.ANSI.get('default')}"
        else:
            return f"{cls.ANSI.get('red')}{msg}{cls.ANSI.get('default')}"

    @classmethod
    def paint_status_bg(cls, msg: str, success: bool) -> str:
        """
        Colors a given message background green or red depending on success factor.
        :param msg: Message to be colored.
        :param success: Success factor.
        :return: String containing formatted message.
        """

        if success:
            return f"{cls.ANSI.get('green')}{cls.ANSI.get('reversed')}{msg}{cls.ANSI.get('default')}"
        else:
            return f"{cls.ANSI.get('red')}{cls.ANSI.get('reversed')}{msg}{cls.ANSI.get('default')}"

    @classmethod
    def get_status_string(cls, status: bool) -> str:
        """
        Returns a standard stylized status indicating string.
        :param status: Success factor.
        :return: String containing status indicator.
        """

        # If status is positive (true), returns standard stylized 'test passed' string.
        if status: return cls.paint_status('(+)', True)

        # If status is negative (false), returns standard stylized 'test failed' string.
        else: return cls.paint_status('(-)', False)

    @classmethod
    def log(cls, line, print_on_screen=True, ignore_wrap=False):
        """
        Trims, prints and saves log lines to memory.
        :param line: Line to be analyzed.
        :param print_on_screen: Flag to whether print line on screen or only on file.
        :param ignore_wrap: Flag to ignore line wrapper if needed.
        :return: void.
        """

        if ignore_wrap:
            if print_on_screen: print(line)
            cls.LOG_STORAGE.append(line)
        else:
            wrap_list = cls.WRAPPER.wrap(text=line)
            for wrap_line in wrap_list:
                if print_on_screen: print(wrap_line)
                cls.LOG_STORAGE.append(wrap_line)

    @classmethod
    def save_logs(cls):
        """
        Saves acquired log lines to .txt file at default log file location with auto generated name.
        :return: void.
        """

        # Removes oldest log file if maximum threshold has been reached.
        path = cls.LOG_SAVE_PATH
        log_files = [f"{path}/{name}" for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]
        no_of_logs = len(log_files)
        if no_of_logs >= cls.MAXIMUM_LOG_FILES_STORED:
            oldest_file = min(log_files, key=os.path.getctime)
            os.remove(oldest_file)

        # Saves current log lines in new log file.
        log_path_and_name = f'{path}/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt'
        strings_to_replace = [v for k, v in cls.ANSI.items()]
        with open(log_path_and_name, "w") as txt_file:
            for line in cls.LOG_STORAGE:
                for reps in strings_to_replace:
                    line = line.replace(reps, '')
                txt_file.write(''.join(line) + '\n')

    @classmethod
    def print_header(cls, content):
        """
        Prints main header on log screen.
        :param content (string): Text to be displayed on main header.
        :return: void
        """

        color, default = cls.ANSI.get('magenta'), cls.ANSI.get('default')
        size = cls.HEADER_SIZE
        cls.log('', ignore_wrap=True)
        main = '{' + "".join([' ' for x in range(int(size/2)-int((len(content)/2)))]) + content
        main += "".join([' ' for x in range(size-len(main))]) + '}'
        upper_line = ' /' + "".join(['=' for x in range(len(main)-4)]) + '\\'
        lower_line = ' \\' + "".join(['=' for x in range(len(main)-4)]) + '/'
        cls.log(f'{cls.ANSI.get("bold")}{color}{upper_line}\n{main}\n{lower_line}{default}', ignore_wrap=True)
        cls.log('', ignore_wrap=True)

    @classmethod
    def __get_now(cls, formatting: str = '%H:%M:%S') -> str:
        """
        Returns current formatted time in configured timezone.
        :param formatting: Time format.
        :return: String containing current time.
        """

        if cls.TIMEZONE == 'UTC':
            return f"{datetime.utcnow().strftime(formatting)}:UTC:"
        else:
            return f"{datetime.now().strftime(formatting)}:LCL:"

    @classmethod
    def timeit(cls, name):
        """
        Decorator to log current function execution time.
        :param name: Procedure name to be displayed.
        :return: void.
        """

        def decorator(method):
            def measure(*args, **kw):
                ts = time.time()
                result = method(*args, **kw)
                te = time.time()
                tf = str(round(te - ts, 3)) + 's'
                if name:
                    cls.log_alert(f"Elapsed ({name}): {tf}")
                else:
                    cls.log_alert(f"Elapsed: {tf}")
                return result
            return measure
        return decorator
