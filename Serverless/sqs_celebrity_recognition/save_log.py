from interfaces.api_phase import APIPhase
from services.aws_dynamodb import AWSDynamoDB


class SaveLog(APIPhase):
    """
    Log saving object class, responsible for saving a given log in dictionary form to a persistent repository.
    """

    def __init__(self, data: dict, invocation_id: str):
        """
        Constructor of the log saving object, stores provided data and instantiates log repository.
        :param data: dictionary containing the data to be stored.
        :param invocation_id: string containing id of current cloud function invocation to be to be used by API metrics.
        """

        self.repository = AWSDynamoDB(self.env.PICTURES_TABLE_NAME)      # :AWSDynamoDB: log repository.
        self.data = data                                                 # :dict: data to be stored.

        # Initializes APIPhase superclass parameters and procedures
        super(SaveLog, self).__init__(prefix='SL', phase_name='Save log', invocation_id=invocation_id)

    def run(self):
        """
        Object's main procedure: verifies service requirements and conditions, saves data.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Checks database/table status and requirements.
        if not self.__evaluate_conditions_and_requirements(): return False

        # Attempts to save log to database, aborts if unable.
        if not self.__save_log(): return False

        # Procedure successful
        return True

    def __evaluate_conditions_and_requirements(self) -> bool:
        """
        Evaluates repository status and requirements.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Attempts to acquire repository description and details.
        try:
            description = self.repository.evaluate_conditions_and_requirements()

        # Abort if impossible
        except Exception as e:
            error_response = self.err.UNABLE_TO_CONTACT_DATABASE
            self.log(error_response.aws_log.format(str(e)))
            self.failed_return_object = self.get_failed_return_object(error_response, {}, self.get_metrics())
            return False

        # Procedure successful, log and return.
        self.log(self.rsc.LOG_SAVE_DATABASE_DESCRIPTION.format(description))
        return True

    def __save_log(self) -> bool:
        """
        Saves provided data to repository.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Attempts to save data on repository.
        try:
            self.repository.save(self.data)

        # Abort and return if impossible.
        except Exception as e:
            error_response = self.err.UNABLE_TO_SAVE_DATABASE
            self.log(error_response.aws_log.format(str(e)))
            self.failed_return_object = self.get_failed_return_object(error_response, {}, self.get_metrics())
            return False

        # Procedure successful, log and return.
        self.log(self.rsc.LOG_SAVE_SUCCESSFUL.format(self.data))
        return True
