import os, subprocess, textwrap
from datetime import datetime
import time

from tests.tests import Tests

DEPLOY = True
FULL = False
FUNCTIONS_TO_DEPLOY = ['add-picture']

UPDATE_REPOSITORY = True
MAIN_BRANCH = True
GIT_COMMIT_MESSAGE = 'Latest updates'

TEST_FUNCTIONS = True
PRINT_FUNCTION_LOGS = False
FUNCTIONS_TO_TEST = [
    ('add-picture', 'tests/mock_add_picture_a.json', 200),
    # ('add-picture', 'tests/mock_add_picture_b.json', 200)
]


class DeployAndTest:

    WRAPPER = textwrap.TextWrapper(width=250)
    LOG_WRAPPER = textwrap.TextWrapper(width=150)
    HEADER_SIZE = 60
    AUTO_SAVE_BRANCH = f'auto-save-{datetime.now().strftime("%Y-%m-%d")}'
    MAIN_WORKING_BRANCH = 'master'
    LOG_SAVE_PATH = 'tests/logs'
    ANSI_COLORS = {
        'magenta': '\u001b[35m',
        'yellow': '\u001b[33m',
        'red': '\u001b[31m',
        'default': '\u001b[0m'
    }
    LOG_STORAGE = []

    def __init__(self):

        # Start duration measuring
        duration = time.time()

        # Deploy service
        self.service_deployment()

        # Git procedures
        self.git_procedures()

        # Testing procedures
        self.test_functions()

        # Print procedure time measuring
        self.log_yellow(f'Elapsed (test and deploy execution): {self.get_duration(duration)}')

        self.save_logs()

    def service_deployment(self):
        if not DEPLOY: return
        duration = time.time()
        self.print_header('SERVICE DEPLOYMENT')
        if FULL:
            self.execute_and_log('sls deploy', 'Deploy full service...')
        else:
            for function_name in FUNCTIONS_TO_DEPLOY:
                self.execute_and_log(f'sls deploy function --function {function_name}',
                                     f"Deploy single function: '{function_name}'")
        self.log_yellow(f'Elapsed: {self.get_duration(duration)}')

    def git_procedures(self):
        if not UPDATE_REPOSITORY: return
        duration = time.time()
        self.print_header('UPDATE REPOSITORY')
        self.execute_and_log('git branch', 'Present current GIT branches...')
        self.execute_and_log('git add .', 'Execute GIT add all...')
        self.execute_and_log(f'git commit -m "{GIT_COMMIT_MESSAGE}"',
                             f"Committing with message: '{GIT_COMMIT_MESSAGE}'...")

        if MAIN_BRANCH:
            self.execute_and_log(f'git push origin {self.MAIN_WORKING_BRANCH}',
                                 f"Executing GIT push to '{self.MAIN_WORKING_BRANCH}' branch...")
        else:
            self.execute_and_log(f'git checkout -b {self.AUTO_SAVE_BRANCH}',
                                 f'Creating local auto-backup branch "{self.AUTO_SAVE_BRANCH}"...')
            self.execute_and_log(f'git push origin {self.AUTO_SAVE_BRANCH}',
                                 f"Pushing to remote auto-backup branch...")
            self.execute_and_log(f'git checkout {self.MAIN_WORKING_BRANCH}',
                                 f"Switching back to local main branch '{self.MAIN_WORKING_BRANCH}'...")
            self.execute_and_log(f'git branch -D {self.AUTO_SAVE_BRANCH}',
                                 f"Deleting local auto-backup branch...")
        self.log_yellow(f'Elapsed: {self.get_duration(duration)}')

    def test_functions(self):
        if not TEST_FUNCTIONS: return
        total_duration = time.time()
        self.print_header('TESTING PROCEDURES')
        for test in FUNCTIONS_TO_TEST:
            duration = time.time()
            name = test[0]
            params = test[1]
            expected = test[2]
            command = f'sls invoke -f {name} -l'
            if params.strip(): command += f' --path {params.strip()}'
            logs = self.execute_and_log(command, f'Testing "{name}" function with parameters  "{params}". '
                                                 f'Expect: "{expected}"...', PRINT_FUNCTION_LOGS)
            Tests(name, logs, expected)
            self.log_yellow(f"Elapsed ('{name}''): {self.get_duration(duration)}")
        self.log_yellow(f'Elapsed (all tests): {self.get_duration(total_duration)}')

    def execute_and_log(self, execute, log, log_details = True):
        self.log_yellow(log)
        logs = []
        p = subprocess.Popen(execute, bufsize=1, stdin=open(os.devnull), shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stds = [p.stdout, p.stderr]
        for i, std in enumerate(stds):
            for line in iter(std.readline, b''):
                log = line.decode("utf-8").replace('\n', '')
                logs.append(log)
                wrap_list = self.WRAPPER.wrap(text=log)
                for wrap_line in wrap_list:
                    if i == 0:
                        self.log(wrap_line, log_details)
                    else:
                        self.log(f"{self.ANSI_COLORS.get('red')}{wrap_line}{self.ANSI_COLORS.get('default')}",
                                 log_details)
        p.stdout.close()
        p.wait()
        return logs

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
        cls.log('')
        main = '{' + "".join([' ' for x in range(int(size/2)-int((len(content)/2)))]) + content
        main += "".join([' ' for x in range(size-len(main))]) + '}'
        upper_line = ' /' + "".join(['=' for x in range(len(main)-4)]) + '\\'
        lower_line = ' \\' + "".join(['=' for x in range(len(main)-4)]) + '/'
        cls.log(f'{color}{upper_line}\n{main}\n{lower_line}{default}')
        cls.log('')

    @classmethod
    def log_yellow(cls, msg):
        msg = f"{cls.ANSI_COLORS.get('yellow')}{msg}{cls.ANSI_COLORS.get('default')}"
        cls.log(msg)

    @classmethod
    def log(cls, msg, print_on_screen = True):
        if print_on_screen: print(msg)
        cls.LOG_STORAGE.append(msg)

    @classmethod
    def save_logs(cls):
        log_path_and_name = f'{cls.LOG_SAVE_PATH}/{datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")}.txt'
        strings_to_replace = [v for k, v in cls.ANSI_COLORS.items()]
        with open(log_path_and_name, "w") as txt_file:
            for line in cls.LOG_STORAGE:
                for reps in strings_to_replace:
                    line = line.replace(reps, '')
                wrap_list = cls.LOG_WRAPPER.wrap(text=line)
                for wrap_line in wrap_list:
                    txt_file.write(''.join(wrap_line) + '\n')

    @staticmethod
    def get_duration(start):
        return str(round(time.time() - start, 3)) + 's'


if __name__ == "__main__":
    dt = DeployAndTest()