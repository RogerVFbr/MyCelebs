import json, time, os
from datetime import datetime
from lib.Helpers.Helpers import Helpers as hl
from lib.Resources.Resources_strings_en import Strings as str
from lib.Resources.Resources_config import Config as cnf
from Reckon.ReckonManager import ReckonManager as rm
from lib.Validation.Validation import Validation
from lib.Dao.Dao import Dao as dao


def reckon_one_to_n(event, context):

    print('.')
    print('+------------------------------------------+')
    print('|. . . . . . . . RECKON 1toN . . . . . . . |')
    print('+------------------------------------------+')

    # Extração do payload enviado e de informações de contexto da requisição.
    body = json.loads(event["body"])
    request_context = event['requestContext']

    # Inicialização do procedimento de validação do payload
    vl = Validation()
    vl.validate_request_object(
        endpoint_name=str.ENDPOINT_NAME_RECKON,
        body=body,
        request_fields=cnf.EXPECTED_REQUEST_FIELDS,
        request_context=request_context,
        id_must_be_unique=False,
    )
    if not vl.validation_status:
        return vl.failed_return_object

    # Checkagem de match entre imagem e ID
    time_business_logic = time.time()

    identity_msg = ''
    # identity_status, identity_msg, search_faces_by_image_response = rm.identity_check(vl.img_bytes, vl.id)
    # if not identity_status:
    #     vl.api_metrics['business_logic_time'] = round(time.time() - time_business_logic, 3)
    #     dao.log(
    #         id=vl.id,
    #         endpoint='failed-' + str.ENDPOINT_NAME_RECKON,
    #         table_name=dict(os.environ.items())['FAILED_RECKON_TABLE_NAME'],
    #         log_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
    #         api_metrics=vl.api_metrics,
    #         img_meta_data=vl.img_meta_data,
    #         img_bytes=vl.img_bytes,
    #         reason=vl.reason,
    #         request_context=request_context,
    #         identity=vl.identity,
    #         detect_faces_response=vl.detect_faces_response,
    #         search_faces_by_image_response=search_faces_by_image_response
    #     )
    #     return hl.get_return_object(
    #         endpoint=str.ENDPOINT_NAME_RECKON,
    #         status_code=400,
    #         op_status=str.OP_STATUS_FAILED,
    #         response_code=0,
    #         message=identity_msg,
    #         img_meta_data=vl.img_meta_data,
    #         api_metrics=vl.api_metrics
    #     )

    # Logging das informações da operação no DynamoDB e da imagem recebida no S3
    # dao.log(
    #     id=vl.id,
    #     endpoint=str.ENDPOINT_NAME_RECKON,
    #     table_name=dict(os.environ.items())['RECKON_TABLE_NAME'],
    #     log_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
    #     api_metrics=vl.api_metrics,
    #     img_meta_data=vl.img_meta_data,
    #     img_bytes=vl.img_bytes,
    #     reason=vl.reason,
    #     request_context=request_context,
    #     identity=vl.identity,
    #     detect_faces_response=vl.detect_faces_response,
    #     search_faces_by_image_response=search_faces_by_image_response
    # )

    vl.api_metrics['business_logic_time'] = round(time.time() - time_business_logic, 3)

    # Retorno de objeto de sucesso
    return hl.get_return_object(
        endpoint=str.ENDPOINT_NAME_RECKON,
        status_code=200,
        op_status=str.OP_STATUS_SUCCESS,
        response_code=0,
        message=identity_msg,
        img_meta_data=vl.img_meta_data,
        api_metrics=vl.api_metrics
    )

