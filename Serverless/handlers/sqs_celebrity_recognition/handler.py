from handlers.sqs_celebrity_recognition.save_data import SaveData
from handlers.sqs_celebrity_recognition.validation import Validation
from handlers.sqs_celebrity_recognition.save_log import SaveLog
from interfaces.api_phase import APIPhase as ap
from services.aws_sqs import AWSSQS


def celeb_recognition(event, context):

    print('.')
    print('+------------------------------------------+')
    print('| . . . . . CELEBRITY RECOGNITION . . . . .|')
    print('+------------------------------------------+')

    # Execute validation phase
    vl = Validation(event)
    if not vl.status: return

    # Execute celebrity recognition phase
    # rc = RecognizeCelebrity(vl.bucket_name, vl.file_name, vl.invocation_id)
    # if not rc.status: return

    # Build final log object to be stored on database
    data_to_be_persisted = vl.new_entry
    # data_to_be_persisted['celebrities'] = rc.celebrities
    data_to_be_persisted['celebrities'] = [{'name':'TEST', 'celebrity_id':'TEST', 'bounding_box':{}, 'urls':[]}]
    # data_to_be_persisted['orientation_correction'] = rc.orientation_correction
    data_to_be_persisted['orientation_correction'] = 'TEST_ROTATION'
    if 'api_metrics' not in data_to_be_persisted:
        data_to_be_persisted['api_metrics'] = {}
    data_to_be_persisted['api_metrics']['celebrity_recognition'] = vl.get_metrics()

    # Save final operation log
    sl = SaveLog(data_to_be_persisted, vl.invocation_id)
    if not sl.status: return

    data_to_be_queued = {
        'id': data_to_be_persisted['id'],
        'celebrities': data_to_be_persisted['celebrities'],
        'invocation_id': vl.invocation_id
    }

    # Save to queue
    sl = SaveData(AWSSQS(ap.env.QUEUE_BASE_URL, ap.env.WEB_SCRAP_QUEUE_NAME), data_to_be_queued,
                  vl.invocation_id)
    if not sl.status: return

    ap.log_successful_execution_msg(vl.invocation_id)

