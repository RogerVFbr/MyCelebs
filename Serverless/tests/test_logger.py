import textwrap

from datetime import datetime
import time


class TestLogger:
    """
    Test logger object class. Formats, prints, and saves messages to local logs folder.
    """

    LOG_SAVE_PATH = 'tests/logs'                    # :str: Default log saving location.
    HEADER_SIZE = 60                                # :int: Length of the headers.
    WRAPPER = textwrap.TextWrapper(width=105)       # :TextWrapper: Maximum amount of characters per line.
    LOG_STORAGE = []                                # :list: Logs memory storage.
    ANSI_COLORS = {                                 # :dict: ANSI decorations for terminal.
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
        yellow, reversed, default = cls.ANSI_COLORS.get('yellow'), cls.ANSI_COLORS.get('reversed'), \
                                    cls.ANSI_COLORS.get('default')
        msg = f"{yellow}{reversed}{datetime.utcnow().strftime('%H:%M:%S')}:UTC:{default}{yellow} {msg}{default}"
        cls.log(msg, print_on_screen)

    @classmethod
    def log_error(cls, msg: str, print_on_screen: bool = True):
        """
        Logs default error message.
        :param msg: Message to be logged.
        :param print_on_screen: Flags whether message is to be printed on screen of only on file.
        :return: void
        """
        red, reversed, default = cls.ANSI_COLORS.get('red'), cls.ANSI_COLORS.get('reversed'), \
                                  cls.ANSI_COLORS.get('default')
        msg = f"{red}{reversed}{datetime.utcnow().strftime('%H:%M:%S')}:UTC:{default}{red} {msg}{default}"
        cls.log(msg, print_on_screen)

    @classmethod
    def underline(cls, msg: str) -> str:
        """
        Formats provided string with underline.
        :param msg: Message to be formatted.
        :return: String containing formatted message.
        """

        return f"{cls.ANSI_COLORS.get('underline')}{msg}{cls.ANSI_COLORS.get('default')}"

    @classmethod
    def bold(cls, msg: str) -> str:
        """
        Formats provided string with bold.
        :param msg: Message to be formatted.
        :return: String containing formatted message.
        """

        return f"{cls.ANSI_COLORS.get('bold')}{msg}{cls.ANSI_COLORS.get('default')}"

    @classmethod
    def invert(cls, msg: str) -> str:
        """
        Formats provided string with inverted color.
        :param msg: Message to be formatted.
        :return: String containing formatted message.
        """

        return f"{cls.ANSI_COLORS.get('invert')}{msg}{cls.ANSI_COLORS.get('default')}"

    @classmethod
    def paint_status(cls, msg: str, success: bool) -> str:
        """
        Colors a given message green or red depending on success factor.
        :param msg: Message to be colored.
        :param success: Success factor.
        :return: String containing formatted message.
        """

        if success:
            return f"{cls.ANSI_COLORS.get('green')}{msg}{cls.ANSI_COLORS.get('default')}"
        else:
            return f"{cls.ANSI_COLORS.get('red')}{msg}{cls.ANSI_COLORS.get('default')}"

    @classmethod
    def paint_status_bg(cls, msg: str, success: bool) -> str:
        """
        Colors a given message background green or red depending on success factor.
        :param msg: Message to be colored.
        :param success: Success factor.
        :return: String containing formatted message.
        """

        if success:
            return f"{cls.ANSI_COLORS.get('green')}{cls.ANSI_COLORS.get('reversed')}" \
                f"{msg}{cls.ANSI_COLORS.get('default')}"
        else:
            return f"{cls.ANSI_COLORS.get('red')}{cls.ANSI_COLORS.get('reversed')}" \
                f"{msg}{cls.ANSI_COLORS.get('default')}"

    @classmethod
    def get_status_string(cls, status: bool) -> str:
        """
        Returns a standard stylized status indicating string.
        :param status: Success factor.
        :return: String containing status indicator.
        """

        # If status is positive (true), returns standard stylized 'test passed' string.
        if status:
            return cls.paint_status('(+)', True)

        # If status is negative (false), returns standard stylized 'test failed' string.
        else:
            return cls.paint_status('(-)', False)

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

        log_path_and_name = f'{cls.LOG_SAVE_PATH}/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt'
        strings_to_replace = [v for k, v in cls.ANSI_COLORS.items()]
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

        color, default = cls.ANSI_COLORS.get('magenta'), cls.ANSI_COLORS.get('default')
        size = cls.HEADER_SIZE
        cls.log('', ignore_wrap=True)
        main = '{' + "".join([' ' for x in range(int(size/2)-int((len(content)/2)))]) + content
        main += "".join([' ' for x in range(size-len(main))]) + '}'
        upper_line = ' /' + "".join(['=' for x in range(len(main)-4)]) + '\\'
        lower_line = ' \\' + "".join(['=' for x in range(len(main)-4)]) + '/'
        cls.log(f'{cls.ANSI_COLORS.get("bold")}{color}{upper_line}\n{main}\n{lower_line}{default}', ignore_wrap=True)
        cls.log('', ignore_wrap=True)

    @classmethod
    def timeit(cls, name):
        """
        Decorator to log current function execution time.
        :param name: Procedure name to be displayed.
        :return: void.
        """

        def decorator(method):
            def timed(*args, **kw):
                ts = time.time()
                result = method(*args, **kw)
                te = time.time()
                tf = str(round(te - ts, 3)) + 's'
                if name:
                    cls.log_alert(f"Elapsed ({name}): {tf}")
                else:
                    cls.log_alert(f"Elapsed: {tf}")
                return result
            return timed
        return decorator
