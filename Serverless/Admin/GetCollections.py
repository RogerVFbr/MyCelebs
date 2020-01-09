import time, boto3
from Admin.AdminManager import AdminManager as am
from lib.Resources.EnvironmentVariables import EnvironmentVariables as ev
from lib.Dao.FetchFromDynamo import FetchFromDynamo as fd


class GetCollections:

    @classmethod
    def get(cls, request_data):
        client = boto3.client('rekognition')

        # Levantamento de todas as collections de faces disponiveis nesse usuario root
        response = client.list_collections(MaxResults=100)
        collectionIds = response['CollectionIds']

        while True:
            if 'NextToken' in response:
                nextToken = response['NextToken']
                response = client.list_collections(NextToken=nextToken, MaxResults=100)
                collectionIds = collectionIds + response['CollectionIds']
            else:
                break

        print(f"ADMIN - Found {str(len(collectionIds))} total collections. Ids: {str(collectionIds)}")

        # Filtrar deixando somente collections associadas a este stage
        collectionIds = [x for x in collectionIds if ev.BASE_NAME in x]
        print(f"ADMIN - Found {str(len(collectionIds))} collections belonging to this stage. Ids: {str(collectionIds)}")

        # Capturar registros de usuario ativos
        register_logs = fd.fetch_data(ev.ACTIVE_REGISTER_TABLE_NAME, request_data)
        print(f"ADMIN - Fetched {str(len(register_logs))} entries from registers table.")

        # Capturar nomes dos arquivos de imagem no bucket de arquivos publicos
        public_bucket_files = am.get_public_bucket_file_names()

        # Inicializar marcadores de tempo das operações
        total_digestion_time = 0
        total_transfer_time = 0

        # Iteração principal para montagem do objeto de retorno e atualização do bucket publico de arquivos de imagens
        return_list = []
        for item in register_logs:
            if item['userId'] in collectionIds:
                transfer_time = time.time()
                if item['img_info']['s3_path_hash'] not in public_bucket_files: am.update_public_bucket(item)
                total_transfer_time += round(time.time() - transfer_time, 3)
                digestion_time = time.time()
                new_item = am.digest_data(item)
                total_digestion_time += round(time.time() - digestion_time, 3)
                return_list.append(new_item)
                collectionIds.remove(item['userId'])
                if len(collectionIds) == 0: break

        print(f"ADMIN - Retrieving {str(len(return_list))} collection register logs after filtering. "
              f"Data digestion time: {total_digestion_time}s | Image transfer time: {total_transfer_time}s. "
              f"Return list: {str(return_list)}")

        return return_list



