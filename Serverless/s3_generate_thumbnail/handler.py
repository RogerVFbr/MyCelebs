from s3_generate_thumbnail.validation import Validation
from interfaces.api_phase import APIPhase as ap


def generate_thumbnail(event, context):

    print('.')
    print('+------------------------------------------+')
    print('| . . . . . .GENERATE THUMBNAIL . . . . . .|')
    print('+------------------------------------------+')

    print(str(event))

    # Execute validation phase
    # vl = Validation(event)
    # if not vl.status: return

    print(ap.rsc.SUCCESSFUL_CLOUD_FUNCTION_EXECUTION.format(''))


