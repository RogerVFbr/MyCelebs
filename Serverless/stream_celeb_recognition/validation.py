import base64
import json

from interfaces.api_phase import APIPhase


class Validation(APIPhase):
    """

    """

    def __init__(self, event: dict):
        """
        Constructor of the Validation object, stores client provided and decoded data.
        :param event: AWS event dictionary.
        """

        self.event = event                  # :dict: AWS Event object.
        self.log_id = None
        self.bucket_name = self.env.BUCKET_NAME
        self.file_name = None
        self.new_entry = {}

        # Initializes APIPhase superclass parameters and procedures
        super(Validation, self).__init__(prefix='VL', phase_name='Validation')

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
        Double checks request object's fields and content existence and copies values to instance variables.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Extracts information from newly acquired request object.
        try:
            self.new_entry = json.loads(self.event.get('Records')[0].get('body'))
            self.log_id = self.event.get('Records')[0].get('receiptHandle')
            self.file_name = self.new_entry.get('file_name', 'N.A.')
        except Exception as e:
            self.log(self.rsc.INEXISTENT_NEW_ENTRY.format(str(e)))
            return False

        # Process completed successfully, log and return true.
        self.log(self.rsc.VALIDATION_EXTRACTED_BODY_PAYLOAD)
        return True




