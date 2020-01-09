import base64
from io import BytesIO
import boto3
from PIL import Image
from lib.Resources.Resources_strings_en import Strings as rsc
from lib.Helpers.Helpers import Helpers as hl
from lib.Helpers.ExifUtilities import ExifUtilities as eu
from lib.Resources.EnvironmentVariables import EnvironmentVariables as ev


class ValidationManager:

    __reko = boto3.client('rekognition')

    @classmethod
    def validate_input_fields(cls, data, request_fields):
        # Verificacao dos campos enviados no JSON de requisicao
        for x in request_fields:
            if x not in data:
                print(rsc.VALIDATION_MSG_REQUEST_INPUT_FIELDS_FAILED_DETAILS.format(str(request_fields), x))
                return False
        print(rsc.VALIDATION_MSG_REQUEST_INPUT_FIELDS_SUCCESS.format(str(request_fields)))
        return True

    @classmethod
    def validate_unique_id(cls, id):
        # Validação de Id único
        ids_list = cls.__reko.list_collections()['CollectionIds']
        if id not in ids_list:
            print(rsc.VALIDATION_MSG_ID_UNIQUENESS_UNIQUE.format(id.replace(ev.BASE_NAME+'-', '')))
            return True
        print(rsc.VALIDATION_MSG_ID_UNIQUENESS_NOT_UNIQUE.format(id.replace(ev.BASE_NAME+'-', '')))
        return False

    @classmethod
    def validate_base64_integrity(cls, image):
        # Validacao inicial da integridade do BASE64
        img_data = {}
        img_data["type"] = "invalid"
        decoded_img = ""

        try:
            decoded_img = base64.b64decode(image)
            im = Image.open(BytesIO(decoded_img))
            img_data["type"] = str(im.format)
            img_data['exif'] = eu.get_exif_data(im)
            im, decoded_img = eu.rotate_image_if_needed(im, img_data['exif'], decoded_img)
            width, height = im.size
            img_data['size'] = hl.sizeof_fmt((len(image) * 3) / 4 - image.count('=', -2), 'B')
            img_data["dimensions"] = {
                'width': width,
                'height': height
            }
            return True, img_data, decoded_img, ""
        except Exception as e:
            print(rsc.VALIDATION_MSG_BASE64_INTEGRITY_FAILED_DETAILS + ' -> ' + str(e))
            return False, img_data, decoded_img, str(e)

    @classmethod
    def validate_photo_characteristics(cls, img_bytes):
        # Validacao das caracteristicas da foto
        try:
            detect_faces_response = cls.__reko.detect_faces(
                Image={'Bytes': img_bytes},
                Attributes=['ALL']
            )
        except Exception as e:
            print(rsc.ERROR_MSG_UNABLE_TO_DECODE)
            return False, {}, rsc.ERROR_MSG_UNABLE_TO_DECODE

        number_of_faces = cls.number_faces(detect_faces_response)

        message = 'VL - Image characteristics: '

        if number_of_faces == 0:
            print(message + rsc.VALIDATION_MSG_IMG_CHAR_NO_FACES)
            return False, detect_faces_response, rsc.VALIDATION_MSG_IMG_CHAR_NO_FACES

        elif number_of_faces > 1:
            print(message + rsc.VALIDATION_MSG_IMG_CHAR_MORE_THAN_ONE_FACE)
            return False, detect_faces_response, rsc.VALIDATION_MSG_IMG_CHAR_MORE_THAN_ONE_FACE

        sharp, bright = cls.extract_image_properties(detect_faces_response)

        if sharp<0.0 or bright<0.0:
            print(message + rsc.VALIDATION_MSG_IMG_CHAR_UNACCEPTABLE_QUALITY)
            return False, detect_faces_response, rsc.VALIDATION_MSG_IMG_CHAR_UNACCEPTABLE_QUALITY

        return True, detect_faces_response, ''



    @classmethod
    def extract_image_properties(cls, data):
        # Extracao de propriedades da imagemm enviada
        return \
            data['FaceDetails'][0]['Quality']['Sharpness'], \
            data['FaceDetails'][0]['Quality']['Brightness']

    @classmethod
    def number_faces(cls, data):
        # Deteccao de numero de rostos na foto enviada
        return len(data['FaceDetails'])






