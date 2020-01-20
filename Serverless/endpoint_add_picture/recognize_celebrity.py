import boto3

from interfaces.api_phase import APIPhase
from endpoint_add_picture.models.celebrity import Celebrity


class RecognizeCelebrity(APIPhase):
    """
    Celebrity recognition object, responsible for accessing AWS' celebrity recognition API with the pre-processed
    image in bytes form. Is also responsible for validating and processing the response.
    """

    def __init__(self, img_bytes: str, img_meta_data: dict,  invocation_id: str):
        """
        Constructor of the celebrity recognition object, stores provided and locally generated data, runs main object
        procedure.
        :param img_bytes: string containing pre-processed image in bytes form.
        :param img_meta_data: dictionary of image extracted meta data.
        :param invocation_id: string containing id of current cloud function invocation to be to be used by API metrics.
        """

        # Initializes APIPhase superclass parameters
        super(RecognizeCelebrity, self).__init__(prefix='RE', invocation_id=invocation_id)

        self.invocation_id = invocation_id      # :str: Current cloud function invocation id for metrics.
        self.img_bytes = img_bytes              # :str: Client provided image in bytes form.
        self.img_meta_data = img_meta_data      # :dict: Dictionary containing image meta data (including EXIF).
        self.celebrities = []                   # :list: List of Celebrity objects in dict form built from API response.
        self.orientation_correction = None      # :str: Recognition API orientation recommendation.

        self.__run()                            # Initiate recognition procedure upon instantiation.

    def __run(self):
        """
        Object's main procedure: logs current api phase, takes care of api metrics measurements, communicates with API,
        triggers evaluation and organization of response.
        :return: void.
        """

        # Start recognition time counter.
        self.start_metrics('Recognition')

        # Log recognition phase start.
        self.log(self.rsc.RECOGNITION_PHASE_START)

        # Execute request on celebrity recognition API using given image bytes
        client = boto3.client('rekognition')
        response = client.recognize_celebrities(Image={'Bytes': self.img_bytes})

        # Evaluate recognize_celebrities API response status
        if not self.__evaluate_response_status(response): return

        # Digest response if available, abort if impossible.
        if not self.__digest_response(response): return

        # Flag recognition operation as successful
        self.status = True
        self.log(self.rsc.RECOGNITION_SUCCESSFUL)

        # Stop recognition time counter.
        self.stop_metrics('Recognition')

    def __evaluate_response_status(self, response: dict) -> bool:
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
            self.log(self.rsc.RECOGNITION_RESPONSE_ACQUIRED.format(str(response)))
            return True

        # If HTTPStatusCode has failed (other than 200), fill up return object and return failure.
        else:
            error_response = self.err.FAILED_REKOGNITION_RESPONSE
            self.log(error_response.aws_log + str(response))
            self.failed_return_object = self.get_failed_return_object(error_response,
                                                                      self.img_meta_data, self.get_metrics())
            return False

    def __digest_response(self, response: dict) -> bool:
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
        self.log(self.rsc.RECOGNITION_DIGESTED_RESPONSE.format(str(self.celebrities)))
        self.log(self.rsc.RECOGNITION_ORIENTATION_RECOMMENDATION.format(str(self.orientation_correction)))
        return True
