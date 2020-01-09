import json
import time

from lib.Helpers.Helpers import Helpers as hl
from lib.Resources.Resources_strings_en import Strings as str
from lib.Resources.Resources_config import Config as cnf
from lib.Resources.EnvironmentVariables import EnvironmentVariables as ev
from Register.RegisterManager import RegisterManager as rm
from lib.Validation.Validation import Validation
from lib.Dao.Dao import Dao as dao


def register(event, context):

    print('.')
    print('+------------------------------------------+')
    print('| . . . . . . . . . REGISTER . . . . . . . |')
    print('+------------------------------------------+')

    # Extração do payload enviado e de informações de contexto da reqisição.
    body = json.loads(event["body"])
    request_context = event['requestContext']
    request_time_id = hl.get_request_time_id()

    # Inicialização do procedimento de validação do payload
    vl = Validation()
    vl.validate_request_object(
        endpoint_name=str.ENDPOINT_NAME_REGISTER,
        body=body,
        request_fields=cnf.EXPECTED_REQUEST_FIELDS,
        request_context=request_context,
        id_must_be_unique=True,
    )
    if not vl.validation_status:
        return vl.failed_return_object

    # Registro de novo usuário na coleção global.
    time_business_logic = time.time()
    registration_status, registration_msg, index_faces_response = rm.register_new_user_on_global_collection(vl.img_bytes, vl.id)
    if not registration_status:
        vl.api_metrics['business_logic_time'] = round(time.time() - time_business_logic, 3)
        return hl.get_return_object(
            endpoint=str.ENDPOINT_NAME_REGISTER,
            status_code=400,
            op_status=str.OP_STATUS_FAILED,
            response_code=0,
            message=registration_msg,
            img_meta_data=vl.img_meta_data,
            api_metrics=vl.api_metrics
        )

    # Inicializacao de uma nova colecao em caso de novo usuario, ou retorno de erro em caso de usuario ja existente
    faceId = index_faces_response.get('FaceRecords')[0].get('Face').get('FaceId')
    registration_status, registration_msg, index_faces_response_2 = \
        rm.register_new_user_on_own_collection(vl.img_bytes, vl.id, faceId)
    if not registration_status:
        vl.api_metrics['business_logic_time'] = round(time.time() - time_business_logic, 3)
        return hl.get_return_object(
            endpoint=str.ENDPOINT_NAME_REGISTER,
            status_code=400,
            op_status=str.OP_STATUS_FAILED,
            response_code=0,
            message=registration_msg,
            img_meta_data=vl.img_meta_data,
            api_metrics=vl.api_metrics
        )

    # Logging das informações da operação no DynamoDB e da imagem recebida no S3
    log_status, log_message, img_s3_location_hash = dao.log(
        id=vl.id,
        endpoint=str.ENDPOINT_NAME_REGISTER,
        table_name=ev.REGISTER_TABLE_NAME,
        alternative_table=ev.ACTIVE_REGISTER_TABLE_NAME,
        log_time=request_time_id,
        api_metrics=vl.api_metrics,
        img_meta_data=vl.img_meta_data,
        img_bytes=vl.img_bytes,
        reason=vl.reason,
        request_context=request_context,
        identity=vl.identity,
        detect_faces_response=vl.detect_faces_response,
        index_faces_response=index_faces_response
    )

    if not log_status:
        return hl.get_return_object(
            endpoint=str.ENDPOINT_NAME_REGISTER,
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
        endpoint=str.ENDPOINT_NAME_REGISTER,
        status_code=200,
        op_status=str.OP_STATUS_SUCCESS,
        response_code=0,
        message=registration_msg,
        img_meta_data=vl.img_meta_data,
        api_metrics=vl.api_metrics,
        request_id=request_time_id,
        img_url=f'https://{ev.FRONT_BUCKET_NAME}.s3.amazonaws.com/{img_s3_location_hash}'
    )

