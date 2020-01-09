class Strings:

    ENDPOINT_NAME_REGISTER = 'register'
    ENDPOINT_NAME_RECKON = 'reckon'
    ENDPOINT_NAME_DELETE = 'delete'

    OP_STATUS_SUCCESS = 'success'
    OP_STATUS_FAILED = 'failed'

    VALIDATION_MSG_REQUEST_INPUT_FIELDS_FAILED_DETAILS = "VL - Input field integrity: INVALID (Expected: {} | Missing: '{}')."
    VALIDATION_MSG_REQUEST_INPUT_FIELDS_FAILED = 'VL - FAILED request input field validation.'
    VALIDATION_MSG_REQUEST_INPUT_FIELDS_SUCCESS = 'VL - Input field integrity: OK ({}).'
    VALIDATION_MSG_ID_UNIQUENESS_UNIQUE = "VL - Id '{}' is unique."
    VALIDATION_MSG_ID_UNIQUENESS_NOT_UNIQUE = "VL - Id '{}' is NOT unique."
    VALIDATION_MSG_ID_UNIQUENESS_FAILED = 'VL - FAILED Id uniqueness validation.'
    VALIDATION_MSG_BASE64_INTEGRITY_FAILED_DETAILS = 'VL - BASE64 encoded image integrity: Impossible to decode.'
    VALIDATION_MSG_BASE64_INTEGRITY_FAILED = 'VL - FAILED BASE64 integrity validation.'
    VALIDATION_MSG_IMAGE_CHARATERISTICS_FAILED = 'VL - FAILED Image characteristics validation.'
    VALIDATION_MSG_IMG_CHAR_NO_FACES = 'Unable to find human face on image.'
    VALIDATION_MSG_IMG_CHAR_MORE_THAN_ONE_FACE = 'More than one face found on image.'
    VALIDATION_MSG_IMG_CHAR_UNACCEPTABLE_QUALITY = 'Image quality is unacceptable.'
    VALIDATION_MSG_SUCCESS = 'VL - Successfully passed all validation procedures.'

    SUCCESS_MSG_REGISTRATION = "Successfully registered new user under Id '{}'."
    SUCCESS_MSG_DELETE = "Successfully deleted user with Id '{}'."
    SUCCESS_MSG_IDENTITY_CHECK = 'Id matches user (Similarity: {:.2f}% | Confidence: {:.2f}%)'

    ERROR_MSG_JSON_STRUCTURE_INVALID = 'JSON structure invalid.'
    ERROR_MSG_UNKNOWN_ID = "Id '{}' is not associated with any user."
    ERROR_MSG_TAKEN_ID = "Id '{}' is taken."
    ERROR_MSG_UNABLE_TO_DECODE = 'Unable to decode image.'

    ERROR_MSG_FAILED_TO_REGISTER = 'Failed to register new user'
    ERROR_MSG_FACE_DOESNT_MATCH = "Face doesn't match user."
    ERROR_MSG_UNEXPECTED_SEARCH_FACES_BY_IMAGE_RESPONSE_STRUCTURE = "Unexpected 'search_faces_by_image' response structure."
    ERROR_MSG_UNEXPECTED_RECOGNITION_ERROR = "Unexpected recognition error."

    LOG_ERROR_UNABLE_TO_LOG = "Unable to log acquired data."

