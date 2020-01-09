import boto3
from lib.Resources.Resources_strings_en import Strings as rsc


class ReckonManager:

    __reko = boto3.client('rekognition')

    @classmethod
    def identity_check (cls, image, id):
        """
        Procedimento de checagem de correspondência entre imagem enviada e a imagem armazenada do usuário.
        :param image (bytes): Imagem a ser checada contra a que está armazenada.
        :param id (string): ID do usuário.
        :return: Tuple(A, B, C)
                A (boolean): true = operação bem sucedida, false = operação mal sucedida.
                B (string): Mensagem de status da operação.
                C (string or dict): Retorno da operação "search_faces_by_image". Caso a operação seja abortada
                                    pela validação ou pela ausência de um match entre as imagens, assumirá o valor de
                                    uma string "N.A.".
        """
        print('BL - Checking user/image correspondence...')

        threshold = 70
        maxFaces = 20

        try:
            search_faces_by_image_response = cls.__reko.search_faces_by_image(CollectionId=id,
                                                    Image={'Bytes': image},
                                                    FaceMatchThreshold=threshold,
                                                    MaxFaces=maxFaces)
        except Exception as e:
            print('BL - Unexpected "search_faces_by_image" error: ' + str(e))
            return False, rsc.ERROR_MSG_UNEXPECTED_RECOGNITION_ERROR, 'N.A.'

        if 'FaceMatches' in search_faces_by_image_response:
            faceMatches = search_faces_by_image_response['FaceMatches']
        else:
            print('BL - ' + rsc.ERROR_MSG_UNEXPECTED_SEARCH_FACES_BY_IMAGE_RESPONSE_STRUCTURE)
            return False, rsc.ERROR_MSG_UNEXPECTED_RECOGNITION_ERROR, 'N.A.'

        if len(faceMatches) == 0:
            print('BL - ' + rsc.ERROR_MSG_FACE_DOESNT_MATCH)
            return False, rsc.ERROR_MSG_FACE_DOESNT_MATCH, 'N.A.'

        match = faceMatches[0]
        message = rsc.SUCCESS_MSG_IDENTITY_CHECK\
            .format(match['Similarity'], match['Face']['Confidence'])

        print('BL - Search_faces_by_image response: ' + str(faceMatches))
        print('BL - ' + message)
        return True, message, faceMatches