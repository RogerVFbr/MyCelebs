import base64

from interfaces.api_phase import CloudFunctionPhase


class Validation(CloudFunctionPhase):
    """
    Validation object class, responsible for validating, decoding and exposing data retrieved from the client's
    sent request object (event dictionary).
    """

    def __init__(self, event: dict):
        """
        Constructor of the Validation object, stores client provided and decoded data.
        :param event: AWS event dictionary.
        """

        self.event = event                  # :dict: AWS Event object.
        self.user_id = None                 # :str: User Id as declared on request payload..
        self.img_name = None                # :str: Client provided name.
        self.img_desc = None                # :str: Client provided image description.
        self.img_b64_str = None             # :str: BASE64 encoded string, containing image in original payload form.
        self.img_bytes = None               # :bytes: Image in bytes form, product of base64.b64decode().

        # Initializes APIPhase superclass parameters and procedures
        invocation_id = event.get('invocation_id')
        super(Validation, self).__init__(prefix='VL', phase_name='Validation', invocation_id=invocation_id)

    def run(self) -> bool:
        """
        Object's main procedure: extract and decode information from event object.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Extract information from request object and abort if unable.
        if not self.__extract_info_from_body(): return False

        # Decode BASE64 to desired format and abort if unable.
        if not self.__decode_base64_image(): return False

        # Procedure successful
        return True

    def __extract_info_from_body(self) -> bool:
        """
        Double checks request object's fields and content existence and copies values to instance variables.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Extracts information from newly acquired request object.
        self.img_name = self.event.get('img_name', 'N.A.').strip()
        self.img_desc = self.event.get('img_desc', 'N.A.').strip()
        self.user_id = self.event.get('user_id', 'N.A.').strip()

        # Checks for existence of BASE64 string and assigns value to instance variable. If unsuccessful, abort.
        img_b64 = self.event.get('image')
        if not img_b64:
            error_response = self.err.INEXISTENT_BASE64_STRING
            self.log(error_response.aws_log)
            self.failed_return_object = self.get_failed_return_object(error_response, {}, self.get_metrics())
            return False
        self.img_b64_str = img_b64

        # Process completed successfully, log and return true.
        self.log(self.rsc.VALIDATION_EXTRACTED_BODY_PAYLOAD)
        return True

    def __decode_base64_image(self) -> bool:
        """
        Decodes BASE64 string into bytes.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Attempts to decode BASE64 string into bytes.
        try:
            self.img_bytes = base64.b64decode(self.img_b64_str)

        # If unable to decode BASE64 image string, build failed return object and abort execution.
        except Exception as e:
            error_response = self.err.UNDECODABLE_BASE64_STRING
            self.log(error_response.aws_log.format(str(e)))
            self.failed_return_object = self.get_failed_return_object(error_response, {}, self.get_metrics())
            return False

        # Process completed successfully, log and return true.
        self.log(self.rsc.VALIDATION_DECODED_BASE64)
        return True




