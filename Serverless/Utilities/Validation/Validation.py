import io, base64
from PIL import Image

from Utilities.Helpers.Helpers import Helpers as hl
from Utilities.Helpers.ExifUtilities import ExifUtilities as eu
from Resources.Resources_strings_en import Strings as rsc
from Utilities.Helpers.ApiMetrics import ApiMetrics


class Validation:

    def __init__(self, event, metrics: ApiMetrics):
        """
        Constructor of the Validation object, responsible for treating and exposing data retrieved from the
        request object.
        :param event: AWS event object
        :param metrics: ApiMetrics object, responsible for performance measuring.
        """

        self.event = event                # :dict: AWS Event object.
        self.img_name = 'N.A.'            # :str: User provided name.
        self.img_desc = 'N.A.'            # :str: User provided image description.
        self.img_base64 = None            # :str: BASE64 encoded string, containing image in original payload form.
        self.img_bytes = None             # :bytes Image in bytes form, product of base64.b64decode()
        self.img_bytesIO = None           # :bytesIO: Image in bytesIO form, to produce a Pillow Image
        self.img_pillow = None            # :Image: Pillow Image object (rotation, exif)
        self.img_meta_data = {
            'type': 'N.A.',               # :str: Image type (JPG, PNG) 
            'size': 'N.A.',               # :str: Image size in KB
            'height': 'N.A.',             # :int: Image height in pixels
            'width': 'N.A.',              # :int: Image width in pixels (ind)
            'exif': 'N.A.'                # :dict: or :str: Dictionary containing exif information if available
        }

        self.validation_status = False    # :bool: Flag to expose validation status failed or successful.
        self.failed_return_object = {}    # :dict: Exposes fail return object in case of failure
        self.api_metrics = metrics        # :ApiMetrics: Stores metrics object responsible time measurements.
        
        self.__validate_request_object()  # Initiate validation process

    def __validate_request_object(self):
        """
        Validates, decodes and extracts information from request object.
        :param event: Request object.
        :return: void.
        """

        # Start validation time counter.
        self.api_metrics.start_time('Validation')

        # Extract information from request object.
        if not self.__extract_info_from_body():
            self.failed_return_object = hl.get_return_object(
                status_code=400,
                response_code=0,
                msg_dev='Invalid JSON content.',
                msg_user='Unable to work with given information.',
                img_meta_data=self.img_meta_data,
                api_metrics=self.api_metrics.get()
            )
            print(rsc.VALIDATION_MSG_REQUEST_INPUT_FIELDS_FAILED)
            return

        # Decode BASE64 to desired formats.
        if not self.__decode_base64_image():
            self.failed_return_object = hl.get_return_object(
                status_code=400,
                response_code=0,
                msg_dev='Invalid BASE64.',
                msg_user='Unable to decode sent file.',
                img_meta_data=self.img_meta_data,
                api_metrics=self.api_metrics.get()
            )
            print(rsc.VALIDATION_MSG_BASE64_INTEGRITY_FAILED)
            return

        # Extract EXIF data if available.
        self.img_meta_data['exif'] = eu.get_exif_data(self.img_pillow)

        # Correct EXIF orientation if possible/needed.
        exif = self.img_meta_data['exif']
        if isinstance(exif, dict) and 'Orientation' in exif and isinstance(exif['Orientation'], int):
            self.__rotate_image_if_needed(exif['Orientation'])

        # Stop validation time counter.
        self.api_metrics.stop_time('Validation')

        # Flag and log validation status as successful (true).
        self.validation_status = True
        print(rsc.VALIDATION_MSG_SUCCESS)

        # Finish validation execution.
        return

    def __extract_info_from_body(self):
        """
        Double checks request object's fields and content existence and copies values to instance variables.
        :return: boolean.
        """

        # Attempts to extract information from newly acquired request object.
        event = self.event
        img_name = event.get('img_name')
        img_desc = event.get('img_desc')
        img_base64 = event.get('image')

        # If successful, assigns values to instance variables.
        if isinstance(img_name, str) and img_name.strip(): self.img_name = img_name.strip()
        if isinstance(img_desc, str) and img_desc.strip(): self.img_desc = img_desc.strip()

        # Checks for existence of BASE64 string, if unsuccessful, abort.
        if not img_base64: return False

        # Assigns BASE64 string to instance variable.
        self.img_base64 = img_base64

        # Process completed successfully, returns true.
        return True;

    def __decode_base64_image(self):
        """
        Decodes BASE64 string into needed image formats.
        :return: boolean.
        """

        try:
            # Decodes BASE64 string into bytes.
            self.img_bytes = base64.b64decode(self.img_base64)

            # Decodes bytes into BytesIO object.
            self.img_bytesIO = io.BytesIO(self.img_bytes)

            # Converts BytesIO object to Pillow object.
            self.img_pillow = Image.open(self.img_bytesIO)

            # Extracts metadata from given results.
            self.img_meta_data['type'] = str(self.img_pillow.format)
            self.img_meta_data['width'], self.img_meta_data['height'] = self.img_pillow.size
            self.img_meta_data['size'] = hl.sizeof_fmt((len(self.img_base64) * 3) / 4 -
                                                       self.img_base64.count('=', -2), 'B')
            return True

        except Exception as e:
            print(rsc.VALIDATION_MSG_BASE64_INTEGRITY_FAILED_DETAILS + ' -> ' + str(e))
            return False

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
        print(f"VL - Image orientation mismatch type {orientation} detected. "
              f"Rotating image by {rotation} degrees counter-clockwise to compensate.")
        new_image = self.img_pillow.rotate(rotation, expand=1)

        # Consolidates rotation into memory, abort if unsuccessful.
        try:
            bytesIO = io.BytesIO()
            new_image.save(bytesIO, format=self.img_meta_data['type'])
        except Exception as e:
            print('VL - Could not update image bytes with newly rotated image: ' + str(e))
            return

        # Updates instance variables with new values.
        self.img_pillow = new_image
        self.img_bytesIO = bytesIO.getvalue()
        self.img_meta_data['width'], self.img_meta_data['height'] = new_image.size
        print('VL - Successfully updated image bytes with newly rotated image.')




