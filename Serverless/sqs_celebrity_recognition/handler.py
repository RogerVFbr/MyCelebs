from sqs_celebrity_recognition.validation import Validation
from sqs_celebrity_recognition.celebrity_recognition import RecognizeCelebrity
from sqs_celebrity_recognition.delete_log import DeleteLog
from sqs_celebrity_recognition.save_log import SaveLog


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
    if not rc.status: return

    # Delete queue log
    dl = DeleteLog(vl.log_id, vl.invocation_id)
    if not dl.status: return

    # Build final log object to be stored on database
    data_to_be_persisted = vl.new_entry
    data_to_be_persisted['celebrities'] = rc.celebrities
    data_to_be_persisted['orientation_correction'] = rc.orientation_correction
    if 'api_metrics' not in data_to_be_persisted:
        data_to_be_persisted['api_metrics'] = {}
    data_to_be_persisted['api_metrics']['celebrity_recognition'] = dl.get_metrics()

    # Save final operation log
    sl = SaveLog(data_to_be_persisted, vl.invocation_id)
    if not sl.status: return