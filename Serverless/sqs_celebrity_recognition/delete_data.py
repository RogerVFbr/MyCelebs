from interfaces.api_phase import APIPhase


class DeleteData(APIPhase):
    """
    Log deletion object, responsible for deleting logs from selected database or service.
    """

    def __init__(self, repository, log_id: str, invocation_id: str):
        """
        Constructor of the log deletion object, stores provided data and instantiates log repository.
        :param log_id: string containing the identification code of the log to be deleted.
        :param invocation_id: string containing id of current cloud function invocation to be to be used by API metrics.
        """

        self.repository = repository
        self.log_id = log_id                                           # :str: id of the log to be deleted.

        # Initializes APIPhase superclass parameters and procedures
        super(DeleteData, self).__init__(prefix='DL', phase_name='Delete queue log', invocation_id=invocation_id)

    def run(self):
        """
        Object's main procedure: verifies service requirements and conditions, performs deletion.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Checks database/table status and requirements.
        if not self.__evaluate_conditions_and_requirements(): return False

        # Attempts to save log to database, aborts if unable.
        if not self.__delete_log(): return False

        # Procedure successful
        return True

    def __evaluate_conditions_and_requirements(self) -> bool:
        """
        Evaluates repository and file location status and requirements.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Procedure successful
        self.log(self.rsc.LOG_SAVE_DATABASE_DESCRIPTION.format('N.A.'))
        return True

    def __delete_log(self) -> bool:
        """
        Performs deletion on repository.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Attempts to delete log on given repository.
        try:
            self.repository.delete(self.log_id)

        # Abort and return error if impossible.
        except Exception as e:
            self.log(self.rsc.UNABLE_TO_DELETE_FROM_DATABASE.format(str(e)))
            return False

        # Procedure successful, log and return.
        self.log(self.rsc.DELETED_FROM_DATABASE.format(self.log_id))
        return True
