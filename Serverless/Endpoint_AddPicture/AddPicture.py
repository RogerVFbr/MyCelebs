from Utilities.Helpers.Helpers import Helpers as hl
from Utilities.Validation.Validation import Validation
from Utilities.Helpers.ApiMetrics import ApiMetrics


def add_picture(event, context):

    metrics = ApiMetrics()

    vl = Validation(event, metrics)
    if not vl.validation_status:
        return vl.failed_return_object

    return hl.get_return_object(
        status_code=200,
        response_code=0,
        msg_dev='Success',
        msg_user='Success',
        img_meta_data=vl.img_meta_data,
        api_metrics=metrics.get()
    )