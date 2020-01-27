import boto3


class AWSDynamoDB:

    def __init__(self, table_name: str):
        self.table_name = table_name
        self.key_hash = None
        self.key_range = None
        self.table_status = False

    def evaluate_conditions_and_requirements(self):

        try:
            description = boto3.client('dynamodb').describe_table(TableName=self.table_name)
        except Exception as e:
            raise Exception(str(e))

        http_status_code = description.get('ResponseMetadata', {}).get('HTTPStatusCode')
        if not http_status_code or http_status_code != 200:
            raise Exception(f'Bad status code: {http_status_code}')

        self.table_status = description.get('Table', {}).get('TableStatus')
        if not self.table_status or self.table_status != 'ACTIVE':
            raise Exception(f'Bad table status: {self.table_status}')

        key_schema = description.get('Table', {}).get('KeySchema', {})

        if key_schema and isinstance(key_schema, list):
            self.key_hash = next((x for x in key_schema if x.get('KeyType', '') == 'HASH'), {}).get('AttributeName')
            self.key_range = next((x for x in key_schema if x.get('KeyType', '') == 'RANGE'), {}).get('AttributeName')

        return str({
            'http_status_code': http_status_code,
            'table_status': self.table_status,
            'key_hash': self.key_hash,
            'key_range': self.key_range
        })

    def save(self,  data):

        type(self).__convert_structure_to_dynamo_compatible(data)

        try:
            table = boto3.resource('dynamodb').Table(self.table_name)
            response = table.put_item(Item=data)
        except Exception as e:
            raise Exception(str(e))

        http_status_code = response.get('ResponseMetadata', {}).get('HTTPStatusCode')
        if not http_status_code or http_status_code != 200:
            raise Exception(f'Bad status code: {http_status_code}')

    @classmethod
    def __convert_structure_to_dynamo_compatible(cls, data):
        if isinstance(data, dict):
            for k, v in data.items():
                data[k] = cls.__convert_structure_to_dynamo_compatible(v)

        elif isinstance(data, list):
            for x in range(len(data)):
                data[x] = cls.__convert_structure_to_dynamo_compatible(data[x])

        elif isinstance(data, tuple):
            data = list(data)
            data = cls.__convert_structure_to_dynamo_compatible(data)

        if isinstance(data, float):
            return str(data)

        else:
            return data








