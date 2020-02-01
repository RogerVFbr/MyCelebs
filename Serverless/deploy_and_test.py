import os, json, subprocess, textwrap
from datetime import datetime

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
    HEADER_SIZE = 60
    AUTO_SAVE_BRANCH = f'auto-save-{datetime.now().strftime("%Y-%m-%d")}'
    MAIN_WORKING_BRANCH = 'master'

    def __init__(self):

        # Deploy service
        self.service_deployment()

        # Git procedures
        self.git_procedures()

        # Testing procedures
        self.test_functions()

    def service_deployment(self):
        if not DEPLOY: return
        self.print_header('SERVICE DEPLOYMENT')
        if FULL:
            self.execute_and_log('sls deploy', 'Deploy full service...')
        else:
            for function_name in FUNCTIONS_TO_DEPLOY:
                self.execute_and_log(f'sls deploy function --function {function_name}',
                                     f"Deploy single function: '{function_name}'")

    def git_procedures(self):
        if not UPDATE_REPOSITORY: return
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

    def test_functions(self):
        if not TEST_FUNCTIONS: return
        self.print_header('TESTING PROCEDURES')
        for test in FUNCTIONS_TO_TEST:
            name = test[0]
            params = test[1]
            expected = test[2]
            command = f'sls invoke -f {name} -l'
            if params.strip(): command += f' --path {params.strip()}'
            logs = self.execute_and_log(command, f'Testing "{name}" function with parameters  "{params}"...',
                                        PRINT_FUNCTION_LOGS)

            Tests(name, logs, expected)

    def execute_and_log(self, execute, log, log_details = True):
        print(f'\u001b[33m{log}\x1b[0m')
        logs = []
        p = subprocess.Popen(execute, bufsize=1, stdin=open(os.devnull), shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        for line in iter(p.stdout.readline, b''):
            log = line.decode("utf-8").replace('\n', '')
            logs.append(log)
            wrap_list = self.WRAPPER.wrap(text=log)
            for wrap_line in wrap_list:
                if log_details: print(wrap_line)
        for line in iter(p.stderr.readline, b''):
            log = line.decode("utf-8").replace('\n', '')
            logs.append(log)
            wrap_list = self.WRAPPER.wrap(text=log)
            for wrap_line in wrap_list:
                if log_details: print('\u001b[31m' + wrap_line + '\u001b[0m')
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
        color, default = '\u001b[35m', '\u001b[0m'
        size = cls.HEADER_SIZE
        print('')
        main = '{' + "".join([' ' for x in range(int(size/2)-int((len(content)/2)))]) + content
        main += "".join([' ' for x in range(size-len(main))]) + '}'
        upper_line = ' /' + "".join(['=' for x in range(len(main)-4)]) + '\\'
        lower_line = ' \\' + "".join(['=' for x in range(len(main)-4)]) + '/'
        print(f'{color}{upper_line}\n{main}\n{lower_line}{default}')
        print('')


if __name__ == "__main__":
    dt = DeployAndTest()