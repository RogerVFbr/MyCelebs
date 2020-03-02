from interfaces.api_phase import APIPhase as ap
from handlers.sqs_web_scraper.validation import Validation


def web_scraper(event, context):

    print('.')
    print('+------------------------------------------+')
    print('| . . . . . . . . WEB SCRAPER . . . . . . .|')
    print('+------------------------------------------+')

    # Execute validation phase
    vl = Validation(event)
    if not vl.status: return

    ap.finalize_function(vl.invocation_id)

