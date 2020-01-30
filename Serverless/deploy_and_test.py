import os
import json


def main():
    with open('deploy_and_test_config.json') as json_file:
        config = json.load(json_file)
        print(f'Parsing configurations: {config}')

    # Prepare execution
    project_path = config['project_paths']['home']
    os.chdir(project_path)
    header_size = 60

    # Serverless procedures
    print_header('SERVERLESS PROCEDURES', header_size)

    # Deploy full service
    # execute_and_log('sls deploy', 'Deploy full service...')

    # Deploy single functions
    function_name = 'add-picture'
    execute_and_log(f'sls deploy function --function {function_name}', f"Deploy single function: '{function_name}'")

    # Git procedures
    print_header('GIT PROCEDURES', header_size)
    commit_msg = 'Standard commit'
    execute_and_log('git status', 'Present GIT status...')
    execute_and_log('git add .', 'Execute GIT add all...')
    execute_and_log(f'git commit -m "{commit_msg}"', f"Commiting with message: {commit_msg}...")




    # print('')
    # print('+-------------------------------------------+')
    # print('|               REGISTER LOGS               |')
    # print('+-------------------------------------------+')
    # print('')
    # os.system('sls logs -f register')

def execute_and_log(execute, log):
    print(f'\u001b[33m{log}\x1b[0m')
    os.system(execute)

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
    main()