from handlers.sqs_web_scraper.get_proxy import GetProxy
from handlers.sqs_web_scraper.validation import Validation
from interfaces.api_phase import CloudFunctionPhase as Cfp



def web_scraper(event, context):

    print('.')
    print('+------------------------------------------+')
    print('| . . . . . . . . WEB SCRAPER . . . . . . .|')
    print('+------------------------------------------+')

    # Execute validation phase
    vl = Validation(event)
    if not vl.status: return

    gp = GetProxy(vl.invocation_id)
    if not gp.status: return

    Cfp.terminate_function(vl.invocation_id)

