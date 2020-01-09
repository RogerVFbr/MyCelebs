import boto3
from lib.Resources.Resources_strings_en import Strings as rsc
from lib.Resources.EnvironmentVariables import EnvironmentVariables as ev
from botocore.exceptions import ClientError
from lib.Dao.Dao import Dao as dao


class DeleteManager:

    __reko = boto3.client('rekognition')

    @classmethod
    def delete_identity_on_own_colletion(cls, id):
        """
        Procedimento de deleção de um usuário registrado.
        :param id (string): ID do usuário a ser deletado.
        :return: Tuple(A, B)
                A (boolean): true = operação bem sucedida, false = operação mal sucedida.
                B (string): Mensagem de status da operação.
        """
        print('BL - Attempting to delete user by deleting own collection...')
        try:
            cls.__reko.delete_collection(CollectionId=id)
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                message = rsc.ERROR_MSG_UNKNOWN_ID.format(id.replace(ev.BASE_NAME+'-', ''))
            else:
                message = str(e.response['Error']['Message'])
            print('BL - ' + message)
            return False, message
        message = rsc.SUCCESS_MSG_DELETE.format(id.replace(ev.BASE_NAME+'-', ''))
        print('BL - Successfully deleted user related collection.')
        return True, message

    @classmethod
    def delete_identity_on_global_collection(cls, id):
        print(f"BL - Attempting to delete user '{id}' from stage's global collection...")

        response = cls.__reko.list_faces(CollectionId=id, MaxResults=100)
        user_faces = [x.get('ExternalImageId') for x in response['Faces']]

        while True:
            if 'NextToken' in response:
                nextToken = response['NextToken']
                response = cls.__reko.list_faces(CollectionId=id, NextToken=nextToken, MaxResults=100)
                user_faces = user_faces + [x.get('ExternalImageId') for x in response['Faces']]
            else:
                break

        print(f"BL - User's own collection contains {len(user_faces)} face(s): {str(user_faces)}")

        try:
            response = cls.__reko.delete_faces(
                CollectionId=ev.GLOBAL_COLLECTIONS_NAME,
                FaceIds=user_faces
            )
        except Exception as e:
            print(f"BL - Error: unable to delete user '{str(id)}' from stage's global collection: " + str(e))
            return False, "Unable to delete user from stage's global collection."

        if 'DeletedFaces' in response and set(user_faces) == set(response['DeletedFaces']):
            print(f"BL - Successfully deleted all faces related to user '{str(id)}' from stage's global collection.")
        else:
            print(f"BL - Error: unable to confirm user '{str(id)}' related faces deletion from stage's global collection.")
            return False, "Unable to delete user from stage's global collection."

        faces_response = cls.__reko.list_faces(CollectionId=ev.GLOBAL_COLLECTIONS_NAME, MaxResults=100)
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

        unique_faces_count = len(set([x.get('ExternalImageId') for x in global_faces]))

        print(f"BL - Stage's global collection contains now {len(global_faces)} face(s) representing "
              f"{unique_faces_count} user(s): {global_faces}")

        return True, rsc.SUCCESS_MSG_DELETE.format(id.replace(ev.BASE_NAME + '-', ''))

    @classmethod
    def delete_identity_on_active_users_table(cls, user_id):
        print(f"BL - Attempting do delete user id '{user_id}' from active users table...")
        if not dao.delete_from_dynamo_by_hash(table_name=ev.ACTIVE_REGISTER_TABLE_NAME, user_id=user_id):
            print(f"BL - Failed to delete user id '{user_id}' from active users table.")
            return False, f"Unable to delete identity '{user_id.replace(ev.BASE_NAME + '-', '')}' from active users table."
        print(f"BL - Successfully deleted user id '{user_id}' from active users table.")
        return True, rsc.SUCCESS_MSG_DELETE.format(user_id.replace(ev.BASE_NAME + '-', ''))




