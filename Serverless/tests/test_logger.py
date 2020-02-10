import textwrap

from datetime import datetime


class TestLogger:

    LOG_SAVE_PATH = 'tests/logs'
    HEADER_SIZE = 60
    WRAPPER = textwrap.TextWrapper(width=120)
    LOG_STORAGE = []
    ANSI_COLORS = {
        'magenta': '\u001b[35m',
        'yellow': '\u001b[33m',
        'red': '\u001b[31m',
        'green': '\u001b[32m',
        'default': '\u001b[0m'
    }

    @classmethod
    def log_alert(cls, msg, print_on_screen=True):
        msg = f"{cls.ANSI_COLORS.get('yellow')}{datetime.utcnow().strftime('%H:%M:%S')}:UTC - " \
              f"{msg}{cls.ANSI_COLORS.get('default')}"
        cls.log(msg, print_on_screen)

    @classmethod
    def log_error(cls, msg, print_on_screen=True):
        msg = f"{cls.ANSI_COLORS.get('red')}{datetime.utcnow().strftime('%H:%M:%S')}:UTC - " \
              f"{msg}{cls.ANSI_COLORS.get('default')}"
        cls.log(msg, print_on_screen)

    @classmethod
    def paint_red(cls, msg):
        return f"{cls.ANSI_COLORS.get('red')}{msg}{cls.ANSI_COLORS.get('default')}"

    @classmethod
    def paint_green(cls, msg):
        return f"{cls.ANSI_COLORS.get('green')}{msg}{cls.ANSI_COLORS.get('default')}"

    @classmethod
    def paint_status(cls, msg, success):
        if success:
            return f"{cls.ANSI_COLORS.get('green')}{msg}{cls.ANSI_COLORS.get('default')}"
        else:
            return f"{cls.ANSI_COLORS.get('red')}{msg}{cls.ANSI_COLORS.get('default')}"

    @classmethod
    def log(cls, msg, print_on_screen=True, ignore_wrap=False):
        if ignore_wrap:
            if print_on_screen: print(msg)
            cls.LOG_STORAGE.append(msg)
        else:
            wrap_list = cls.WRAPPER.wrap(text=msg)
            for wrap_line in wrap_list:
                if print_on_screen: print(wrap_line)
                cls.LOG_STORAGE.append(wrap_line)

    @classmethod
    def save_logs(cls):
        log_path_and_name = f'{cls.LOG_SAVE_PATH}/{datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")}.txt'
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
        :param size (int): Horizontal size of the header in number of characters.
        :return: None
        """
        color, default = cls.ANSI_COLORS.get('magenta'), cls.ANSI_COLORS.get('default')
        size = cls.HEADER_SIZE
        cls.log('', ignore_wrap=True)
        main = '{' + "".join([' ' for x in range(int(size/2)-int((len(content)/2)))]) + content
        main += "".join([' ' for x in range(size-len(main))]) + '}'
        upper_line = ' /' + "".join(['=' for x in range(len(main)-4)]) + '\\'
        lower_line = ' \\' + "".join(['=' for x in range(len(main)-4)]) + '/'
        cls.log(f'{color}{upper_line}\n{main}\n{lower_line}{default}', ignore_wrap=True)
        cls.log('', ignore_wrap=True)