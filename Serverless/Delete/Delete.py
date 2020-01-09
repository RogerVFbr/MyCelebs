import json
import time
from lib.Helpers.Helpers import Helpers as hl
from lib.Resources.Resources_strings_en import Strings as str
from lib.Resources.Resources_config import Config as cnf
from Delete.DeleteManager import DeleteManager as dm
from lib.Validation.Validation import Validation


def delete(event, context):

    print('.')
    print('+------------------------------------------+')
    print('| . . . . . . . . . DELETE . . . . . . . . |')
    print('+------------------------------------------+')

    # Extração do payload enviado e de informações de contexto da reqisição.
    body = json.loads(event["body"])
    request_context = event['requestContext']

    # Inicialização do procedimento de validação do payload
    vl = Validation()
    vl.validate_request_object(
        endpoint_name=str.ENDPOINT_NAME_DELETE,
        body=body,
        request_fields=cnf.EXPECTED_REQUEST_FIELDS,
        request_context=request_context,
        id_must_be_unique=False,
        check_image=False
    )
    if not vl.validation_status:
        return vl.failed_return_object

    # Faz tentativa de deletar usuario na collection global
    time_business_logic = time.time()
    delete_status, delete_msg = dm.delete_identity_on_global_collection(vl.id)
    if not delete_status:
        vl.api_metrics['business_logic_time'] = round(time.time() - time_business_logic, 3)
        return hl.get_return_object(
            endpoint=str.ENDPOINT_NAME_DELETE,
            status_code=400,
            op_status=str.OP_STATUS_FAILED,
            response_code=0,
            message=delete_msg,
            img_meta_data={},
            api_metrics=vl.api_metrics
        )

    # Faz tentativa de deletar usuario na própria coleção
    delete_status, delete_msg = dm.delete_identity_on_own_colletion(vl.id)
    if not delete_status:
        vl.api_metrics['business_logic_time'] = round(time.time() - time_business_logic, 3)
        return hl.get_return_object(
            endpoint=str.ENDPOINT_NAME_DELETE,
            status_code=400,
            op_status=str.OP_STATUS_FAILED,
            response_code=0,
            message=delete_msg,
            img_meta_data={},
            api_metrics=vl.api_metrics
        )

    # Faz tentativa de deletar usuario da table de usuarios ativos
    delete_status, delete_msg = dm.delete_identity_on_active_users_table(vl.id)
    if not delete_status:
        vl.api_metrics['business_logic_time'] = round(time.time() - time_business_logic, 3)
        return hl.get_return_object(
            endpoint=str.ENDPOINT_NAME_DELETE,
            status_code=400,
            op_status=str.OP_STATUS_FAILED,
            response_code=0,
            message=delete_msg,
            img_meta_data={},
            api_metrics=vl.api_metrics
        )

    # Retorno de objeto de sucesso
    vl.api_metrics['business_logic_time'] = round(time.time() - time_business_logic, 3)
    return hl.get_return_object(
        endpoint=str.ENDPOINT_NAME_DELETE,
        status_code=200,
        op_status=str.OP_STATUS_SUCCESS,
        response_code=0,
        message=delete_msg,
        img_meta_data={},
        api_metrics=vl.api_metrics
    )