from endpoint_add_picture.image_pre_processing import ImagePreProcessing
from endpoint_add_picture.save_image import SaveImage
from interfaces.api_phase import APIPhase
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
    rc = RecognizeCelebrity(pp.img_bytes, vl.invocation_id)
    if not rc.status:
        return rc.failed_return_object

    # Save image
    si = SaveImage(pp.img_bytes, pp.img_meta_data['type'], vl.invocation_id)
    if not si.status:
        return si.failed_return_object

    # Save log

    # Return success object
    return APIPhase.get_return_object(
        status_code=200,
        response_code=0,
        msg_dev='Success',
        msg_user='Success',
        img_meta_data=pp.img_meta_data,
        api_metrics=rc.get_metrics()
    )