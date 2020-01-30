import os, json, subprocess

FULL_DEPLOY = False
FUNCTIONS_TO_DEPLOY = ['add-picture']

UPDATE_REPOSITORY = True
GIT_COMMIT_MESSAGE = 'Current updates'

TEST_FUNCTIONS = True
FUNCTIONS_TO_TEST = [
    ('add-picture', 'tests/mock_add_picture_a.json'),
    # ('add-picture', 'tests/mock_add_picture_b.json')
]




class DeployAndTest:

    project_path = None
    function_parameters = None
    header_size = 60
    CONFIG_FILE_PATH = 'tests/config.json'
    FUNCTION_PARAMETERS_PATH = 'tests/function_parameters.json'

    def __init__(self):

        # Read config JSON
        with open(self.CONFIG_FILE_PATH) as json_file:
            self.project_path = json.load(json_file)['project_paths']['home']

        # Prepare execution

        # Deploy service
        self.print_header('SERVICE DEPLOYMENT', self.header_size)
        if FULL_DEPLOY:
            self.execute_and_log('sls deploy', 'Deploy full service...')
        else:
            for function_name in FUNCTIONS_TO_DEPLOY:
                self.execute_and_log(f'sls deploy function --function {function_name}',
                                     f"Deploy single function: '{function_name}'")

        # Git procedures
        if UPDATE_REPOSITORY:
            self.print_header('UPDATE REPOSITORY', self.header_size)
            self.execute_and_log('git status', 'Present GIT status...')
            self.execute_and_log('git add .', 'Execute GIT add all...')
            self.execute_and_log(f'git commit -m "{GIT_COMMIT_MESSAGE}"',
                                 f"Commiting with message: {GIT_COMMIT_MESSAGE}...")
            self.execute_and_log(f'git push origin master', f"Executing GIT push to master branch...")

        # Testing procedures
        if TEST_FUNCTIONS:
            self.print_header('TESTING PROCEDURES', self.header_size)
            for test in FUNCTIONS_TO_TEST:
                name = test[0]
                params = ''
                try:
                    params = test[1]
                except:
                    pass
                command = f'sls invoke -f {name} -l'
                if params.split(): command += f' --path {params.split()}'
                self.execute_and_log(command, f'Testing "{name}" function with parameters "{params}"...')

    def execute_and_log(self, execute, log):
        print(f'\u001b[33m{log}\x1b[0m')
        p = subprocess.Popen(execute, bufsize=1, stdin=open(os.devnull), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in iter(p.stdout.readline, b''):
            print(line.decode("utf-8").replace('\n', ''))
        for line in iter(p.stderr.readline, b''):
            print(line.decode("utf-8").replace('\n', ''))
            pass
        p.stdout.close()
        p.wait()

    @staticmethod
    def print_header(content, size):
        """
        Prints main header on log screen.
        :param content (string): Text to be displayed on main header.
        :param size (int): Horizontal size of the header in number of characters.
        :return: None
        """
        color, default = '\u001b[35m', '\u001b[0m'
        print('')
        main = '{' + "".join([' ' for x in range(int(size/2)-int((len(content)/2)))]) + content
        main += "".join([' ' for x in range(size-len(main))]) + '}'
        upper_line = ' /' + "".join(['=' for x in range(len(main)-4)]) + '\\'
        lower_line = ' \\' + "".join(['=' for x in range(len(main)-4)]) + '/'
        print(f'{color}{upper_line}\n{main}\n{lower_line}{default}')
        print('')


if __name__ == "__main__":
    dt = DeployAndTest()