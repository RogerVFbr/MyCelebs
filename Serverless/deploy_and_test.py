import os, subprocess, textwrap, time
from datetime import datetime
from tests.tests import Tests
from tests.test_logger import TestLogger as tl

DEPLOY = True
FULL = False
FUNCTIONS_TO_DEPLOY = ['add-picture', 'celeb-recognition']

UPDATE_REPOSITORY = True
MAIN_BRANCH = True
GIT_COMMIT_MESSAGE = 'Solving multiple SQS trigger executions.'

TEST_FUNCTIONS = True
PRINT_LOGS_ON_SCREEN = False
FUNCTIONS_TO_TEST = [
    ('add-picture', 'tests/mock_add_picture_a.json', 200, ['celeb-recognition']),
    # ('add-picture', 'tests/mock_add_picture_b.json', 200)
]


class DeployAndTest:

    # WRAPPER = textwrap.TextWrapper(width=250)
    # LOG_WRAPPER = textwrap.TextWrapper(width=150)
    AUTO_SAVE_BRANCH = f'auto-save-{datetime.now().strftime("%Y-%m-%d")}'
    MAIN_WORKING_BRANCH = 'master'

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
        tl.log_yellow(f'Elapsed (deploy and test execution): {self.get_duration(duration)}')

        tl.save_logs()

    def service_deployment(self):
        if not DEPLOY: return
        duration = time.time()
        tl.print_header('SERVICE DEPLOYMENT')
        if FULL:
            self.execute_and_log('sls deploy', 'Deploy full service...')
        else:
            for function_name in FUNCTIONS_TO_DEPLOY:
                self.execute_and_log(f'sls deploy function --function {function_name}',
                                     f"Deploy function: '{function_name}'")
        tl.log_yellow(f'Elapsed: {self.get_duration(duration)}')

    def git_procedures(self):
        if not UPDATE_REPOSITORY: return
        duration = time.time()
        tl.print_header('UPDATE REPOSITORY')
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
        tl.log_yellow(f'Elapsed: {self.get_duration(duration)}')

    def test_functions(self):
        if not TEST_FUNCTIONS: return
        total_duration = time.time()
        tl.print_header('TESTING PROCEDURES')
        for test in FUNCTIONS_TO_TEST:
            duration = time.time()
            name = test[0]
            params = test[1]
            expected = test[2]
            command = f'sls invoke -f {name} -l'
            if params.strip(): command += f' --path {params.strip()}'
            logs = self.execute_and_log(command, f'Testing "{name}" @ params "{params}". '
                                                 f'Expect: "{expected}"...', PRINT_LOGS_ON_SCREEN)
            status, logs = Tests.test(name, logs, expected)
            # for log in logs:
            #     wrap_list = self.WRAPPER.wrap(text=log)
            #     for line in wrap_list:
            #         tl.log(line)
            for log in logs:
                    tl.log(log)
            tl.log_yellow(f"Elapsed ('{name}'): {self.get_duration(duration)}")
        tl.log_yellow(f'Elapsed (all tests): {self.get_duration(total_duration)}')

    def execute_and_log(self, execute, log, log_details = True):
        tl.log_yellow(f"{datetime.utcnow().strftime('%H:%M:%S')}:UTC - {log} ({execute})")
        logs = []
        p = subprocess.Popen(execute, bufsize=1, stdin=open(os.devnull), shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        for i, std in enumerate([p.stdout, p.stderr]):
            for line in iter(std.readline, b''):
                log = line.decode("utf-8").replace('\n', '')
                logs.append(log)
                # wrap_list = self.WRAPPER.wrap(text=log)
                # for wrap_line in wrap_list:
                #     if i == 0:
                #         tl.log(wrap_line, log_details)
                #     else:
                #         tl.log(f"{tl.ANSI_COLORS.get('red')}{wrap_line}{tl.ANSI_COLORS.get('default')}",
                #                  log_details)
                if i == 0:
                    tl.log(log, log_details)
                else:
                    tl.log_red(log, log_details)
        p.stdout.close()
        p.wait()
        return logs

    @staticmethod
    def get_duration(start):
        return str(round(time.time() - start, 3)) + 's'


if __name__ == "__main__":
    dt = DeployAndTest()