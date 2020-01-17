import boto3

from interfaces.api_phase import APIPhase
from endpoint_add_picture.models.celebrity import Celebrity


class RecognizeCelebrity(APIPhase):

    def __init__(self, img_bytes: str, img_meta_data: dict,  invocation_id: str):
        """
        Constructor of the celebrity recognition object, responsible for accessing AWS' celebrity recognition API with
        the pre-processed image in bytes form. Is also responsible for validating and processing the response.
        :param img_bytes: string containing pre-processed image in bytes form.
        :param img_meta_data: dictionary of image extracted meta data.
        :param invocation_id:
        """

        # Initializes APIPhase superclass parameters
        super(RecognizeCelebrity, self).__init__(prefix='BL', invocation_id=invocation_id)

        self.img_bytes = img_bytes              # :str: Client provided image in bytes form.
        self.img_meta_data = img_meta_data      # :dict: Dictionary containing image meta data (including EXIF)
        self.celebrities = []                   # :list: List of Celebrity objects built from API response.
        self.orientation_correction = None      # :str: Recognition API orientation recommendation

        self.__execute()                        # Initiate recognition procedure upon instantiation.

    def __execute(self):
        """
        Object's main function/procedure: communicates with API, triggers evaluation and organization of response.
        :return: void.
        """

        # Start recognition time counter.
        self.start_metrics('Recognition')

        # Execute request on celebrity recognition API using given image bytes
        client = boto3.client('rekognition')
        response = client.recognize_celebrities(Image={'Bytes': self.img_bytes})

        # Evaluate recognize_celebrities API response status
        if not self.__evaluate_response_status(response): return

        # Digest response if available, abort if impossible.
        if not self.__digest_response(response): return

        # Flag recognition operation as successful
        self.status = True

        # Stop recognition time counter.
        self.stop_metrics('Recognition')

    def __evaluate_response_status(self, response: dict):
        """
        Evaluates response object integrity and status.
        :param response: Dictionary containing recognition API's response.
        :return: boolean.
        """

        # If HTTPStatusCode is not available in response dictionary, fill up return object and abort execution.
        if not response.get('ResponseMetadata', {}).get('HTTPStatusCode'):
            error_response = self.err.UNEXPECTED_REKOGNITION_RESPONSE_STRUCTURE
            self.log(error_response.aws_log.format(response))
            self.failed_return_object = self.get_failed_return_object(error_response, self.img_meta_data,
                                                                      self.get_metrics())
            return False

        # If HTTPStatusCode is successful (200), return success.
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            self.log(f'Successfully acquired "recognize_celebrities" response: {str(response)}')
            return True

        # If HTTPStatusCode has failed (other than 200), fill up return object and return failure.
        else:
            error_response = self.err.FAILED_REKOGNITION_RESPONSE
            self.log(error_response.aws_log + str(response))
            self.failed_return_object = self.get_failed_return_object(error_response,
                                                                      self.img_meta_data, self.get_metrics())
            return False

    def __digest_response(self, response: dict):
        """
        Translate recognition API response structure to project's (Celebrity objects list).
        :param response: Dictionary containing recognition API's response.
        :return: boolean.
        """

        # If main property 'CelebrityFaces' not found in the response, fill up return object and abort execution.
        if not response.get('CelebrityFaces'):
            self.log(self.err.UNEXPECTED_REKOGNITION_RESPONSE_STRUCTURE.aws_log + str(response))
            self.failed_return_object = self.get_failed_return_object(
                self.err.UNEXPECTED_REKOGNITION_RESPONSE_STRUCTURE, self.img_meta_data, self.get_metrics())
            return False

        # If one or more celebrities were found, store a list of dicts with essential information.
        if len(response['CelebrityFaces']) > 0:
            for celebrity in response['CelebrityFaces']:
                self.celebrities.append(Celebrity(
                    name=celebrity.get('Name', 'N.A.'),
                    celebrity_id=celebrity.get('Id', 'N.A.'),
                    bounding_box=celebrity.get('Face', {}).get('BoundingBox', {}),
                    urls=celebrity.get('Urls', [])
                ).__dict__)

        # If no celebrities were found, add one "others" celebrity object to celebrities list.
        else:
            self.celebrities.append(Celebrity(
                    name='Others',
                    celebrity_id='N.A.',
                    bounding_box={},
                    urls=[]
            ).__dict__)

        # Store image AWS' orientation recommendation into instance variable.
        self.orientation_correction = response.get('OrientationCorrection', 'N.A.')

        # Log and return successful execution.
        self.log(f'Digested "recognize_celebrities" response: {str(self.celebrities)}')
        self.log(f'Recommended orientation correction: {str(self.orientation_correction)}')
        return True
