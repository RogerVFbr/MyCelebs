import random, string

from interfaces.models.response_object import ResponseObject
from utilities.api_metrics import ApiMetrics
from resources.errors import Errors
from resources.models.error import Error
from resources.strings_en import Strings


class APIPhase:

    def __init__(self, prefix: str, invocation_id: str = None):
        self.status = False                              # :boolean: Flag to expose phase status.
        self.failed_return_object = {}                   # :dict: Exposes failure return object in case of failure.
        self.prefix = prefix                             # :str: Current API phase prefix for logging.
        self.err = Errors                                # :Error: Contains error message objects.
        self.rsc = Strings                               # :Strings: Contains general strings.
        self.invocation_id = self.get_id(invocation_id)  # :str: Handles execution invocation Id for metrics.

    @staticmethod
    def get_return_object(status_code: int = 200,
                          response_code: int = 0,
                          msg_dev: str = 'N.A.',
                          msg_user: str = 'N.A.',
                          img_meta_data: dict = {},
                          api_metrics: dict = {}):

        return ResponseObject(
            status_code=status_code,
            response_code=response_code,
            msg_dev=msg_dev,
            msg_user=msg_user,
            img_meta_data=img_meta_data,
            api_metrics=api_metrics

        ).__dict__

    @staticmethod
    def get_failed_return_object(error_object: Error,
                                 img_meta_data: dict = {},
                                 api_metrics: dict = {}):

        return ResponseObject(
            status_code=error_object.status_code,
            response_code=error_object.response_code,
            msg_dev=error_object.msg_dev,
            msg_user=error_object.msg_user,
            img_meta_data=img_meta_data,
            api_metrics=api_metrics

        ).__dict__

    @staticmethod
    def get_id(invocation_id):
        if invocation_id:
            return invocation_id
        else:
            return ''.join(random.choice(string.ascii_uppercase) for x in range(6))

    def log(self, msg):
        print(f'{self.prefix} - {msg}')

    def start_metrics(self, metric):
        ApiMetrics.start(self.invocation_id, metric)

    def stop_metrics(self, metric):
        ApiMetrics.stop(self.invocation_id, metric)

    def get_metrics(self):
        return ApiMetrics.get(self.invocation_id)

