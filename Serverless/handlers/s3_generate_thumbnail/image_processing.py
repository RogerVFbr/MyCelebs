from io import BytesIO
from PIL import Image

from interfaces.api_phase import APIPhase


class ImageProcessing(APIPhase):
    """
    Image processing object, responsible for converting image to required Pillow Image format and performing
    any processing required.
    """

    def __init__(self, img_bytes_io: BytesIO, invocation_id: str):
        """
        Constructor of the image processing object, stores provided and locally generated data, runs main object
        procedure.
        :param img_bytes_io: validation provided image in BytesIO form.
        :param invocation_id: string containing id of current cloud function invocation to be to be used by API metrics.
        """

        self.img_bytes_io = img_bytes_io           # :bytes: Image in bytes form, product of base64.b64decode().
        self.img_pillow = None                     # :Image: Pillow Image object.
        self.img_bytes = None
        self.img_ext = None
        self.thmb_size = (128, 128)

        # Initializes APIPhase superclass parameters and procedures
        super(ImageProcessing, self).__init__(prefix='PI', phase_name='Pre-processing', invocation_id=invocation_id)

    def run(self) -> bool:
        """
        Object's main procedure: creates Pillow Image object, rotates image based on EXIF orientation (if available)
        and extracts image meta data.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Creates Pillow Image Object, aborts if impossible.
        if not self.__convert_image_bytes_io_to_pillow(): return False

        # Generates thumbnail from given image, aborts if impossible.
        if not self.__generate_thumbnail(): return False

        # Procedure successful
        return True

    def __convert_image_bytes_io_to_pillow(self) -> bool:
        """
        Attempts to convert provided image in bytes form to business logic required Pillow Image format.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Attempts to create a Pillow Image object from given image bytes.
        try:
            self.img_pillow = Image.open(self.img_bytes_io)

        # Unable to decode image bytes, build failed return object and abort execution.
        except Exception as e:
            error_response = self.err.UNDECODABLE_IMAGE_BYTES
            self.log(error_response.aws_log.format(str(e)))
            return False

        # Successfully built Pillow Image object, log and return.
        self.log(self.rsc.PRE_PROC_CREATED_PILLOW_OBJECT)
        return True

    def __generate_thumbnail(self) -> bool:
        try:
            width, height = self.img_pillow.size
            self.img_ext = self.img_pillow.format
            self.img_pillow.thumbnail(self.thmb_size)
            bytes_io = BytesIO()
            self.img_pillow.save(bytes_io, format=self.img_ext)
            self.img_bytes = bytes_io.getvalue()
        except Exception as e:
            self.log(self.rsc.PROC_UNABLE_TO_GENERATE_TUMBNAIL.format(str(e)))
            return False

        self.log(self.rsc.PROC_SUCCESSFULLY_GENERATED_TUMBNAIL.format(self.thmb_size[0], self.thmb_size[1],
                                                                      width, height))
        return True
