import io
from PIL import Image

from interfaces.api_phase import APIPhase
from endpoint_add_picture.exif_utilities import ExifUtilities as eu


class ImagePreProcessing(APIPhase):

    def __init__(self, img_bytes: bytes, invocation_id: str):
        """
        Constructor of the Validation object, responsible for validating, pre-processing and exposing
        data retrieved from the client sent request object.
        :param event: AWS event dictionary.
        :param metrics: ApiMetrics object, responsible for performance measuring.
        """

        # Initializes APIPhase superclass parameters
        super(ImagePreProcessing, self).__init__(prefix='PP')

        self.img_bytes = img_bytes           # :bytes: Image in bytes form, product of base64.b64decode().
        self.img_pillow = None               # :Image: Pillow Image object (rotation, exif).
        self.img_size = None
        self.img_meta_data = {
            'type': 'N.A.',                 # :str: Image type (JPG, PNG).
            'size': 'N.A.',                 # :str: Image size in KB.
            'height': 'N.A.',               # :int: Image height in pixels.
            'width': 'N.A.',                # :int: Image width in pixels.
            'exif': {}                      # :dict: Dictionary containing exif information if available.
        }
        self.invocation_id = self.get_id(invocation_id)

        self.__execute()                     # Initiate validation procedure upon instantiation.

    def __execute(self):
        """
        Object's main procedure: validates, decodes and extracts information from request object.
        :return: void.
        """

        # Start pre-processing time counter.
        self.start_metrics('Pre-processing')

        # Log pre-processing phase start.
        self.log(self.rsc.VALIDATION_PHASE_START)

        # Create Pillow Image Object, abort if impossible.
        if not self.__convert_image_bytes_to_pillow(): return

        # Extract EXIF data if available.
        self.img_meta_data['exif'] = eu.get_exif_data(self.img_pillow)

        # Correct image orientation based on EXIF data if possible and needed.
        exif = self.img_meta_data['exif']
        if isinstance(exif, dict) and 'Orientation' in exif and isinstance(exif['Orientation'], int):
            self.__rotate_image_if_needed(exif['Orientation'])

        # Update image metadata instance variables.
        self.__update_meta_data()

        # Flag and log pre-processing status as successful (true).
        self.status = True
        self.log('Image pre-processing concluded successfully.')

        # Stop pre-processing time counter.
        self.stop_metrics('Pre-processing')

    def __convert_image_bytes_to_pillow(self):

        try:
            self.img_pillow = Image.open(io.BytesIO(self.img_bytes))

        except Exception as e:
            # Unable to decode BASE64 image string, build failed return object and abort execution.
            error_response = self.err.UNDECODABLE_BASE64_STRING
            self.log(error_response.aws_log.format(str(e)))
            self.failed_return_object = self.get_failed_return_object(error_response, {}, self.get_metrics())
            return False

        self.log('Created Pillow Image object.')
        return True

    def __rotate_image_if_needed(self, orientation: int):
        """
        Checks and compensates for EXIF orientation mismatch.
        :param orientation: int
        :return: void.
        """

        # Checks orientation and calculates rotation accordingly.
        if   orientation == 3 or orientation == 4: rotation = 180
        elif orientation == 5 or orientation == 6: rotation = 270
        elif orientation == 7 or orientation == 8: rotation = 90
        else: return

        # If EXIF orientation is detected, rotate accordingly.
        self.log(f"Image orientation mismatch type {orientation} detected. "
              f"Rotating image by {rotation} degrees counter-clockwise to compensate.")
        new_image = self.img_pillow.rotate(rotation, expand=1)

        # Consolidates rotation into memory, abort if unsuccessful.
        try:
            bytesIO = io.BytesIO()
            new_image.save(bytesIO, format=self.img_meta_data['type'])
        except Exception as e:
            self.log.log('Could not update image bytes with newly rotated image: ' + str(e))
            return

        # Updates instance variables with new values.
        self.img_pillow = new_image
        self.img_bytes = bytesIO.getvalue()
        self.img_size = bytesIO.tell()

        self.log('Successfully updated image bytes with newly rotated image.')

    def __update_meta_data(self):

        # Extracts metadata from final image.
        self.img_meta_data['type'] = str(self.img_pillow.format)
        self.img_meta_data['width'], self.img_meta_data['height'] = self.img_pillow.size
        self.img_meta_data['size'] = self.__sizeof_fmt(self.img_size, 'B')

        # Updates EXIF data if available.
        self.img_meta_data['exif'] = eu.get_exif_data(self.img_pillow)

    @staticmethod
    def __sizeof_fmt(num, suffix='B'):
        """
        Formats amount of bytes by order of magnitude
        :param num: Number to be processed.
        :param suffix: Order of magnitude.
        :return: Formatted string.
        """

        for unit in ['', ' K', ' M', ' G', ' T', ' P', ' E', ' Z']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)
