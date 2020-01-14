import boto3

from Endpoint_AddPicture.Models.Celebrity import Celebrity
from Utilities.Helpers.ApiMetrics import ApiMetrics
from Utilities.Helpers.Helpers import Helpers as hl


class RecognizeCelebrity:

    def __init__(self, img_bytes: str, img_meta_data: dict,  api_metrics: ApiMetrics):
        self.img_bytes = img_bytes
        self.img_meta_data = img_meta_data
        self.celebrities = []
        self.orientation_correction = None
        self.recognition_status = False
        self.failed_return_object = {}
        self.api_metrics = api_metrics

        self.__recognize_celebrity()

    def __recognize_celebrity(self):
        """

        :return: void
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

        :param response:
        :return:
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

        :param response:
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

        # If any celebrities could be found, make a list of dicts with essential information.
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

        # Store orientation recommendation from AWS into instance variable.
        self.orientation_correction = response.get('OrientationCorrection', 'N.A.')

        # Log and return successful execution.
        print(f'BL - Digested "recognize_celebrities" response: {str(self.celebrities)}')
        print(f'BL - Recommended orientation correction: {str(self.orientation_correction)}')
        return True
