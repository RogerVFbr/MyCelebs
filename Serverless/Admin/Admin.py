import simplejson as json

from Admin.GetCollections import GetCollections
from Admin.GetCollectionById import GetCollectionById
from Admin.GetFailedReckonLogs import GetFailedReckonLogs
from Admin.GetReckonLogs import GetReckonLogs
from Admin.GetRegistrationLogs import GetRegistrationLogs


def admin(event, context):

    print('.')
    print('+------------------------------------------+')
    print('| . . . . . . . . . ADMIN . . . . . . . . .|')
    print('+------------------------------------------+')

    # Extração do payload enviado e de informações de contexto da requisição.
    body = json.loads(event["body"])
    print('ADMIN - Request body: ' + str(body))

    if 'command' not in body or 'table' not in body:
        return {
            "statusCode": 400,
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            "body": json.dumps({
               'message': 'Unable to process request.'
            })
        }

    response = {}

    if body['command'] == 'get' and body['table'] == 'reckon':
        response['payload'] = GetReckonLogs.get(body)

    elif body['command'] == 'get' and body['table'] == 'reckon-fail':
        response['payload'] = GetFailedReckonLogs.get(body)

    elif body['command'] == 'get' and body['table'] == 'register':
        response['payload'] = GetRegistrationLogs.get(body)

    elif body['command'] == 'collections':
        response['payload'] = GetCollections.get(body)

    elif body['command'] == 'collectionById':
        response['payload'] = GetCollectionById.get(body)

    return {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(response)
    }