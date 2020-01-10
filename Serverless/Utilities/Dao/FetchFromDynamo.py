from boto3.dynamodb.conditions import Key, Attr
from boto3 import resource
from Resources.EnvironmentVariables import EnvironmentVariables as ev


class FetchFromDynamo:

    @classmethod
    def fetch_data(cls, table_name, request_data):
        dynamoDB = resource('dynamodb')
        table = dynamoDB.Table(table_name)

        hash_filter = None
        range_filter = None
        range_filter_string = ''

        filter_options = [request_data.get('year'), request_data.get('month'), request_data.get('day'),
                          request_data.get('hour'), request_data.get('minute'), request_data.get('second')]

        for i, filter_opt in enumerate(filter_options, 1):
            if filter_opt is None or filter_opt == 'all' or filter_opt == '': break
            filter_opt = str(filter_opt)
            if len(filter_opt) is 1: filter_opt = '0' + filter_opt
            range_filter_string += filter_opt
            if i is not len(filter_options): range_filter_string += '-'

        if 'userId' in request_data and request_data['userId'] != '':
            hash_filter = Key('userId').eq(ev.BASE_NAME + '-' + request_data['userId'])

        if range_filter_string is not '':
            range_filter = Key('time').begins_with(range_filter_string)

        print(f'FETCH_FROM_DYNAMO - Request data content: {str(request_data)}')
        print(f'FETCH_FROM_DYNAMO - Hash filter: {str(hash_filter)}')
        print(f'FETCH_FROM_DYNAMO - Range filter: {str(range_filter)}')
        print(f'FETCH_FROM_DYNAMO - Range filter string: {str(range_filter_string)}')

        if hash_filter is None and range_filter is None:
            response = table.scan()
        elif hash_filter is not None and range_filter is None:
            response = table.scan(FilterExpression=hash_filter)
            # response = table.query(KeyConditionExpression=hash_filter)
        elif hash_filter is None and range_filter is not None:
            response = table.scan(FilterExpression=range_filter)
        elif hash_filter is not None and range_filter is not None:
            response = table.scan(FilterExpression=hash_filter & range_filter)

        items = response['Items']

        while True:
            if response.get('LastEvaluatedKey'):
                if hash_filter is None and range_filter is None:
                    response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                elif hash_filter is not None and range_filter is None:
                    response = table.scan(FilterExpression=hash_filter, ExclusiveStartKey=response['LastEvaluatedKey'])
                elif hash_filter is None and range_filter is not None:
                    response = table.scan(FilterExpression=range_filter, ExclusiveStartKey=response['LastEvaluatedKey'])
                elif hash_filter is not None and range_filter is not None:
                    response = table.scan(FilterExpression=hash_filter & range_filter,
                                          ExclusiveStartKey=response['LastEvaluatedKey'])

                items += response['Items']
            else:
                break

        return sorted(items, key=lambda k: k['time'], reverse=True)