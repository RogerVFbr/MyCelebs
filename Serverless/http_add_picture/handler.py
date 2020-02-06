from http_add_picture.validation import Validation
from http_add_picture.image_pre_processing import ImagePreProcessing
from http_add_picture.save_image import SaveImage
from http_add_picture.save_data import SaveData
from interfaces.api_phase import APIPhase as ap
from services.aws_sqs import AWSSQS


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

    # Save image
    si = SaveImage(pp.img_bytes, pp.img_meta_data.type, vl.invocation_id)
    if not si.status:
        return si.failed_return_object
    pp.img_meta_data.size = si.img_size

    # Assemble log object
    data_to_be_persisted = {
        'id': vl.user_id,
        'time': vl.invocation_id,
        'file_name': si.file_name,
        'api_metrics': {'add_picture': si.get_metrics_snapshot()},
        'img_name': vl.img_name,
        'img_desc': vl.img_desc,
        'img_url': si.img_url,
        'img_thumbnail_url': si.img_thumbnail_url,
        'img_meta_data': {
            'type': pp.img_meta_data.type,
            'size': si.img_size,
            'height': pp.img_meta_data.height,
            'width': pp.img_meta_data.width,
            'exif': pp.img_meta_data.exif
        }
    }

    # Save log
    sl = SaveData(AWSSQS(ap.env.QUEUE_BASE_URL, ap.env.ADD_PICTURE_QUEUE_NAME), data_to_be_persisted, vl.invocation_id)
    if not sl.status:
        return sl.failed_return_object

    print(ap.rsc.SUCCESSFUL_CLOUD_FUNCTION_EXECUTION.format(vl.invocation_id))

    # Return success object
    return ap.get_return_object(
        status_code=200,
        response_code=0,
        msg_dev='Success',
        msg_user='Success',
        img_meta_data=pp.img_meta_data.__dict__,
        api_metrics=sl.get_metrics()
        # api_metrics=si.get_metrics()
    )