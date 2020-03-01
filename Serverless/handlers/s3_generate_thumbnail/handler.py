from handlers.s3_generate_thumbnail.image_processing import ImageProcessing
from handlers.s3_generate_thumbnail.load_image import LoadImage
from handlers.s3_generate_thumbnail.save_image import SaveImage
from handlers.s3_generate_thumbnail.validation import Validation
from interfaces.api_phase import APIPhase as ap
from services.aws_s3_dao import AWSS3


def generate_thumbnail(event, context):

    print('.')
    print('+------------------------------------------+')
    print('| . . . . . .GENERATE THUMBNAIL . . . . . .|')
    print('+------------------------------------------+')

    # Execute validation phase
    vl = Validation(event)
    if not vl.status: return

    # Execute image loading phase
    li = LoadImage(AWSS3(ap.env.BUCKET_NAME), vl.file_name, vl.invocation_id)
    if not li.status: return

    # Execute image processing phase
    ip = ImageProcessing(li.img_bytes_io, vl.invocation_id)
    if not ip.status: return

    # Save image
    si = SaveImage(ip.img_bytes, ip.img_ext, vl.invocation_id)
    if not si.status: return

    ap.log_successful_execution_msg(vl.invocation_id)


