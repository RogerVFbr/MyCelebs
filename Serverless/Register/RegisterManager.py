import boto3
from lib.Resources.Resources_strings_en import Strings as rsc
from lib.Resources.EnvironmentVariables import EnvironmentVariables as ev


class RegisterManager:

    __reko = boto3.client('rekognition')

    @classmethod
    def register_new_user_on_own_collection(cls, image, id, faceId):
        """
        Procedimento de inicialização de uma nova coleção. Utiliza o ID do usuário como CollectionId para criar
        nova coleção e indexa a imagem a ela, retornando atributos detectados.
        :param image (Bytes): Imagem recebida em formato Bytes.
        :param id (string): ID do novo usuário.
        :return: Tuple(A, B)
                A (boolean): true = operação bem sucedida, false = operação mal sucedida.
                B (string): Mensagem de status da operação.
        """
        print('BL - Attempting to register new user on own collection...')
        try:
            print('BL - Creating collection for new Id...')
            cls.__reko.create_collection(CollectionId=id)
            print('BL - Indexing face to new collection...')
            index_faces_response = cls.__reko.index_faces(
                CollectionId=id,
                Image={'Bytes': image},
                ExternalImageId=faceId,
                DetectionAttributes=['ALL']
            )
            print('BL - Index_faces response: ' + str(index_faces_response))
        except Exception as e:
            print('BL - ' + rsc.ERROR_MSG_FAILED_TO_REGISTER + ': ' + str(e))
            return False, rsc.ERROR_MSG_FAILED_TO_REGISTER + ': ' + str(e), 'N.A.'
        print('BL - ' + rsc.SUCCESS_MSG_REGISTRATION.format(id))

        return True, rsc.SUCCESS_MSG_REGISTRATION.format(id.replace(ev.BASE_NAME+'-', '')), index_faces_response

    @classmethod
    def register_new_user_on_global_collection(cls, image, id):
        if not cls.__check_global_collection_existence():
            if not cls.__create_global_collection():
                return False, rsc.ERROR_MSG_FAILED_TO_REGISTER + ': Unable to create global collection.', 'N.A.'

        status, index_faces = cls.__register_on_global_collection(id, image)

        if not status:
            return False, rsc.ERROR_MSG_FAILED_TO_REGISTER + ': Unable to register user on global collection.', 'N.A.'

        return True, rsc.SUCCESS_MSG_REGISTRATION.format(id.replace(ev.BASE_NAME+'-', '')), index_faces

    @classmethod
    def __check_global_collection_existence(cls):
        collections_response = cls.__reko.list_collections(MaxResults=100)
        collectionIds = collections_response['CollectionIds']

        while True:
            if 'NextToken' in collections_response:
                nextToken = collections_response['NextToken']
                collections_response = cls.__reko.list_collections(NextToken=nextToken, MaxResults=100)
                collectionIds = collectionIds + collections_response['CollectionIds']
            else:
                break

        if ev.GLOBAL_COLLECTIONS_NAME in collectionIds:
            print(f'BL - Global collection found for this stage.')
            return True

        else:
            print('BL - Global collection for this stage has not been found. Creating...')
            return False

    @classmethod
    def __create_global_collection(cls):
        try:
            cls.__reko.create_collection(CollectionId=ev.GLOBAL_COLLECTIONS_NAME)
            print(f"BL - Successfully created new global collection for this stage under ID: '{ev.GLOBAL_COLLECTIONS_NAME}'.")
            return True
        except Exception as e:
            print(f"BL - Failed to create global collection for this stage under ID: '{ev.GLOBAL_COLLECTIONS_NAME}'.")
            return False

    @classmethod
    def __register_on_global_collection(cls, id, image):
        print("BL - Attempting to register new user on stage's global collection...")
        try:
            index_faces_response = cls.__reko.index_faces(
                CollectionId=ev.GLOBAL_COLLECTIONS_NAME,
                Image={'Bytes': image},
                ExternalImageId=id
            )
            print('BL - Index_faces response: ' + str(index_faces_response))
            if len(index_faces_response) == 0:
                print("BL - Failed to register new user on stage's global collection, no faces found.")
                return False, 'N.A.'
        except Exception as e:
            print("BL - Failed to register new user on stage's global collection: " + str(e))
            return False, 'N.A.'

        print(f"BL - Successfully registered new user on stage's global collection. ExternalImageId: '{id}' | "
              f"FaceId: '{index_faces_response.get('FaceRecords')[0].get('Face').get('FaceId')}'.")

        faces_response = cls.__reko.list_faces(CollectionId=ev.GLOBAL_COLLECTIONS_NAME, MaxResults=100)
        # print('Faces: ' + str(faces_response))
        global_faces = [{'ExternalImageId': x['ExternalImageId'], 'FaceId': x['FaceId']} for x
                        in faces_response['Faces']]
        while True:
            if 'NextToken' in faces_response:
                nextToken = faces_response['NextToken']
                faces_response = cls.__reko.list_faces(CollectionId=ev.GLOBAL_COLLECTIONS_NAME, NextToken=nextToken,
                                                 MaxResults=100)
                global_faces = global_faces + [{'ExternalImageId': x['ExternalImageId'], 'FaceId': x['FaceId']} for x
                                               in faces_response['Faces']]
            else:
                break

        print(f"BL - Stage's global collection contains now {len(global_faces)} face(s): {global_faces}")

        return True, index_faces_response








