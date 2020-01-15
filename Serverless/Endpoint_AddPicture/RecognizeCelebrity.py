import boto3

from Endpoint_AddPicture.Models.Celebrity import Celebrity
from Utilities.Helpers.ApiMetrics import ApiMetrics
from Utilities.Helpers.Helpers import Helpers as hl


class RecognizeCelebrity:

    def __init__(self, img_bytes: str, img_meta_data: dict,  api_metrics: ApiMetrics):
        """
        Constructor of the celebrity recognition object, responsible for accessing AWS celebrity recognition API with
        the user provided image in bytes form. Is also responsible for validating and processing the response.
        :param img_bytes: string containing client provided image in bytes form
        :param img_meta_data: dictionary of image extracted meta data.
        :param api_metrics: ApiMetrics object, responsible for performance measuring.
        """

        self.img_bytes = img_bytes                  # :str: Client provided image in bytes form.
        self.img_meta_data = img_meta_data          # :dict: Dictionary containing image meta data (including EXIF)
        self.celebrities = []                       # :list: List of Celebrity objects built from API response.
        self.orientation_correction = None          # :str: Recognition API orientation recomendation

        self.recognition_status = False             # :boolean: Flag to expose recognition status failed or successful.
        self.failed_return_object = {}              # :dict: Exposes failure return object in case of failure
        self.api_metrics = api_metrics              # :ApiMetrics: Stores metrics object responsible time measurements.

        self.__recognize_celebrity()                # Initiate validation procedure

    def __recognize_celebrity(self):
        """
        Object's main function/procedure: communicates with API, triggers evaluation and organization of response.
        :return: void.
        """

        # Start recognition time counter.
        self.api_metrics.start_time('Recognition')

        # Execute celebrity recognition API on given image bytes
        client = boto3.client('rekognition')
        response = client.recognize_celebrities(Image={'Bytes': self.img_bytes})

        # Evaluate recognize_celebrities API response status
        if not self.__evaluate_response_status(response): return

        # Digest response if available, abort if impossible.
        if not self.__digest_response(response): return

        # Flag recognition operation as successful
        self.recognition_status = True

        # Stop recognition time counter.
        self.api_metrics.stop_time('Recognition')

    def __evaluate_response_status(self, response: dict):
        """
        Evaluates response object integrity and status.
        :param response: Dictionary containing recognition API's response.
        :return: boolean.
        """

        # If HTTPStatusCode is not available in response dictionary, abort execution.
        if not response.get('ResponseMetadata', {}).get('HTTPStatusCode'):
            print(f'BL - ERROR: "recognize_celebrities" response structure has changed: {str(response)}')
            self.failed_return_object = hl.get_return_object(
                status_code=400,
                response_code=0,
                msg_dev='"recognize_celebrities" API response structure has changed.',
                msg_user='Unable to complete celebrity recognition.',
                img_meta_data=self.img_meta_data,
                api_metrics=self.api_metrics.get()
            )
            return False

        # If HTTPStatusCode is successful (200), return success.
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print(f'BL - Successfully acquired "recognize_celebrities" response: {str(response)}')
            return True

        # If HTTPStatusCode has failed (other than 200), fill up return object and return failure.
        else:
            print(f'BL - ERROR: Unable to acquire successful "recognize_celebrities" response: {str(response)}')
            self.failed_return_object = hl.get_return_object(
                status_code=400,
                response_code=0,
                msg_dev='Unable to contact "recognize_celebrities" API.',
                msg_user='Unable to complete celebrity recognition.',
                img_meta_data=self.img_meta_data,
                api_metrics=self.api_metrics.get()
            )
            return False

    def __digest_response(self, response: dict):
        """
        Translate recognition API response structure to project's (Celebrity objects list).
        :param response: Dictionary containing recognition API's response.
        :return: boolean.
        """

        # If main property 'CelebrityFaces' not found in the response, abort execution.
        if not response.get('CelebrityFaces'):
            print(f'BL - ERROR: Unable to digest "recognize_celebrities" response. Structure might have changed.')
            self.failed_return_object = hl.get_return_object(
                status_code=400,
                response_code=0,
                msg_dev='Unable to digest "recognize_celebrities" response.',
                msg_user='Unable to complete celebrity recognition. Please try again.',
                img_meta_data=self.img_meta_data,
                api_metrics=self.api_metrics.get()
            )
            return False

        # If one or more celebrities were found, make a list of dicts with essential information.
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

        # Store image orientation recommendation from AWS into instance variable.
        self.orientation_correction = response.get('OrientationCorrection', 'N.A.')

        # Log and return successful execution.
        print(f'BL - Digested "recognize_celebrities" response: {str(self.celebrities)}')
        print(f'BL - Recommended orientation correction: {str(self.orientation_correction)}')
        return True
