import os
import json
import subprocess


class DeployAndTest:

    project_path = None

    def __init__(self):
        # Read config JSON
        with open('tests/config.json') as json_file:
            config = json.load(json_file)
            print(f'Parsing configurations: {config}')
            self.project_path = config['project_paths']['home']

        # Prepare execution
        # os.path.dirname(os.path.realpath(__file__))
        header_size = 60

        # Deploy service
        self.print_header('SERVICE DEPLOYMENT', header_size)
        # execute_and_log('sls deploy', 'Deploy full service...')
        function_name = 'add-picture'
        self.execute_and_log(f'sls deploy function --function '
                             f'{function_name}', f"Deploy single function: '{function_name}'")

        # Git procedures
        self.print_header('UPDATE REPOSITORY', header_size)
        commit_msg = 'Standard commit'
        self.execute_and_log('git status', 'Present GIT status...')
        self.execute_and_log('git add .', 'Execute GIT add all...')
        self.execute_and_log(f'git commit -m "{commit_msg}"', f"Commiting with message: {commit_msg}...")
        self.execute_and_log(f'git push origin master', f"Executing GIT push to master branch...")

        # Testing procedures
        self.print_header('TESTING PROCEDURES', header_size)
        self.execute_and_log('sls invoke -f add-picture -l --path tests/mock_add_picture_a.json',
                             'Testing add-picture function...')

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