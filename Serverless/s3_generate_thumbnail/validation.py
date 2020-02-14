import json

from interfaces.api_phase import APIPhase


class Validation(APIPhase):
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
        self.origin_bucket = None                   # :str: Image storage bucket name.
        self.destin_bucket = None                   # :str: Image storage bucket name.
        self.file_name = None                       # :str: Image stored file name.
        self.new_entry = {}                         # :dict: Acquired log data.

        # Attempts to extract invocation id from event object.
        invocation_id = \
            self.event.get('Records', [{}])[0].get('s3', {}).get('object', {}).get('key').split('.')[0].split('/')[-1]

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
        Double checks request object's fields and content existence and copies values to instance variables.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Extracts information from newly acquired request object.
        try:
            record = self.event['Records'][0]
            self.origin_bucket = record['s3']['bucket']['name']
            self.destin_bucket = self.env.THUMBNAIL_BUCKET_NAME
            self.file_name = record['s3']['object']['key']
        except Exception as e:
            self.log(self.rsc.INEXISTENT_NEW_ENTRY.format(str(e)))
            return False

        # Process completed successfully, log and return true.
        self.log(self.rsc.VALIDATION_EXTRACTED_BODY_PAYLOAD)
        return True





