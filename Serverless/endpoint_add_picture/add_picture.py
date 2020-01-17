from endpoint_add_picture.image_pre_processing import ImagePreProcessing
from utilities.helpers import Helpers as hl
from endpoint_add_picture.validation import Validation
from endpoint_add_picture.recognize_celebrity import RecognizeCelebrity


def add_picture(event, context):

    print('.')
    print('+------------------------------------------+')
    print('| . . . . . . . .ADD PICTURE . . . . . . . |')
    print('+------------------------------------------+')

    # Execute validation phase
    vl = Validation(event)
    if not vl.status:
        return vl.failed_return_object

    # Execute image pre-processing phase
    pp = ImagePreProcessing(vl.img_bytes, vl.invocation_id)
    if not pp.status:
        return pp.failed_return_object

    # Execute celebrity recognition phase
    rc = RecognizeCelebrity(pp.img_bytes, pp.img_meta_data, vl.invocation_id)
    if not rc.status:
        return rc.failed_return_object

    # Save image

    # Save log

    # Return success object
    return hl.get_return_object(
        status_code=200,
        response_code=0,
        msg_dev='Success',
        msg_user='Success',
        img_meta_data=vl.img_meta_data,
        api_metrics=rc.get_metrics()
    )