import boto3


class AWSRekognition:
    """
    AWS Rekognition object class, responsible for exposing the cloud's face recognition service in a unified interface.
    """

    def __init__(self):
        """
        Constructor, stores given image bytes to be analyzed, API response dictionary and errors if available.
        """

        self.response = None
        self.error = None

    def recognize_celebrity(self, bucket: str, name: str) -> bool:
        """
        Main celebrity recognition procedure, attempts to contact AWS Rekognition API with provided image bytes.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Attempts to contact AWS celebrity recognition service.
        try:
            self.response = boto3.client('rekognition').recognize_celebrities(
                Image={
                    'S3Object': {
                        'Bucket': bucket,
                        'Name': name
                }})

        # Unable to contact service, abort.
        except Exception as e:
            self.error = e
            return False

        http_status_code = self.response.get('ResponseMetadata', {}).get('HTTPStatusCode')
        if not http_status_code or http_status_code != 200:
            self.error = f'Bad status code: {http_status_code}'
            return False

        return True

