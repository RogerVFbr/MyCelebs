import boto3


class AWSS3:

    def __init__(self, bucket):
        self.bucket = bucket

    def save_file(self, img_bytes: bytes, img_name: str, path: str = '') -> (bool, str):

        # Correct path spelling
        if path.split() and not path.endswith('/'): path += '/'

        # Correct image name spelling
        if img_name.startswith('/'): img_name = img_name[1:]

        # Attempts to contact AWS S3 blob storage and save file
        try:
            bucket = boto3.resource('s3').Bucket(self.env.BUCKET_NAME)
            storage_response = bucket.put_object(Key=f'{path}{img_name}', Body=img_bytes)
            return True, storage_response

        # If unable, returns false and exposes error.
        except Exception as e:
            return False, str(e)