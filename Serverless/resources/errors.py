from resources.models.error import Error


class Errors:

    INEXISTENT_BASE64_STRING = Error(
        aws_log='FAILED BASE64 request field validation.',
        msg_dev='Invalid JSON content.',
        msg_user='Unable to work with given information.',
        status_code=400,
        response_code=0
    )

    UNDECODABLE_BASE64_STRING = Error(
        aws_log='FAILED to decode BASE64 string: {}',
        msg_dev='Unable to decode BASE64 string.',
        msg_user='Unable to decode sent file.',
        status_code=400,
        response_code=0
    )

    UNDECODABLE_IMAGE_BYTES = Error(
        aws_log='FAILED to convert image bytes to Pillow Image object: {}',
        msg_dev='Unable to decode image bytes.',
        msg_user='Unable to decode sent file.',
        status_code=400,
        response_code=0
    )

    FAILED_REKOGNITION_REQUEST = Error(
        aws_log='ERROR: Unable to unable to contact "recognize_celebrities" API. Error: {}',
        msg_dev='Unable to contact "recognize_celebrities" API.',
        msg_user='Unable to complete celebrity recognition.',
        status_code=400,
        response_code=0
    )

    UNEXPECTED_REKOGNITION_RESPONSE_STRUCTURE = Error(
        aws_log='ERROR: "recognize_celebrities" response structure might have changed: {}',
        msg_dev='Unexpected "recognize_celebrities" API response structure.',
        msg_user='Unable to complete celebrity recognition.',
        status_code=400,
        response_code=0
    )

    FAILED_REKOGNITION_RESPONSE = Error(
        aws_log='ERROR: Unable to acquire successful "recognize_celebrities" response: {}',
        msg_dev='Unable to acquire successful response from "recognize_celebrities" API.',
        msg_user='Unable to complete celebrity recognition.',
        status_code=400,
        response_code=0
    )

    UNABLE_TO_CONTACT_BLOB_STORAGE_API = Error(
        aws_log='ERROR: Unable to unable to contact "S3" blob storage API. Error: {}',
        msg_dev='Unable to contact "S3" blob storage API.',
        msg_user='Unable to save image.',
        status_code=400,
        response_code=0
    )
