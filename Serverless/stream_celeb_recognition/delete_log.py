from interfaces.api_phase import APIPhase
from services.aws_dynamodb import AWSDynamoDB
from services.aws_sqs import AWSSQS


class DeleteLog(APIPhase):

    def __init__(self, log_id: str, invocation_id: str):

        self.repository = AWSSQS(self.env.ADD_PICTURE_QUEUE_URL)
        self.log_id = log_id

        # Initializes APIPhase superclass parameters and procedures
        super(DeleteLog, self).__init__(prefix='DL', phase_name='Delete queue log', invocation_id=invocation_id)

    def run(self):

        # Checks database/table status and requirements.
        if not self.__evaluate_conditions_and_requirements(): return False

        # Attempts to save log to database, aborts if unable.
        if not self.__delete_log(): return False

        # Procedure successful
        return True

    def __evaluate_conditions_and_requirements(self) -> bool:
        self.log(self.rsc.LOG_SAVE_DATABASE_DESCRIPTION.format('N.A.'))
        return True

    def __delete_log(self) -> bool:

        try:
            self.repository.delete(self.log_id)
        except Exception as e:
            self.log(self.rsc.UNABLE_TO_DELETE_FROM_DATABASE.format(str(e)))
            return False

        self.log(self.rsc.DELETED_FROM_DATABASE)
        return True
