import os

# C:\Users\Xqube notebook 1\Desktop\ROGER FRERET\Serverless

xqube = {
    'SERVERLESS_PATH' : 'C:\\Users\\Xqube notebook 1\\Desktop\\ROGER FRERET\\Serverless\\FacialRecognitionAuth',
    'TESTS_PATH': 'C:\\Users\\Xqube notebook 1\\Desktop\\ROGER FRERET\\Serverless\\EndPointTester',
    'python_exec': 'python main.py'
}

home = {
    'SERVERLESS_PATH' : '/Users/rogerfreret/Desktop/FELLOW/FellowAuth/CognifyServerless',
    'TESTS_PATH': '/Users/rogerfreret/Desktop/FELLOW/FellowAuth/EndPointTester',
    'python_exec': 'python3 main.py'
}


config = home


# Deploy full service
os.chdir(config['SERVERLESS_PATH'])
os.system('sls deploy')
# os.system('sls deploy function --function admin')
# os.system('sls deploy function --function register')

# Run automated tests
os.chdir(config['TESTS_PATH'])
# os.system(config['python_exec'])

# Show Lambda logs
os.chdir(config['SERVERLESS_PATH'])
# print('')
# print('+-------------------------------------------+')
# print('|               REGISTER LOGS               |')
# print('+-------------------------------------------+')
# print('')
# os.system('sls logs -f register')

# print('')
# print('+-------------------------------------------+')
# print('|                RECKON LOGS                |')
# print('+-------------------------------------------+')
# print('')
# os.system('sls logs -f Reckon')
#
# print('')
# print('+-------------------------------------------+')
# print('|                DELETE LOGS                |')
# print('+-------------------------------------------+')
# print('')
# os.system('sls logs -f Delete')






# Create a serverless project for Node.js within AWS Lambda
# sls create --template aws-nodejs

# Create AWS credentials file in ~/.aws
# sls config credentials --provider aws --key <access-key-id> --secret <secret> --profile <profilename>

# Deploy functions from serverless.yml to AWS Lambda
# sls deploy

# Deploy single function
# serverless deploy function --function <myFunction>

# Invoke function and return log
# sls invoke -f <function-name-in-serverless.yml> -l

# Stream function logs in real time
# sls logs -f <function-name-in-serverless.yml> -t

# Show logs of a function
# serverless logs -f <function-name-in-serverless.yml>

# Tail logs of a function
# serverless logs -f <function-name-in-serverless.yml> --tail
