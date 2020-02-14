from io import BytesIO
import boto3


class AWSS3:
    """
    AWS S3 object, responsible for exposing the cloud's blob storage service in a unified interface.
    """

    def __init__(self, bucket: str):
        """
        Constructor function, stores instantiation provided bucket name.
        :param bucket: string containing bucket name to be worked on.
        """

        self.bucket = bucket

    def save_file(self, file_bytes: bytes, file_name: str, path: str = '') -> (bool, str, str):
        """
        Saves file provided in bytes form with given name at given file path.
        :param file_bytes: provided file in bytes form.
        :param file_name: name to be used once file is stored.
        :param path: '/' (slash) separated strings denoting the folder structure/path on which the file will be saved.
        :return: tuple with 3 values. First is a boolean expressing operation status, second value expresses
        operation details, third returns stored image size.
        """

        # Correct path spelling
        if path.split() and not path.endswith('/'): path += '/'

        # Correct image name spelling
        if file_name.startswith('/'): file_name = file_name[1:]

        key_name = f'{path}{file_name}'

        # Attempts to contact AWS S3 blob storage and save file
        try:
            bucket = boto3.resource('s3').Bucket(self.bucket)
            storage_response = bucket.put_object(Key=key_name, Body=file_bytes)

        # If unable, returns false and exposes error.
        except Exception as e:
            return False, str(e), 'N.A.'

        # Successfully finishes procedure.
        return True, str(storage_response), self.__sizeof_fmt(bucket.Object(key_name).content_length, 'B')

    def load_file_as_bytes_io(self, key: str) -> (bool, str):

        status, response, file_byte_string = self.load_file_as_string(key)
        if status:
            file_byte_string = BytesIO(file_byte_string)
        return status, response, file_byte_string

    def load_file_as_string(self, key: str) -> (bool, str):

        # Attempts to contact AWS S3 blob storage and load file.
        try:
            s3 = boto3.client('s3')
            obj = s3.get_object(Bucket=self.bucket, Key=key)
            file_byte_string = obj['Body'].read()

        # If unable, returns false and exposes error.
        except Exception as e:
            return False, str(e), None

        return True, '', file_byte_string


    @staticmethod
    def __sizeof_fmt(num, suffix='B') -> str:
        """
        Formats amount of bytes by order of magnitude.
        :param num: Number to be processed.
        :param suffix: Order of magnitude.
        :return: Formatted string.
        """

        for unit in ['', ' K', ' M', ' G', ' T', ' P', ' E', ' Z']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)
