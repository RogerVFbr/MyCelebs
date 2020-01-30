import os
import json
import subprocess
import sys


class DeployAndTest:

    project_path = None

    def __init__(self):
        # Read config JSON
        with open('deploy_and_test_config.json') as json_file:
            config = json.load(json_file)
            print(f'Parsing configurations: {config}')

        # Prepare execution
        self.project_path = config['project_paths']['home']
        # os.chdir(project_path)
        os.path.dirname(os.path.realpath(__file__))
        header_size = 60

        # Deploy service
        self.print_header('SERVICE DEPLOYMENT', header_size)
        # execute_and_log('sls deploy', 'Deploy full service...')
        function_name = 'add-picture'
        self.execute_and_log(f'sls deploy function --function {function_name}', f"Deploy single function: '{function_name}'")

        # Git procedures
        self.print_header('UPDATE REPOSITORY', header_size)
        commit_msg = 'Standard commit'
        self.execute_and_log('git status', 'Present GIT status...')
        self.execute_and_log('git add .', 'Execute GIT add all...')
        self.execute_and_log(f'git commit -m "{commit_msg}"', f"Commiting with message: {commit_msg}...")
        self.execute_and_log(f'git push origin master', f"Executing GIT push to master branch...")

        # Testing procedures
        # execute_and_log('sls invoke -f add-picture -l', 'Testing add-picture function...')




        # print('')
        # print('+-------------------------------------------+')
        # print('|               REGISTER LOGS               |')
        # print('+-------------------------------------------+')
        # print('')
        # os.system('sls logs -f register')

    def execute_and_log(self, execute, log):
        print(f'\u001b[33m{log}\x1b[0m')
        # os.system(execute)
        p = subprocess.Popen(execute, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # while True:
        #     output = p.stdout.readline()
        #     if output == '' and p.poll() is not None:
        #         break
        #     if output:
        #         print(output.strip())
        # rc = p.poll()
        # print(rc)
        # print(p.communicate()[0].decode("utf-8"))
        # print(p.communicate()[1].decode("utf-8"))
        # print(p.communicate())
        # while p.poll() is None:
        #     out = p.stdout.read(1)
        #     sys.stdout.write(out.decode("utf-8"))
        #     sys.stdout.flush()
        # p.stdout.close()
        # p.wait()
        for line in iter(p.stdout.readline, b''):
            print(line.decode("utf-8"))
        p.stdout.close()
        p.wait()
        # p.stdout.read()
        # print(p.stdout.read())

        # p = subprocess.run(execute, shell=True, capture_output=True)
        # print(type(p.stdout))


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