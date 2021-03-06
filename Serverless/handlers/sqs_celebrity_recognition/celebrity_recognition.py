from interfaces.cloud_function_phase import CloudFunctionPhase
from services.aws_rekognition import AWSRekognition
from handlers.sqs_celebrity_recognition.models.celebrity import Celebrity


class RecognizeCelebrity(CloudFunctionPhase):
    """
    Celebrity recognition object, responsible for accessing celebrity recognition API using a file storage stored
    image. Is also responsible for validating and processing the response.
    """

    def __init__(self, bucket_name: str, file_name: str,  invocation_id: str):
        """
        Constructor of the celebrity recognition object, stores provided and locally generated data, runs main object
        procedure.
        :param bucket_name: file storage location.
        :param file_name: stored file name.
        :param invocation_id: string containing id of current cloud function invocation to be to be used by API metrics.
        """

        self.bucket_name = bucket_name                    # :str: File storage file location.
        self.file_name = file_name                        # :str: Stored file location.
        self.celebrities = []                             # :list: List of objects built from API response.
        self.orientation_correction = None                # :str: Recognition API orientation recommendation.
        self.recognition_response = None                  # :dict: Celebrity recognition API response.
        self.recognition_service = AWSRekognition()       # :AWSRekognition: Celebrity recognition API.

        # Initializes APIPhase superclass parameters and procedures
        super(RecognizeCelebrity, self).__init__(prefix='RE', phase_name='Recognition', invocation_id=invocation_id)

    def run(self) -> bool:
        """
        Object's main procedure: communicates with recognition API, evaluates and organizes response.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Execute request on celebrity recognition API using given image bytes.
        if not self.__request_celebrity_recognition(): return False

        # Digest response if available, abort if impossible.
        if not self.__digest_response(self.recognition_response): return False

        # Procedure successful
        return True

    def __request_celebrity_recognition(self) -> bool:
        """
        Executes request on celebrity recognition API.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Attempts to contact celebrity recognition service
        if self.recognition_service.recognize_celebrity(self.env.BUCKET_NAME, self.file_name):
            self.recognition_response = self.recognition_service.response
            self.log(self.rsc.RECOGNITION_API_CONTACTED)
            return True

        # If unable, fill failed return object and abort.
        else:
            error_response = self.err.FAILED_REKOGNITION_REQUEST
            self.log(error_response.aws_log.format(str(self.recognition_service.error)))
            self.failed_return_object = self.get_failed_return_object(error_response, {}, self.get_metrics())
            return False

    def __digest_response(self, response: dict) -> bool:
        """
        Translate recognition API response structure to project's (Celebrity objects list).
        :param response: Dictionary containing recognition API's response.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # If main property 'CelebrityFaces' not found in the response, fill up return object and abort execution.
        if not response.get('CelebrityFaces'):
            error_response = self.err.UNEXPECTED_REKOGNITION_RESPONSE_STRUCTURE
            self.log(error_response.aws_log + str(response))
            self.failed_return_object = self.get_failed_return_object(error_response, {}, self.get_metrics())
            return False

        # If one or more celebrities were found, store a list of dicts with essential information.
        if len(response['CelebrityFaces']) > 0:
            for celebrity in response['CelebrityFaces']:
                self.celebrities.append(Celebrity(
                    name=celebrity.get('Name', 'N.A.'),
                    recognition_id=celebrity.get('Id', 'N.A.'),
                    bounding_box=celebrity.get('Face', {}).get('BoundingBox', {}),
                    urls=celebrity.get('Urls', [])
                ).__dict__)

        # If no celebrities were found, add one "others" celebrity object to celebrities list.
        else:
            self.celebrities.append(Celebrity(
                    name='Others',
                    recognition_id='N.A.',
                    bounding_box={},
                    urls=[]
            ).__dict__)

        # Store image AWS' orientation recommendation into instance variable.
        self.orientation_correction = response.get('OrientationCorrection', 'N.A.')

        # Log and return successful execution.
        self.log(self.rsc.RECOGNITION_DIGESTED_RESPONSE.format(str(self.celebrities)))
        self.log(self.rsc.RECOGNITION_ORIENTATION_RECOMMENDATION.format(str(self.orientation_correction)))
        return True
