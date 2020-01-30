import os, json, subprocess, textwrap
from datetime import datetime


FULL_DEPLOY = False
FUNCTIONS_TO_DEPLOY = ['add-picture']

UPDATE_MAIN_BRANCH = True
GIT_COMMIT_MESSAGE = 'Latest updates'

TEST_FUNCTIONS = True
LOG_TEST_DETAILS = False
FUNCTIONS_TO_TEST = [
    ('add-picture', 'tests/mock_add_picture_a.json'),
    # ('add-picture', 'tests/mock_add_picture_b.json')
]


class DeployAndTest:

    WRAPPER = textwrap.TextWrapper(width=250)
    HEADER_SIZE = 60
    CONFIG_FILE_PATH = 'tests/config.json'
    AUTO_SAVE_BRANCH = f'auto-save-{datetime.now().strftime("%Y-%m-%d")}'
    MAIN_WORKING_BRANCH = 'master'

    def __init__(self):

        # Read config JSON
        with open(self.CONFIG_FILE_PATH) as json_file:
            self.project_path = json.load(json_file)['project_paths']['home']

        # Deploy service
        self.print_header('SERVICE DEPLOYMENT')
        if FULL_DEPLOY:
            self.execute_and_log('sls deploy', 'Deploy full service (sls deploy)...')
        else:
            for function_name in FUNCTIONS_TO_DEPLOY:
                self.execute_and_log(f'sls deploy function --function {function_name}',
                                     f"Deploy single function: '{function_name}' "
                                     f"(sls deploy function --function <function_name>)")

        # Git procedures
        self.print_header('UPDATE REPOSITORY')
        self.execute_and_log('git branch', 'Present current GIT branches...')
        self.execute_and_log('git add .', 'Execute GIT add all...')
        self.execute_and_log(f'git commit -m "{GIT_COMMIT_MESSAGE}"',
                             f"Committing with message: '{GIT_COMMIT_MESSAGE}'...")

        if UPDATE_MAIN_BRANCH:
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

        # Testing procedures
        if TEST_FUNCTIONS:
            self.print_header('TESTING PROCEDURES')
            for test in FUNCTIONS_TO_TEST:
                name = test[0]
                params = ''
                try:
                    params = test[1]
                except:
                    pass
                command = f'sls invoke -f {name} -l'
                if params.strip(): command += f' --path {params.strip()}'
                logs = self.execute_and_log(command, f'Testing "{name}" function with parameters '
                    f'"{params}" (sls invoke -f <name> -l --path <params_path>)...', LOG_TEST_DETAILS)
                print('EXTRACTED DICTS:')
                dicts = self.parse_dicts_from_strings(''.join(logs).replace('true', 'True').replace('false', 'False'))
                if len(dicts)>0:
                    wrap_list = self.WRAPPER.wrap(text=str(dicts[0]))
                    for line in wrap_list:
                        print(line)

    def execute_and_log(self, execute, log, log_details = True):
        print(f'\u001b[33m{log}\x1b[0m')
        logs = []
        p = subprocess.Popen(execute, bufsize=1, stdin=open(os.devnull), shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        for line in iter(p.stdout.readline, b''):
            log = line.strip().decode("utf-8").replace('\n', '')
            logs.append(log)
            wrap_list = self.WRAPPER.wrap(text=log)
            for wrap_line in wrap_list:
                if log_details: print(wrap_line)
        for line in iter(p.stderr.readline, b''):
            log = line.strip().decode("utf-8").replace('\n', '')
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

    @staticmethod
    def parse_dicts_from_strings(value):
        dicts = []
        current_check = ''
        open_bracers = 0
        for x in value:
            if x == '{':
                open_bracers += 1
            elif x == '}' and open_bracers > 0:
                open_bracers -= 1
                if open_bracers == 0:
                    current_check += x
                    dicts.append(eval(current_check))
                    current_check = ''
                    continue
            if open_bracers > 0:
                current_check += x
        return dicts


if __name__ == "__main__":
    dt = DeployAndTest()