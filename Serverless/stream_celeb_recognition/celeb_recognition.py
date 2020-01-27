from stream_celeb_recognition.delete_log import DeleteLog
from stream_celeb_recognition.recognize_celebrity import RecognizeCelebrity
from stream_celeb_recognition.validation import Validation


def celeb_recognition(event, context):

    print('.')
    print('+------------------------------------------+')
    print('| . . . . . CELEBRITY RECOGNITION . . . . .|')
    print('+------------------------------------------+')

    # Execute validation phase
    vl = Validation(event)
    if not vl.status: return

    # Execute celebrity recognition phase
    rc = RecognizeCelebrity(vl.bucket_name, vl.file_name, vl.invocation_id)
    if not rc.status:
        return rc.failed_return_object

    # Delete log
    dl = DeleteLog(vl.log_id, vl.invocation_id)
    if not dl.status: return
