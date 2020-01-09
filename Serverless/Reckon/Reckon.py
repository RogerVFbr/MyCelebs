import json, time
from lib.Helpers.Helpers import Helpers as hl
from lib.Resources.Resources_strings_en import Strings as str
from lib.Resources.Resources_config import Config as cnf
from lib.Resources.EnvironmentVariables import EnvironmentVariables as ev
from Reckon.ReckonManager import ReckonManager as rm
from lib.Validation.Validation import Validation
from lib.Dao.Dao import Dao as dao


def reckon(event, context):

    print('.')
    print('+------------------------------------------+')
    print('| . . . . . . . . . RECKON . . . . . . . . |')
    print('+------------------------------------------+')

    # Extração do payload enviado e de informações de contexto da requisição.
    body = json.loads(event["body"])
    request_context = event['requestContext']
    request_time_id = hl.get_request_time_id()

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
    identity_status, identity_msg, search_faces_by_image_response = rm.identity_check(vl.img_bytes, vl.id)
    if not identity_status:
        vl.api_metrics['business_logic_time'] = round(time.time() - time_business_logic, 3)
        log_status, log_message, img_s3_location_hash = dao.log(
            id=vl.id,
            endpoint='failed-' + str.ENDPOINT_NAME_RECKON,
            table_name=ev.FAILED_RECKON_TABLE_NAME,
            log_time=request_time_id,
            api_metrics=vl.api_metrics,
            img_meta_data=vl.img_meta_data,
            img_bytes=vl.img_bytes,
            reason=vl.reason,
            request_context=request_context,
            identity=vl.identity,
            detect_faces_response=vl.detect_faces_response,
            search_faces_by_image_response=search_faces_by_image_response
        )

        # Caso haja ocorrido um erro durante o log
        if not log_status:
            return hl.get_return_object(
                endpoint=str.ENDPOINT_NAME_RECKON,
                status_code=400,
                op_status=str.OP_STATUS_FAILED,
                response_code=0,
                message=identity_msg + ' | ' + log_message,
                img_meta_data=vl.img_meta_data,
                api_metrics=vl.api_metrics
            )

        # Foto enviada nao corresponde a identidade, retorna negativo.
        return hl.get_return_object(
            endpoint=str.ENDPOINT_NAME_RECKON,
            status_code=400,
            op_status=str.OP_STATUS_FAILED,
            response_code=0,
            message=identity_msg,
            img_meta_data=vl.img_meta_data,
            api_metrics=vl.api_metrics,
            request_id=request_time_id,
            img_url=img_s3_location_hash
        )

    # Logging das informações da operação no DynamoDB e da imagem recebida no S3
    log_status, log_message, img_s3_location_hash = dao.log(
        id=vl.id,
        endpoint=str.ENDPOINT_NAME_RECKON,
        table_name=ev.RECKON_TABLE_NAME,
        log_time=request_time_id,
        api_metrics=vl.api_metrics,
        img_meta_data=vl.img_meta_data,
        img_bytes=vl.img_bytes,
        reason=vl.reason,
        request_context=request_context,
        identity=vl.identity,
        detect_faces_response=vl.detect_faces_response,
        search_faces_by_image_response=search_faces_by_image_response
    )

    if not log_status:
        return hl.get_return_object(
            endpoint=str.ENDPOINT_NAME_RECKON,
            status_code=400,
            op_status=str.OP_STATUS_FAILED,
            response_code=0,
            message=log_message,
            img_meta_data=vl.img_meta_data,
            api_metrics=vl.api_metrics
        )

    vl.api_metrics['business_logic_time'] = round(time.time() - time_business_logic, 3)

    # Retorno de objeto de sucesso
    return hl.get_return_object(
        endpoint=str.ENDPOINT_NAME_RECKON,
        status_code=200,
        op_status=str.OP_STATUS_SUCCESS,
        response_code=0,
        message=identity_msg,
        img_meta_data=vl.img_meta_data,
        api_metrics=vl.api_metrics,
        request_id=request_time_id,
        img_url=f'https://{ev.FRONT_BUCKET_NAME}.s3.amazonaws.com/{img_s3_location_hash}'
    )

# https://facial-recog-auth-fellow-01-01-front-images-repo.s3.amazonaws.com/049f6aa8bd6c77eba26b4a0f7fdc8b24.JPEG
# https://facial-recog-auth-fellow-01-01-front-images-repo.s3.amazonaws.com7c9aaced39dcd2b043d95a8bb7d28441.jpeg/
