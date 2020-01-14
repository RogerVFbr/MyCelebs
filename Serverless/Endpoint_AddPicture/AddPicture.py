from Utilities.Helpers.Helpers import Helpers as hl
from Utilities.Helpers.ApiMetrics import ApiMetrics
from Endpoint_AddPicture.Validation import Validation
from Endpoint_AddPicture.RecognizeCelebrity import RecognizeCelebrity


def add_picture(event, context):

    # Initialize metrics gathering tool
    metrics = ApiMetrics()

    # Perform validation stage
    vl = Validation(event, metrics)
    if not vl.validation_status:
        return vl.failed_return_object

    # Perform celebrity recognition stage
    rc = RecognizeCelebrity(vl.img_bytes, vl.img_meta_data, metrics)
    if not rc.recognition_status:
        return rc.failed_return_object



    # Return success object
    return hl.get_return_object(
        status_code=200,
        response_code=0,
        msg_dev='Success',
        msg_user='Success',
        img_meta_data=vl.img_meta_data,
        api_metrics=metrics.get()
    )