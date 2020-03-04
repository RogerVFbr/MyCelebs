from interfaces.cloud_function_phase import CloudFunctionPhase
from services.aws_dynamodb import AWSDynamoDB


class CheckCelebrityUniqueness(CloudFunctionPhase):
    """
    Log saving object class, responsible for saving a given log in dictionary form to a persistent repository.
    """

    def __init__(self, user_id: str, celebrities: list, invocation_id: str):
        """
        Constructor of the log saving object, stores provided data and instantiates log repository.
        :param data: dictionary containing the data to be stored.
        :param invocation_id: string containing id of current cloud function invocation to be to be used by API metrics.
        """

        self.repository = AWSDynamoDB(self.env.CELEBRITIES_TABLE_NAME)      # :AWSDynamoDB: Celebrities repository.
        self.celebrities = celebrities                                      # :dict: data to be stored.
        self.user_id = user_id                                              # :str: User id.
        self.unique_celebs = []                                             # :list: Stores new celebs.

        # Initializes APIPhase superclass parameters and procedures
        super(CheckCelebrityUniqueness, self).__init__(prefix='CD', phase_name='Check local celebrity data',
                                                       invocation_id=invocation_id)

    def run(self):
        """
        Object's main procedure: verifies service requirements and conditions, loads data.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Checks database/table status and requirements.
        if not self.__evaluate_conditions_and_requirements(): return False

        # Attempts to to detect is picture celebrity is new on local database, aborts if unable.
        for celeb in self.celebrities:
            if not self.__get_unique_celebrities(celeb): return False

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
            return False

        # Procedure successful, log and return.
        self.log(self.rsc.LOG_SAVE_DATABASE_DESCRIPTION.format(description))
        return True

    def __get_unique_celebrities(self, celeb) -> int:
        """
        Retrieves entry count of a particular key combination.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Attempts to load data from repository.
        key_range = celeb['name'].lower().replace(' ', '-')
        try:
            response = self.repository.load(self.user_id, range_key_equals=key_range)

        # Abort and return if impossible.
        except Exception as e:
            self.log(self.rsc.LOG_LOAD_FAILED.format(str(e)))
            return False

        # Extract log count, abort if impossible.
        log_count = response.get('Count')
        if log_count is None:
            self.log(self.rsc.UNABLE_TO_EXTRACT_LOG_COUNT)
            return False

        # Check celebrity uniqueness.
        if log_count == 0:
            self.log(self.rsc.UNIQUE_CELEBRITY.format(celeb['name'], log_count, self.user_id, key_range))
            self.unique_celebs.append(celeb)
        else:
            self.log(self.rsc.DUPLICATED_CELEBRITY.format(celeb['name'], log_count, self.user_id, key_range))

        return True

