from datetime import datetime
import json
import numbers


class Helpers:

    @classmethod
    def get_request_time_id(cls):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") \
        .replace(' ', '-').replace(':', '-').replace('.', '-')

    @classmethod
    def get_return_object(cls, endpoint, status_code, op_status, response_code, message, img_meta_data,
                          api_metrics, request_id='N.A.', img_url='N.A.', payload=[]):
        # Montagem do objeto de retorno
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        }

        body = {
            "endpoint": endpoint,
            "op_status": op_status,
            "response_code": response_code,
            "message": message,
            "img_meta_data": img_meta_data,
            "api_metrics": api_metrics,
            "request_id": request_id,
            "img_url": img_url,
            "payload": payload
        }

        return_object = {
            "statusCode": status_code,
            "headers": headers,
            "body": json.dumps(body)
        }

        print('RETURN - Return object: ' + str(return_object))

        return return_object

    @classmethod
    def sizeof_fmt(cls, num, suffix='B'):
        # Formatação de bytes por ordem de grandeza
        for unit in ['', ' K', ' M', ' G', ' T', ' P', ' E', ' Z']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

    @classmethod
    def convert_structure_to_dynamo_compatible(cls, data):
        # Método recursivo para converter floats em strings em um objeto de estrutura desconhecida
        if isinstance(data, dict):
            for k, v in data.items():
                data[k] = cls.convert_structure_to_dynamo_compatible(v)

        elif isinstance(data, list):
            for x in range(len(data)):
                data[x] = cls.convert_structure_to_dynamo_compatible(data[x])

        elif isinstance(data, tuple):
            data = list(data)
            data = cls.convert_structure_to_dynamo_compatible(data)

        if isinstance(data, float):
            return str(data)

        else:
            return data

    @classmethod
    def convert_structure_content_to_strings(cls, data):
        # Método recursivo para converter floats em strings em um objeto de estrutura desconhecida
        if isinstance(data, dict):
            for k, v in data.items():
                data[k] = cls.convert_structure_content_to_strings(v)

        elif isinstance(data, list):
            for x in range(len(data)):
                data[x] = cls.convert_structure_content_to_strings(data[x])

        elif isinstance(data, tuple):
            data = list(data)
            data = cls.convert_structure_content_to_strings(data)

        elif isinstance(data, int):
            return data

        else:
            return str(data)

        return data

    @classmethod
    def convert_decimals_to_strings(cls, data):
        # Método recursivo para converter decimals em strings em um objeto de estrutura desconhecida
        if isinstance(data, dict):
            for k, v in data.items():
                data[k] = cls.convert_decimals_to_strings(v)

        elif isinstance(data, list):
            for x in range(len(data)):
                data[x] = cls.convert_decimals_to_strings(data[x])

        if isinstance(data, numbers.Number):
            return str(data)
        else:
            return data





