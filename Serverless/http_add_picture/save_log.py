from interfaces.api_phase import APIPhase
from services.aws_sqs import AWSSQS


class SaveLog(APIPhase):

    def __init__(self, data: dict, invocation_id: str):

        self.repository = AWSSQS(self.env.ADD_PICTURE_QUEUE_URL)
        self.data = data

        # Initializes APIPhase superclass parameters and procedures
        super(SaveLog, self).__init__(prefix='SL', phase_name='Save log', invocation_id=invocation_id)

    def run(self):

        # Checks database/table status and requirements.
        if not self.__evaluate_conditions_and_requirements(): return False

        # Attempts to save log to database, aborts if unable.
        if not self.__save_log(): return False

        # Procedure successful
        return True

    def __evaluate_conditions_and_requirements(self) -> bool:

        try:
            description = self.repository.evaluate_conditions_and_requirements()

        except Exception as e:
            error_response = self.err.UNABLE_TO_CONTACT_DATABASE
            self.log(error_response.aws_log.format(str(e)))
            self.failed_return_object = self.get_failed_return_object(error_response, {}, self.get_metrics())
            return False

        self.log(self.rsc.LOG_SAVE_DATABASE_DESCRIPTION.format(description))
        return True

    def __save_log(self) -> bool:

        try:
            self.repository.save(self.data)

        except Exception as e:
            error_response = self.err.UNABLE_TO_SAVE_DATABASE
            self.log(error_response.aws_log.format(str(e)))
            self.failed_return_object = self.get_failed_return_object(error_response, {}, self.get_metrics())
            return False

        return True
