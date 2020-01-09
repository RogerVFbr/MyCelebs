import os, time, boto3
from lib.Helpers.Helpers import Helpers as hl
from lib.Validation.ValidationManager import ValidationManager as vm
from lib.Resources.Resources_strings_en import Strings as rsc
from lib.Resources.EnvironmentVariables import EnvironmentVariables as ev


class Validation:

    def __init__(self):
        self.validation_status = False
        self.id = ''
        self.img_meta_data = {}
        self.img_bytes = ''
        self.reason = 'N.A.'
        self.detect_faces_response = {}
        self.identity = {}
        self.identity['coordinates'] = {
            'source': 'N.A.',
            'lat': 'N.A.',
            'lng': 'N.A.'
        }
        self.identity['device'] = 'N.A.'
        self.failed_return_object = {}
        self.image = None
        self.api_metrics = {
            'validation_time_json': 'N.A.',
            'validation_time_char': 'N.A.',
            'business_logic_time': 'N.A.'
        }


    def validate_request_object(self, endpoint_name, body, request_fields, request_context, id_must_be_unique,
                                check_image=True):

        # Validacao de existência dos campos do JSON enviado
        validation_time_json = time.time()
        if not vm.validate_input_fields(body, request_fields):
            self.api_metrics['validation_time_json'] = round(time.time() - validation_time_json, 3)
            self.failed_return_object = hl.get_return_object(
                endpoint=endpoint_name,
                status_code=400,
                op_status=rsc.OP_STATUS_FAILED,
                response_code=0,
                message=rsc.ERROR_MSG_JSON_STRUCTURE_INVALID,
                img_meta_data=self.img_meta_data,
                api_metrics=self.api_metrics
            )
            print(rsc.VALIDATION_MSG_REQUEST_INPUT_FIELDS_FAILED)
            return

        # Extrair e organizar as informações recebidas
        self.__extract_info_from_body(request_context, body)

        # Validacao de Id unico
        if id_must_be_unique != vm.validate_unique_id(self.id):
            self.api_metrics['validation_time_json'] = round(time.time() - validation_time_json, 3)
            message = rsc.ERROR_MSG_TAKEN_ID.format(self.id.replace(ev.BASE_NAME+'-', '')) \
                if id_must_be_unique else rsc.ERROR_MSG_UNKNOWN_ID.format(self.id.replace(ev.BASE_NAME+'-', ''))
            self.failed_return_object = hl.get_return_object(
                endpoint=endpoint_name,
                status_code=400,
                op_status=rsc.OP_STATUS_FAILED,
                response_code=0,
                message=message,
                img_meta_data=self.img_meta_data,
                api_metrics=self.api_metrics
            )
            print(rsc.VALIDATION_MSG_ID_UNIQUENESS_FAILED)
            return

        # Caso somente checagem de campos seja necessaria, interromper e retornar sucesso
        if not check_image:
            self.validation_status = True
            self.api_metrics['validation_time_json'] = round(time.time() - validation_time_json, 3)
            print(rsc.VALIDATION_MSG_SUCCESS)
            return

        # Validacao preliminar de integridade do BASE64
        integrity_status, self.img_meta_data, self.img_bytes, integrity_msg = vm.validate_base64_integrity(self.image)
        if not integrity_status:
            self.api_metrics['validation_time_json'] = round(time.time() - validation_time_json, 3)
            self.failed_return_object = hl.get_return_object(
                endpoint=endpoint_name,
                status_code=400,
                op_status=rsc.OP_STATUS_FAILED,
                response_code=0,
                message=integrity_msg,
                img_meta_data=self.img_meta_data,
                api_metrics=self.api_metrics
            )
            print(rsc.VALIDATION_MSG_BASE64_INTEGRITY_FAILED)
            return

        self.__complement_missing_info_using_exif(self.img_meta_data['exif'])
        self.api_metrics['validation_time_json'] = round(time.time() - validation_time_json, 3)
        validation_time_char = time.time()

        # Validacao das caracteristicas da imagem enviada
        characteristics_status, self.detect_faces_response, characteristics_msg = vm.validate_photo_characteristics(self.img_bytes)
        if not characteristics_status:
            self.api_metrics['validation_time_char'] = round(time.time() - validation_time_char, 3)
            self.failed_return_object = hl.get_return_object(
                endpoint=endpoint_name,
                status_code=400,
                op_status=rsc.OP_STATUS_FAILED,
                response_code=0,
                message=characteristics_msg,
                img_meta_data=self.img_meta_data,
                api_metrics=self.api_metrics
            )
            print(rsc.VALIDATION_MSG_IMAGE_CHARATERISTICS_FAILED)
            return

        self.api_metrics['validation_time_char'] = round(time.time() - validation_time_char, 3)
        self.validation_status = True
        print(rsc.VALIDATION_MSG_SUCCESS)
        return

    def __extract_info_from_body(self, request_context, body):

        if 'identity' in request_context:
            request_identity_full = request_context['identity']
            if 'sourceIp' in request_identity_full:
                self.identity['sourceIp'] = request_identity_full['sourceIp']
            if 'userAgent' in request_identity_full:
                self.identity['userAgent'] = request_identity_full['userAgent']
            if 'apiKeyId' in request_identity_full:
                self.identity['apiKeyProfileName'] = boto3.client('apigateway').get_api_key(
                    apiKey=request_identity_full['apiKeyId'],
                    includeValue=False)['name']
            request_context.pop('identity', None)

        if 'coordinates' in body and isinstance(body['coordinates'], dict):
            lat_availability = 'lat' in body['coordinates'] and body['coordinates']['lat'] != ''
            lng_availability = 'lng' in body['coordinates'] and body['coordinates']['lng'] != ''
            if lat_availability and lng_availability:
                self.identity['coordinates']['lat'] = body['coordinates']['lat']
                self.identity['coordinates']['lng'] = body['coordinates']['lng']
                self.identity['coordinates']['source'] = 'device'

        if 'device' in body and body['device'] != '':
            self.identity['device'] = body['device']

        if 'image' in body:
            self.image = body['image']

        if 'reason' in body and body['reason'] != '':
            self.reason = body['reason']

        env_variables = dict(os.environ.items())
        if 'BASE_NAME' in env_variables:
            self.id = dict(os.environ.items())['BASE_NAME'] + '-' + body['id']
        else:
            self.id = 'NO-BASE-NAME-' + body['id']

    def __complement_missing_info_using_exif(self, exif):

        if not isinstance(exif, dict): return

        # if self.identity['device'] == 'N.A.':
        device = None
        if 'Make' in exif and exif['Make'] != '' and exif['Make'] != 'None': device = exif['Make']
        if 'Model' in exif and exif['Model'] != '' and exif['Model'] != 'None': device += ' ' + exif['Model']
        if device: self.identity['device'] += f' | (Exif) {device}'

        if self.identity['coordinates']['lat'] == 'N.A.' or self.identity['coordinates']['lat'] == 'N.A.':
            if 'GPSInfo' in exif and isinstance(exif['GPSInfo'], dict) and 'lat' in exif['GPSInfo'] and 'lng' in exif['GPSInfo']:
                try:
                    _ = float(exif['GPSInfo']['lat'])
                    _ = float(exif['GPSInfo']['lng'])
                    self.identity['coordinates'] = exif['GPSInfo']
                    self.identity['coordinates']['source'] = 'exif'
                except Exception as e:
                    print(f"VL - Unable to acquire coordinates from exif GPSInfo: '{str(exif['GPSInfo'])}'. Error: {str(e)}")
