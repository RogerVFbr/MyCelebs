import json
from interfaces.cloud_function_phase import CloudFunctionPhase


class Validation(CloudFunctionPhase):
    """
    Validation object class, responsible for validating and exposing data retrieved from a cloud queue
    service (event dictionary).
    """

    def __init__(self, event: dict):
        """
        Constructor of the Validation object, stores client provided and decoded data.
        :param event: AWS event dictionary.
        """

        self.event = event                          # :dict: AWS Event object.
        self.user_id = None                         # :str: Request user id.
        self.table_id = None
        self.urls = []
        self.celebrity = None                       # :str: Celebrity to scrap.

        # Attempts to extract invocation Id from event object
        invocation_id = json.loads(self.event.get('Records', [{}])[0].get('body', {})).get('invocation_id')

        # Initializes APIPhase superclass parameters and procedures
        super(Validation, self).__init__(prefix='VL', phase_name='Validation', invocation_id=invocation_id)

    def run(self) -> bool:
        """
        Object's main procedure: evaluate and extract information from event object.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Extract information from request object and abort if unable.
        if not self.__extract_info_from_body(): return False

        # Procedure successful
        return True

    def __extract_info_from_body(self) -> bool:
        """
        Double checks request object's fields and content existence and points values to instance variables.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Extracts information from newly acquired request object.
        try:
            new_entry = json.loads(self.event.get('Records', [{}])[0].get('body', {}))
            self.user_id = new_entry['user_id']
            self.celebrity = new_entry['celebrity']
            self.table_id = self.celebrity['table_id']
            self.urls = self.celebrity['urls']
        except Exception as e:
            self.log(self.rsc.INEXISTENT_NEW_ENTRY.format(str(e)))
            return False

        # Process completed successfully, log and return true.
        self.log(self.rsc.VALIDATION_EXTRACTED_BODY_PAYLOAD)
        return True





