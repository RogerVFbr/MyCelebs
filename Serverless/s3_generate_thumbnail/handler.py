from s3_generate_thumbnail.validation import Validation


def generate_thumbnail(event, context):

    print('.')
    print('+------------------------------------------+')
    print('| . . . . . .GENERATE THUMBNAIL . . . . . .|')
    print('+------------------------------------------+')

    # Execute validation phase
    vl = Validation(event)
    if not vl.status: return

