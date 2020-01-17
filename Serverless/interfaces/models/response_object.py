import json


class ResponseObject:

    def __init__(self,
                 status_code: int = 200,
                 response_code: int = 0,
                 msg_dev: str = 'N.A.',
                 msg_user: str = 'N.A.',
                 img_meta_data: dict = {},
                 api_metrics: dict = {}
    ):
        self.statusCode = status_code

        self.headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        }

        self.body = json.dumps({
            'response_code': response_code,
            'msg_dev': msg_dev,
            'msg_user': msg_user,
            'img_meta_data': img_meta_data,
            'api_metrics': api_metrics
        })

        print('RETURN - Return object: ' + str(self.__dict__))

