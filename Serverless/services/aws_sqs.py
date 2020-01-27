import json

import boto3


class AWSSQS:

    def __init__(self, queue_url: str):
        self.queue_url = queue_url
        self.client = boto3.client('sqs')

    def evaluate_conditions_and_requirements(self):
        return 'N.A.'

    def save(self,  data):

        try:
            response = self.client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(data)
            )
        except Exception as e:
            raise Exception(str(e))

        http_status_code = response.get('ResponseMetadata', {}).get('HTTPStatusCode')
        if not http_status_code or http_status_code != 200:
            raise Exception(f'Bad status code: {http_status_code}')

    def delete(self, receipt_handle: str):

        try:
            response = self.client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )

        except Exception as e:
            raise Exception(str(e))

        http_status_code = response.get('ResponseMetadata', {}).get('HTTPStatusCode')
        if not http_status_code or http_status_code != 200:
            raise Exception(f'Bad status code: {http_status_code}')









