import time
from Admin.AdminManager import AdminManager as am
from lib.Dao.FetchFromDynamo import FetchFromDynamo as fd
from lib.Resources.EnvironmentVariables import EnvironmentVariables as ev


class GetFailedReckonLogs:

    @classmethod
    def get(cls, request_data):

        public_bucket_files = am.get_public_bucket_file_names()
        items = fd.fetch_data(ev.FAILED_RECKON_TABLE_NAME, request_data)
        return_list = []

        total_digestion_time = 0
        total_transfer_time = 0

        for item in items:
            transfer_time = time.time()
            if item['img_info']['s3_path_hash'] not in public_bucket_files: am.update_public_bucket(item)
            total_transfer_time += round(time.time() - transfer_time, 3)
            digestion_time = time.time()
            new_item = am.digest_data(item)
            total_digestion_time += round(time.time() - digestion_time, 3)
            return_list.append(new_item)

        print(f'ADMIN - Retrieving {len(return_list)} items to client from failed reckon table. '
              f'Data digestion time: {total_digestion_time}s | Image transfer time: {total_transfer_time}s.')

        return return_list