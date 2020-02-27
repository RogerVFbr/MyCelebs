import os, subprocess, time
from datetime import datetime
from tests.test_procedure import TestProcedure
from tests.test_logger import TestLogger as tl

DEPLOY = True
FULL = False
FUNCTIONS_TO_DEPLOY = [
    # 'add-picture',
    # 'celeb-recognition',
    'generate-thumbnail'
]

UPDATE_REPOSITORY = True
MAIN_BRANCH = True
GIT_COMMIT_MESSAGE = 'Timing decorators.'

TEST_FUNCTIONS = True
PRINT_LOGS_ON_SCREEN = False
TESTS_TO_PERFORM = [
    'add-picture-integration'
]


class DeployAndTest:

    AUTO_SAVE_BRANCH = f'auto-save-{datetime.now().strftime("%Y-%m-%d")}'
    MAIN_WORKING_BRANCH = 'master'

    @tl.timeit('deploy and test execution')
    def __init__(self):

        # Deploy service
        self.service_deployment()

        # Git procedures
        self.git_procedures()

        # Testing procedures
        self.test_functions()

        # Save generated logs
        tl.save_logs()

    @tl.timeit(None)
    def service_deployment(self):
        if not DEPLOY: return
        tl.print_header('SERVICE DEPLOYMENT')
        if FULL:
            self.execute_and_log('sls deploy', 'Deploy full service...')
        else:
            for function_name in FUNCTIONS_TO_DEPLOY:
                self.execute_and_log(f'sls deploy function --function {function_name}',
                                     f"Deploy function: '{function_name}'")

    @tl.timeit(None)
    def git_procedures(self):
        if not UPDATE_REPOSITORY: return
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

    @tl.timeit('all tests')
    def test_functions(self):
        if not TEST_FUNCTIONS: return
        tl.print_header('TESTING PROCEDURES')
        TestProcedure(TESTS_TO_PERFORM, PRINT_LOGS_ON_SCREEN)

    @staticmethod
    def execute_and_log(execute, log, log_details = True):
        tl.log_alert(f"{log} ({execute})")
        p = subprocess.Popen(execute, bufsize=1, stdin=open(os.devnull), shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        for i, std in enumerate([p.stdout, p.stderr]):
            for line in iter(std.readline, b''):
                log = line.decode("utf-8").replace('\n', '')
                if i == 0: tl.log(log, log_details)
                else: tl.log_error(log, log_details)
        p.stdout.close()
        p.wait()


if __name__ == "__main__":
    dt = DeployAndTest()
