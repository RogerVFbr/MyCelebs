class Strings:

    PHASE_START = "'{}' phase initializing..."
    PHASE_SUCCESSFUL = "'{}' phase completed. Elapsed: {}s."

    VALIDATION_EXTRACTED_BODY_PAYLOAD = 'Extracted payload from request object.'
    VALIDATION_DECODED_BASE64 = 'Decoded BASE64 image string to bytes.'

    PRE_PROC_CREATED_PILLOW_OBJECT = 'Pillow Image object created.'
    PRE_PROC_NO_ROTATION_NEEDED = 'No image rotation needed. (EXIF Orientation: {})'
    PRE_PROC_ORIENTATION_MISMATCH_DETECTED = 'Image orientation mismatch type {} detected. Rotating image by {} ' \
                                             'degrees counter-clockwise to compensate.'
    PRE_PROC_UNABLE_TO_UPDATE_BYTES = 'Could not update image bytes with newly rotated image: {}'
    PRE_PROC_NO_EXIF_ORIENTATION = 'No EXIF orientation found on image.'
    PRE_PROC_SUCCESSFULLY_ROTATED = 'Successfully updated image bytes with newly rotated image.'

    PROC_SUCCESSFULLY_GENERATED_TUMBNAIL = 'Generated {}x{} thumbnail from {}x{} sized image.'
    PROC_UNABLE_TO_GENERATE_TUMBNAIL = 'Unable to generate thumbnail: {}'

    RECOGNITION_API_CONTACTED = 'Contacted "recognize_celebrities" API.'
    RECOGNITION_STATUS_SUCCESS = '"recognize_celebrities" API response denotes success.'
    RECOGNITION_DIGESTED_RESPONSE = 'Digested "recognize_celebrities" response: {}'
    RECOGNITION_ORIENTATION_RECOMMENDATION = 'Recommended orientation correction: {}'
    RECOGNITION_ACQUIRED_META_DATA = 'Final image meta data: {}'

    IMAGE_SAVE_API_CONTACTED = 'Saved image to "S3" file storage API ({}). Response: {}'
    IMAGE_LOAD_API_CONTACTED = 'Loaded image from "S3" file storage API. Response: {}'
    IMAGE_LOAD_API_FAIL = 'Unable to load image from "S3" file storage API. Response: {}'
    IMAGE_SAVE_PUBLIC_URL = 'Image will be available at: {}'

    LOG_SAVE_DATABASE_DESCRIPTION = 'Database conditions/requirements: {}'
    LOG_SAVE_SUCCESSFUL = "Saved log to database: {}"
    LOG_LOAD_SUCCESSFUL = 'Acquired response from database: {}'
    LOG_LOAD_FAILED = 'Unable to acquire from database: {}'
    UNABLE_TO_EXTRACT_LOG_COUNT = 'Unable extract log count.'
    UNIQUE_CELEBRITY = "'{}' is unique in this user's database. (Count: {} | Hash: '{}' | Range: '{}')"
    DUPLICATED_CELEBRITY = "'{}' already exists in this user's database. (Count: {} | Hash: '{}' | Range: '{}')"

    INAPPROPRIATE_EVENT_NAME = 'Ignoring inappropriate event type: {}'
    APPROPRIATE_EVENT_NAME = 'Proper event type detected, proceeding with execution: {}'
    UNEXPECTED_RESPONSE_STRUCTURE = 'ERROR: Unexpected response structure.'
    INEXISTENT_NEW_ENTRY = "ERROR: Can't read new entry, it might be empty or response structure might have changed: {}"

    UNABLE_TO_CONNECT_TO_PROXIES_PROVIDER = "Unable to connect to proxies provider '{}'. Elapsed: {}. -> {}."
    PROXIES_FOUND = "Found {} HTTPS ready proxies @ '{}'. Elapsed: {}."
    PROXY_ATTEMPTING_CONNECTION = "Attempting connection via: {}."
    PROXY_ATTEMPTS_TIMED_OUT = "Connections attempts timed out without result. Elapsed: {}"
    PROXY_EVALUATED = "Evaluated {} proxies."
    PROXY_SELECTED = "Proxy selected: {}. Attempt: {}. Elapsed: {}"
    PROXY_UNABLE_TO_QUALIFY = "Unable to qualify proxy. Elapsed: {}"
    PROXY_SKIPPED = "Discarding '{}': {}."

    UNABLE_TO_DELETE_FROM_DATABASE = 'ERROR: Unable to delete from database: {}'
    DELETED_FROM_DATABASE = 'Data deleted from database. Id: {}'

    SUCCESSFUL_CLOUD_FUNCTION_EXECUTION = 'FUNCTION EXECUTION COMPLETED UNDER INVOCATION ID: {}'






