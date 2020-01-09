import copy, boto3, time
from boto3 import resource
from lib.Resources.EnvironmentVariables import EnvironmentVariables as ev


class AdminManager:

    __s3 = boto3.client('s3')
    __s3_resource = resource('s3')

    @classmethod
    def digest_data(cls, item):
        new_item = copy.deepcopy({})
        new_item['identity'] = item['identity']
        new_item['userId'] = item['userId'].replace(ev.BASE_NAME + '-', '')
        new_item['time'] = item['time']
        new_item['img_info'] = {}
        new_item['img_info']['img_meta_data'] = item['img_info']['img_meta_data']
        new_item['img_info']['s3_path_hash'] = item['img_info']['s3_path_hash']
        new_item['reason'] = item['reason']
        new_item['api_metrics'] = [{'key': k, 'value': v} for k, v in item['api_metrics'].items()]
        new_item['face_details'] = {}
        new_item['face_details']['AgeRange'] = item['rekognition_responses']['detect_face']['FaceDetails'][0][
            'AgeRange']
        new_item['face_details']['Gender'] = item['rekognition_responses']['detect_face']['FaceDetails'][0][
            'Gender']

        new_item['face_details']['Emotions'] = item['rekognition_responses']['detect_face']['FaceDetails'][0][
            'Emotions']
        new_item['face_details']['Emotions'] = \
            [{'Type': x['Type'], 'Confidence': float(x['Confidence'])} for x in new_item['face_details']['Emotions']]
        new_item['face_details']['Emotions'] = sorted(new_item['face_details']['Emotions'],
                                                      key=lambda k: k['Confidence'], reverse=True)[:3]

        new_item['bounding_box'] = {}

        if 'rekognition_responses' in item:

            if 'index_faces' in item['rekognition_responses'] and item['rekognition_responses']['index_faces'] != 'N.A.':
                new_item['bounding_box'] = item['rekognition_responses']['index_faces']['FaceRecords'][0]['Face']['BoundingBox']

            elif 'search_faces_by_imag' in item['rekognition_responses'] and item['rekognition_responses']['search_faces_by_imag'] != 'N.A.':
                new_item['bounding_box'] = item['rekognition_responses']['search_faces_by_imag'][0]['Face']['BoundingBox']

            elif 'detect_face' in item['rekognition_responses'] and item['rekognition_responses']['detect_face'] != 'N.A.':
                new_item['bounding_box'] = item['rekognition_responses']['detect_face']['FaceDetails'][0]['BoundingBox']

            if new_item['bounding_box'] != {}:
                new_item['bounding_box']['Height'] = float(new_item['bounding_box']['Height'])
                new_item['bounding_box']['Left'] = float(new_item['bounding_box']['Left'])
                new_item['bounding_box']['Top'] = float(new_item['bounding_box']['Top'])
                new_item['bounding_box']['Width'] = float(new_item['bounding_box']['Width'])

        return new_item

    @classmethod
    def update_public_bucket(cls, item):
        print('ADMIN - Copying image to public bucket...')
        print('ADMIN - Image base key: ' + item['img_info']['s3_path'])
        print('ADMIN - Image hash: ' + item['img_info']['s3_path_hash'])
        copy_source = {
            'Bucket': ev.BUCKET_NAME,
            'Key': item['img_info']['s3_path']
        }
        cls.__s3_resource.meta.client.copy(copy_source, ev.FRONT_BUCKET_NAME, item['img_info']['s3_path_hash'])

    @classmethod
    def get_public_bucket_file_names(cls):
        print('ADMIN - Scanning file names on public images folder...')
        op_duration = time.time()
        s3_result = cls.__s3.list_objects_v2(Bucket=ev.FRONT_BUCKET_NAME)
        if 'Contents' not in s3_result: return []
        file_list = []
        for key in s3_result['Contents']:
            file_list.append(key['Key'])
        while s3_result['IsTruncated']:
            continuation_key = s3_result['NextContinuationToken']
            s3_result = cls.__s3.list_objects_v2(Bucket=ev.FRONT_BUCKET_NAME, ContinuationToken=continuation_key)
            for key in s3_result['Contents']:
                file_list.append(key['Key'])
        print('ADMIN - File names scanning completed. Found {} files. Time elapsed: {:.3}s.'
              .format(len(file_list), time.time() - op_duration))
        return file_list
