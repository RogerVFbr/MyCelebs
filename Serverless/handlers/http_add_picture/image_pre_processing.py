import io

from PIL import Image

from handlers.http_add_picture.models.img_meta_data import ImgMetaData
from interfaces.api_phase import APIPhase
from handlers.http_add_picture.exif_utilities import ExifUtilities as eu


class ImagePreProcessing(APIPhase):
    """
    Image pre-processing object, responsible for converting image to required Pillow Image format, performing
    any processing required, extracting and exposing resulting meta data.
    """

    def __init__(self, img_bytes: bytes, invocation_id: str):
        """
        Constructor of the Image pre-processing object, stores provided and locally generated data, runs main object
        procedure.
        :param img_bytes: validation provided image in bytes form.
        :param invocation_id: string containing id of current cloud function invocation to be to be used by API metrics.
        """

        self.img_bytes = img_bytes           # :bytes: Image in bytes form, product of base64.b64decode().
        self.img_pillow = None               # :Image: Pillow Image object (rotation, exif).
        self.img_meta_data = ImgMetaData(
            type='N.A.',                     # :str: Image type (JPG, PNG).
            size='N.A.',                     # :str: Image size in KB.
            height=0,                        # :int: Image height in pixels.
            width=0,                         # :int: Image width in pixels.
            exif={}                          # :dict: Dictionary containing exif information if available.
        )

        # Initializes APIPhase superclass parameters and procedures
        super(ImagePreProcessing, self).__init__(prefix='PP', phase_name='Pre-processing', invocation_id=invocation_id)

    def run(self) -> bool:
        """
        Object's main procedure: creates Pillow Image object, rotates image based on EXIF orientation (if available)
        and extracts image meta data.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Creates Pillow Image Object, abort if impossible.
        if not self.__convert_image_bytes_to_pillow(): return False

        # Corrects image orientation based on EXIF data if possible and needed.
        self.__rotate_image_if_needed()

        # Updates image metadata instance variables.
        self.__update_meta_data()

        # Procedure successful
        return True

    def __convert_image_bytes_to_pillow(self) -> bool:
        """
        Attempts to convert provided image in bytes form to business logic required Pillow Image format.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Attempts to create a Pillow Image object from given image bytes.
        try:
            self.img_pillow = Image.open(io.BytesIO(self.img_bytes))

        # Unable to decode image bytes, build failed return object and abort execution.
        except Exception as e:
            error_response = self.err.UNDECODABLE_IMAGE_BYTES
            self.log(error_response.aws_log.format(str(e)))
            self.failed_return_object = self.get_failed_return_object(error_response, {}, self.get_metrics())
            return False

        # Successfully built Pillow Image object, log and return.
        self.log(self.rsc.PRE_PROC_CREATED_PILLOW_OBJECT)
        return True

    def __rotate_image_if_needed(self):
        """
        Checks and compensates for EXIF orientation mismatch if available and needed.
        :param orientation: int. Expresses the EXIF Orientation type.
        :return: void.
        """

        # Attempts to extract EXIF data fro Pillow Image object
        orientation = eu.get_exif_data(self.img_pillow).get('Orientation')
        if not orientation:
            self.log(self.rsc.PRE_PROC_NO_EXIF_ORIENTATION)
            return

        # Checks orientation and calculates rotation accordingly.
        if   orientation == 3 or orientation == 4: rotation = 180
        elif orientation == 5 or orientation == 6: rotation = 270
        elif orientation == 7 or orientation == 8: rotation = 90
        else:
            self.log(self.rsc.PRE_PROC_NO_ROTATION_NEEDED.format(orientation))
            return

        # If EXIF orientation is detected, rotate accordingly.
        self.log(self.rsc.PRE_PROC_ORIENTATION_MISMATCH_DETECTED.format(orientation, rotation))
        new_image = self.img_pillow.rotate(rotation, expand=1)

        # Consolidates rotation into memory, abort if unsuccessful.
        try:
            self.bytes_io = io.BytesIO()
            new_image.save(self.bytes_io, format=self.img_pillow.format)
        except Exception as e:
            self.log(self.rsc.PRE_PROC_UNABLE_TO_UPDATE_BYTES.format(str(e)))
            return

        # Updates instance variables with new values.
        self.img_pillow = new_image
        self.img_bytes = self.bytes_io.getvalue()

        # Log successful image rotation.
        self.log(self.rsc.PRE_PROC_SUCCESSFULLY_ROTATED)

    def __update_meta_data(self):
        """
        Updates instance meta data dictionary with finalized, pre-processed image meta data.
        :return: void.
        """

        # Extracts metadata from final image.
        self.img_meta_data.type = str(self.img_pillow.format)
        self.img_meta_data.width, self.img_meta_data.height = self.img_pillow.size

        # Updates EXIF data if available.
        self.img_meta_data.exif = eu.get_exif_data(self.img_pillow)

        # Logs acquired meta data
        self.log(self.rsc.RECOGNITION_ACQUIRED_META_DATA.format(str(self.img_meta_data.__dict__)))


