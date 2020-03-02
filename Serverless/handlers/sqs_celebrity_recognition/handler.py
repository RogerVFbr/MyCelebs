from handlers.sqs_celebrity_recognition.check_local_celebrity_data import CheckLocalCelebrityData
from handlers.sqs_celebrity_recognition.validation import Validation
from interfaces.save_log import SaveLog
from interfaces.api_phase import APIPhase as ap
from services.aws_dynamodb import AWSDynamoDB
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

    # Build and save picture log.
    pic_log = vl.new_entry
    # pic_data['celebrities'] = rc.celebrities
    pic_log['celebrities'] = [{'name': 'TEST', 'table_id': 'test', 'recognition_id': 'TEST', 'bounding_box': {},
                               'urls': []}]
    # pic_log['orientation_correction'] = rc.orientation_correction
    pic_log['orientation_correction'] = 'TEST_ROTATION'
    if 'api_metrics' not in pic_log: pic_log['api_metrics'] = {}
    pic_log['api_metrics']['celebrity_recognition'] = vl.get_metrics(vl.invocation_id)

    spl = SaveLog(
        repository=AWSDynamoDB(ap.env.PICTURES_TABLE_NAME),
        data=pic_log,
        prefix='SP',
        phase_name='Save picture log',
        invocation_id=vl.invocation_id
    )
    if not spl.status: return

    # Check if local celebrity data exists
    cd = CheckLocalCelebrityData(vl.new_entry['user_id'], pic_log['celebrities'], vl.invocation_id)
    if not cd.status: return

    # Save new celebrities if applicable.
    for celeb in cd.unique_celebs:
        new_celeb_entry = {
            'user_id': vl.new_entry['user_id'],
            'celebrity_id': celeb['name'].lower().replace(' ', ''),
            'recognition_data': celeb
        }
        scl = SaveLog(
            repository=AWSDynamoDB(ap.env.CELEBRITIES_TABLE_NAME),
            data=new_celeb_entry,
            prefix='SC',
            phase_name='Save celebrity log',
            invocation_id=vl.invocation_id
        )
        if not scl.status: return

    # If new celebrities have been detected, trigger web scrapper.
    if len(cd.unique_celebs) > 0:

        # Save to queue
        data_to_be_queued = {
            'user_id': pic_log['user_id'],
            'celebrities': cd.unique_celebs,
            'invocation_id': vl.invocation_id
        }
        sq = SaveLog(
            repository=AWSSQS(ap.env.QUEUE_BASE_URL, ap.env.WEB_SCRAP_QUEUE_NAME),
            data=data_to_be_queued,
            prefix='SQ',
            phase_name='Save to queue',
            invocation_id=vl.invocation_id
        )
        if not sq.status: return

    ap.finalize_function(vl.invocation_id)

