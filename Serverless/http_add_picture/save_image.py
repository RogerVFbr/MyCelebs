from interfaces.api_phase import APIPhase
from services.aws_s3_dao import AWSS3


class SaveImage(APIPhase):
    """
    Image saving object, responsible for preparing the file storage structure, accessing the blob storage API,
    and evaluating the response.
    """

    def __init__(self, img_bytes: bytes,  img_ext: str, invocation_id: str):
        """
        Constructor of the save image object, stores provided and locally generated data, runs main object
        procedure.
        :param img_bytes: pre-processed image in bytes form.
        :param img_ext: string containing image extension (type).
        :param invocation_id: string containing id of current cloud function invocation to be to be used by API metrics.
        """

        self.img_bytes = img_bytes                      # :str: Client provided image in bytes form.
        self.img_ext = img_ext                          # :str: Image type/extension.
        self.file_name = None                            # :str: Stored image final name.
        self.img_size = None                            # :str: Stored image size.
        self.public_url = None                          # :str: Public image url.
        self.repository = AWSS3(self.env.BUCKET_NAME)   # :AWSS3: File repository.

        # Initializes APIPhase superclass parameters and procedures
        super(SaveImage, self).__init__(prefix='SI', phase_name='Save image', invocation_id=invocation_id)

    def run(self) -> bool:
        """
        Object's main procedure: executes image saving DAO and evaluates response.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Build stored image name.
        self.file_name = f'{self.invocation_id}.{self.img_ext}'

        # Execute request on image saving infrastructure, abort if impossible.
        if not self.__save_image(): return False

        # Build public image url
        self.public_url = f'{self.env.PUBLIC_IMG_BASE_ADDRESS}{self.file_name}'
        self.log(self.rsc.IMAGE_SAVE_PUBLIC_URL.format(self.public_url))

        # Procedure successful
        return True

    def __save_image(self) -> bool:
        """
        Attempts to save image on blob storage.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Attempts to save file to repository
        status, response, self.img_size = self.repository.save_file(self.img_bytes, self.file_name)

        # If unable to save image, fill up return object and abort.
        if not status:
            error_response = self.err.UNABLE_TO_CONTACT_BLOB_STORAGE_API
            self.log(error_response.aws_log.format(response))
            self.failed_return_object = self.get_failed_return_object(error_response, {}, self.get_metrics())
            return False

        # Procedure successful
        self.log(self.rsc.IMAGE_SAVE_API_CONTACTED.format(self.img_size, response))
        return True

