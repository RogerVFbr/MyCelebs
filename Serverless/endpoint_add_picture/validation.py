import base64

from interfaces.api_phase import APIPhase


class Validation(APIPhase):

    def __init__(self, event: dict):
        """
        Constructor of the Validation object, responsible for validating, pre-processing and exposing
        data retrieved from the client sent request object.
        :param event: AWS event dictionary.
        :param metrics: ApiMetrics object, responsible for performance measuring.
        """

        # Initializes APIPhase superclass parameters
        super(Validation, self).__init__(prefix='VL')

        self.event = event                  # :dict: AWS Event object.
        self.img_name = None                # :str: Client provided name.
        self.img_desc = None                # :str: Client provided image description.
        self.img_b64_str = None             # :str: BASE64 encoded string, containing image in original payload form.
        self.img_bytes = None               # :bytes: Image in bytes form, product of base64.b64decode().

        self.__execute()                    # Initiate validation procedure upon instantiation.

    def __execute(self):
        """
        Object's main procedure: validates, decodes and extracts information from request object.
        :return: void.
        """

        # Start validation time counter.
        self.start_metrics('Validation')

        # Log validation phase start
        self.log(self.rsc.VALIDATION_PHASE_START)

        # Extract information from request object and abort if unable.
        if not self.__extract_info_from_body(): return

        # Decode BASE64 to desired format and abort if unable.
        if not self.__decode_base64_image(): return

        # Flag and log validation status as successful (true).
        self.status = True
        self.log(self.rsc.VALIDATION_MSG_SUCCESS)

        # Stop validation time counter.
        self.stop_metrics('Validation')

    def __extract_info_from_body(self):
        """
        Double checks request object's fields and content existence and copies values to instance variables.
        :return: boolean.
        """

        # Extracts information from newly acquired request object.
        self.img_name = self.event.get('img_name', 'N.A.').strip()
        self.img_desc = self.event.get('img_desc', 'N.A.').strip()

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

    def __decode_base64_image(self):
        """
        Decodes BASE64 string into bytes.
        :return: boolean.
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

