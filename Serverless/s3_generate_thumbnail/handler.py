from s3_generate_thumbnail.load_image import LoadImage
from s3_generate_thumbnail.validation import Validation
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

    ap.log_successful_execution_msg(vl.invocation_id)


