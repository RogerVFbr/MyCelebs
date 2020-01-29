from abc import ABC, abstractmethod
from datetime import datetime

from interfaces.models.response_object import ResponseObject
from services.api_metrics import ApiMetrics
from resources.environment_variables import EnvironmentVariables
from resources.errors import Errors
from resources.models.error import Error
from resources.strings_en import Strings


class APIPhase(ABC):
    """
    Superclass encapsulating behavioral properties and methods common to all API phases. Is responsible for carrying
    and exposing phase status, error objects and message strings. Also stores cloud function invocation ID and provides
    interfaces for accessing the metrics API and logging. Serves as a factory for response objects.
    """

    err = Errors                                         # :Error: Contains error message objects.
    rsc = Strings                                        # :Strings: Contains general strings.
    env = EnvironmentVariables                           # :EnvironmentVariables: Contains environment variables.

    def __init__(self, prefix: str, phase_name: str, invocation_id: str = None):
        """
        Constructor of the APIPhase superclass, stores client/subclass data and generates unique invocation id if
        none has been provided.
        :param prefix: string. Prefix for logging.
        :param invocation_id: string. Unique execution identifier for metrics.
        """

        self.status = False                              # :boolean: Flag to expose phase status.
        self.failed_return_object = {}                   # :dict: Exposes failure return object in case of failure.
        self.prefix = prefix                             # :str: Current API phase prefix for logging.
        self.phase_name = phase_name                     # :str: Current API phase name.
        self.invocation_id = self.get_id(invocation_id)  # :str: Handles execution invocation Id for metrics.
        self.metrics = ApiMetrics                        # :ApiMetrics: Contains metrics measurement module.

        super().__init__()                               # Runs ABC abstract class initialization.
        self.__main()                                    # Runs API Phase main procedure.

    def __main(self):
        """
        Main API Phase procedure: measures phase time duration, executes phase business logic, logs phase start and
        end.
        :return: void.
        """

        # Start phase time counter.
        self.start_metrics(self.phase_name)

        # Log phase start
        self.log(self.rsc.PHASE_START.format(self.phase_name))

        # Run phase business logic, abort if fails.
        if not self.run(): return

        # Stop phase time counter.
        elapsed = self.stop_metrics(self.phase_name)

        # Flag and log phase status as successful (true).
        self.status = True
        self.log(self.rsc.PHASE_SUCCESSFUL.format(self.phase_name, elapsed))

    @abstractmethod
    def run(self) -> bool:
        """
        Phase business logic (to be overridden by child phase classes).
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """
        pass

    @staticmethod
    def get_return_object(status_code: int = 200,
                          response_code: int = 0,
                          msg_dev: str = 'N.A.',
                          msg_user: str = 'N.A.',
                          img_meta_data: dict = {},
                          api_metrics: dict = {}) -> dict:
        """
        Builds default Response object according to provided parameters end returns it in dictionary form.
        :param status_code: integer. API response HTTP status code.
        :param response_code: integer. API custom response code.
        :param msg_dev: string. Detailed status description message to be used for developing/debugging purposes.
        :param msg_user: string. Generic user oriented message describing status of response.
        :param img_meta_data: dictionary. Meta data extracted from sent image if available.
        :param api_metrics: dictionary. Time measurements of each API execution phase.
        :return:
        """

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
                                 api_metrics: dict = {}) -> dict:
        """
        Builds default error Response object according to provided parameters end returns it in dictionary form.
        :param error_object: Error object. Encapsulated general messages associated with particular error.
        :param img_meta_data: dictionary. Meta data extracted from sent image if available.
        :param api_metrics: dictionary. Time measurements of each API execution phase.
        :return:
        """

        return ResponseObject(
            status_code=error_object.status_code,
            response_code=error_object.response_code,
            msg_dev=error_object.msg_dev,
            msg_user=error_object.msg_user,
            img_meta_data=img_meta_data,
            api_metrics=api_metrics

        ).__dict__

    @staticmethod
    def get_id(invocation_id) -> str:
        """
        Provides unique invocation identifier if needed.
        :param invocation_id: string. Invocation Id.
        :return: string.
        """

        # If an invocation ID has been provided, use it.
        if invocation_id:
            return invocation_id

        # If none has been provided, return a new one.
        else:
            return datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")

    def log(self, msg):
        """
        Logs general messages on cloud logging system by concatenating phase prefix with provided message.
        :param msg: string. Message to be logged.
        :return: void.
        """

        print(f'{self.prefix} - {msg}')

    def start_metrics(self, metric):
        """
        Initiates time measurement of a particular phase of the API execution.
        :param metric: string. API procedure to be measured.
        :return: void.
        """

        self.metrics.start(self.invocation_id, metric)

    def stop_metrics(self, metric) -> float:
        """
        Stops the time measurement of a particular phase of the API execution.
        :param metric: string. API procedure whose measurement is to be stopped..
        :return: float. Phase final time measurement.
        """

        return self.metrics.stop(self.invocation_id, metric)

    def get_metrics(self, invocation_id: str = None) -> dict:
        """
        Extracts the final API metrics dictionary.
        :return: dictionary. Contains measured metrics of this particular cloud function invocation.
        """

        if not invocation_id:
            return self.metrics.get(self.invocation_id)
        else:
            return self.metrics.get(invocation_id)

    def get_metrics_snapshot(self, invocation_id: str = None) -> dict:
        """
        Extracts current API metrics dictionary.
        :return: dictionary. Contains measured metrics of this particular cloud function invocation.
        """

        if not invocation_id:
            return self.metrics.get_snapshot(self.invocation_id)
        else:
            return self.metrics.get_snapshot(invocation_id)


