class Strings:

    PHASE_START = 'Initializing {} phase...'
    PHASE_SUCCESSFUL = "Successfully completed '{}' phase procedures. Elapsed: {}s."

    VALIDATION_EXTRACTED_BODY_PAYLOAD = 'Extracted payload from request object.'
    VALIDATION_DECODED_BASE64 = 'Decoded BASE64 encoded image string.'

    PRE_PROC_CREATED_PILLOW_OBJECT = 'Pillow Image object created.'
    PRE_PROC_NO_ROTATION_NEEDED = 'No image rotation needed. (EXIF Orientation: {})'
    PRE_PROC_ORIENTATION_MISMATCH_DETECTED = 'Image orientation mismatch type {} detected. Rotating image by {} ' \
                                             'degrees counter-clockwise to compensate.'
    PRE_PROC_UNABLE_TO_UPDATE_BYTES = 'Could not update image bytes with newly rotated image: {}'
    PRE_PROC_NO_EXIF_ORIENTATION = 'No EXIF orientation found on image.'
    PRE_PROC_SUCCESSFULLY_ROTATED = 'Successfully updated image bytes with newly rotated image.'

    RECOGNITION_API_CONTACTED = 'Successfully contacted "recognize_celebrities" API.'
    RECOGNITION_STATUS_SUCCESS = '"recognize_celebrities" API response denotes success.'
    RECOGNITION_DIGESTED_RESPONSE = 'Digested "recognize_celebrities" response: {}'
    RECOGNITION_ORIENTATION_RECOMMENDATION = 'Recommended orientation correction: {}'
    RECOGNITION_ACQUIRED_META_DATA = 'Final image meta data: {}'

    IMAGE_SAVE_API_CONTACTED = 'Saved image to "S3" blob storage API. Response: {}'
    IMAGE_SAVE_PUBLIC_URL = 'Image will be available at: {}'






