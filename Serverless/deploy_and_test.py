import os, subprocess
from datetime import datetime
from tests.test_procedure import TestProcedure
from tests.test_logger import TestLogger as tl

DEPLOY = True
FULL = True
FUNCTIONS_TO_DEPLOY = [
    # 'add-picture',
    # 'celeb-recognition',
    # 'generate-thumbnail',
    'web-scraper'
]

UPDATE_REPOSITORY = True
MAIN_BRANCH = True
GIT_COMMIT_MESSAGE = 'Web scraping proxy finder started.'

TEST_FUNCTIONS = True
PRINT_LOGS_ON_SCREEN = True
TESTS_TO_PERFORM = [
    'add-picture-integration',
    # 'web-scraper'
]


class DeployAndTest:

    AUTO_SAVE_BRANCH = f'auto-save-{datetime.now().strftime("%Y-%m-%d")}'
    MAIN_WORKING_BRANCH = 'master'

    SLS_DEPLOY = 'sls deploy'
    SLS_DEPLOY_FUNCTION = 'sls deploy function --function {}'
    GIT_BRANCH = 'git branch'
    GIT_BRANCH_DELETE = 'git branch -D {}'
    GIT_ADD_ALL = 'git add .'
    GIT_COMMIT = 'git commit -m {}'
    GIT_PUSH = 'git push origin {}'
    GIT_CHECKOUT_NEW_BRANCH = 'git checkout -b {}'
    GIT_CHECKOUT = 'git checkout {}'

    @tl.timeit('deploy and test execution')
    def __init__(self):

        # Deploy service
        if DEPLOY: self.service_deployment()

        # Git procedures
        if UPDATE_REPOSITORY: self.git_procedures()

        # Testing procedures
        if TEST_FUNCTIONS: self.test_functions()

    @tl.timeit(None)
    def service_deployment(self):
        tl.print_header('SERVICE DEPLOYMENT')
        if FULL:
            self.execute(self.SLS_DEPLOY, 'Deploy full service...')
        else:
            for function_name in FUNCTIONS_TO_DEPLOY:
                self.execute(self.SLS_DEPLOY_FUNCTION.format(function_name), f"Deploy function: '{function_name}'")

    @tl.timeit(None)
    def git_procedures(self):
        tl.print_header('UPDATE REPOSITORY')
        self.execute(self.GIT_BRANCH, 'Present current GIT branches...')
        self.execute(self.GIT_ADD_ALL, 'Execute GIT add all...')
        self.execute(self.GIT_COMMIT.format(f'"{GIT_COMMIT_MESSAGE}"'), f"Committing with message: '{GIT_COMMIT_MESSAGE}'...")

        if MAIN_BRANCH:
            self.execute(self.GIT_PUSH.format(self.MAIN_WORKING_BRANCH),
                         f"GIT pushing to '{self.MAIN_WORKING_BRANCH}' branch...")
        else:
            self.execute(self.GIT_CHECKOUT_NEW_BRANCH.format(self.AUTO_SAVE_BRANCH),
                                 f'Creating local auto-backup branch "{self.AUTO_SAVE_BRANCH}"...')
            self.execute(self.GIT_PUSH.format(self.AUTO_SAVE_BRANCH),
                                 f"Pushing to remote auto-backup branch...")
            self.execute(self.GIT_CHECKOUT.format(self.MAIN_WORKING_BRANCH),
                                 f"Switching back to local main branch '{self.MAIN_WORKING_BRANCH}'...")
            self.execute(self.GIT_BRANCH_DELETE.format(self.AUTO_SAVE_BRANCH),
                                 f"Deleting local auto-backup branch...")

    @tl.timeit('all tests')
    def test_functions(self):
        tl.print_header('TESTING PROCEDURES')
        TestProcedure(TESTS_TO_PERFORM, PRINT_LOGS_ON_SCREEN)

    @staticmethod
    def execute(execute, log, log_details = True):
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
    tl.save_logs()

