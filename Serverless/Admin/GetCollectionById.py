import time, boto3
from Admin.AdminManager import AdminManager as am
from lib.Resources.EnvironmentVariables import EnvironmentVariables as ev
from lib.Dao.FetchFromDynamo import FetchFromDynamo as fd

class GetCollectionById:

    @classmethod
    def get(cls, request_data):

        # Inicializar lista de retorno
        return_list = []

        # Extrair userId do corpo da requisicao
        try:
            user_id = ev.BASE_NAME + '-' + request_data.get('userId')
            print(f"BL - Successfully extracted given user ID from request body: '{str(user_id)}'")
        except Exception as e:
            print('BL - Error: unable to extract user ID from request body.')
            return return_list

        # Inicializar cliente boto3
        client = boto3.client('rekognition')

        # Levantamento de todas as faces na collection do usuario solicitado
        try:
            response = client.list_faces(CollectionId=user_id, MaxResults=100)
            face_ids = [x.get('ExternalImageId') for x in response.get('Faces')]
            while True:
                if 'NextToken' in response:
                    nextToken = response['NextToken']
                    response = client.list_faces(CollectionId=user_id, NextToken=nextToken, MaxResults=100)
                    face_ids = face_ids + [x.get('ExternalImageId') for x in response.get('Faces')]
                else:
                    break

            if len(response) == 0:
                print('ADMIN - Empty collection: collection associated with given user ID contains no faces.')
                return return_list

            print(f"ADMIN - Found {str(len(face_ids))} faces in this user's collection. Ids: {str(face_ids)}")

        except Exception as e:
            print(f"ADMIN - Error: unable to list faces for given user ID's collection.: {str(e)}")
            return return_list

        # Capturar log de registros do usuario requisitado
        register_logs = fd.fetch_data(ev.REGISTER_TABLE_NAME, request_data)
        print(f"ADMIN - Fetched {str(len(register_logs))} entries associated with userId '{user_id}' "
              f"from registers log table: {register_logs}")

        # Capturar nomes dos arquivos de imagem no bucket de arquivos publicos
        public_bucket_files = am.get_public_bucket_file_names()

        # Inicializar marcadores de tempo das operações
        total_digestion_time = 0
        total_transfer_time = 0

        # Iteração principal para montagem do objeto de retorno e atualização do bucket publico de arquivos de imagens
        for item in register_logs:

            # Extrair faceId do log atual
            try:
                face_id = item.get('rekognition_responses').get('index_faces').get('FaceRecords')[0].get('Face')\
                    .get('FaceId')
            except Exception as e:
                print(f"ADMIN - Error: unable to retrieve face id from current entry: " + str(e))
                print(f"ADMIN - Failed entry: " + str(item))
                continue

            # Atuar caso o faceId encontrado esteja entre os detectados na collection do usuario
            if face_id in face_ids:

                # Verificar se a imagem associada esta no bucket publico e atualizar caso necessario, medindo tempo
                transfer_time = time.time()
                try:
                    if item['img_info']['s3_path_hash'] not in public_bucket_files: am.update_public_bucket(item)
                except Exception as e:
                    print(f"ADMIN - Error: unable to retrieve image path hash from current entry: " + str(e))
                    print(f"ADMIN - Failed entry: " + str(item))
                    continue
                finally:
                    total_transfer_time += round(time.time() - transfer_time, 3)

                # Montar objeto de retorno para o log corrente e adicionar a lista de retorno principal, medindo tempo
                digestion_time = time.time()
                new_item = am.digest_data(item)
                total_digestion_time += round(time.time() - digestion_time, 3)
                return_list.append(new_item)

                # Remover o faceId da lista de faceIds requisitadas do usuario e interromper a iteracao caso todas ja
                # tenham sido localizadas
                face_ids.remove(face_id)
                if len(face_ids) == 0: break

        # Informar metricas da operacao ao desenvolvedor
        print(f"ADMIN - Retrieving {str(len(return_list))} collection register logs after associating with user "
              f"collection. Data digestion time: {total_digestion_time}s | Image transfer time: "
              f"{total_transfer_time}s. Return list: {str(return_list)}")

        return return_list