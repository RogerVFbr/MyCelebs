import boto3, hashlib, copy

from boto3.dynamodb.conditions import Key

from Utilities.Helpers.Helpers import Helpers as hl
from Resources.EnvironmentVariables import EnvironmentVariables as ev
from Resources.Resources_strings_en import Strings as rsc


class Dao:

    __dynamodb = boto3.resource('dynamodb')
    __s3 = boto3.resource('s3')

    @classmethod
    def log(cls,
            id,
            endpoint,
            table_name,
            log_time,
            api_metrics,
            img_meta_data,
            img_bytes,
            reason,
            request_context,
            identity,
            alternative_table = None,
            detect_faces_response='N.A.',
            index_faces_response='N.A.',
            search_faces_by_image_response='N.A.'
            ):

        # Log image to private S3 Bucket
        s3_log_status, img_s3_location, img_s3_location_hash = cls.log_to_private_s3(
            bucket_name=ev.BUCKET_NAME,
            id=id,
            endpoint=endpoint,
            image_name='{}-{}'.format(id, log_time),
            image_extension=img_meta_data['type'],
            image_data=img_bytes
        )

        if not s3_log_status:
            return False, rsc.LOG_ERROR_UNABLE_TO_LOG, ''

        # Log image to public S3 Bucket used by admin front end
        if not cls.log_to_public_s3(
            bucket_name=ev.FRONT_BUCKET_NAME,
            image_name=img_s3_location_hash,
            image_data=img_bytes
        ):
            return False, rsc.LOG_ERROR_UNABLE_TO_LOG, ''

        # Log operation data to main table
        if not cls.log_to_dynamo(
            table_name=table_name,
            userId=id,
            log_time=log_time,
            reason=reason,
            api_metrics=api_metrics,
            request_context=request_context,
            identity=identity,
            img_meta_data=img_meta_data,
            img_s3_location=img_s3_location,
            img_s3_location_hash=img_s3_location_hash,
            detect_faces_response=detect_faces_response,
            index_faces_response=index_faces_response,
            search_faces_by_image_response=search_faces_by_image_response
        ):
            return False, rsc.LOG_ERROR_UNABLE_TO_LOG, ''

        # Log operation data to secondary table
        if alternative_table is not None:
            if not cls.log_to_dynamo(
                table_name=alternative_table,
                userId=id,
                log_time=log_time,
                reason=reason,
                api_metrics=api_metrics,
                request_context=request_context,
                identity=identity,
                img_meta_data=img_meta_data,
                img_s3_location=img_s3_location,
                img_s3_location_hash=img_s3_location_hash,
                detect_faces_response=detect_faces_response,
                index_faces_response=index_faces_response,
                search_faces_by_image_response=search_faces_by_image_response
            ):
                return False, rsc.LOG_ERROR_UNABLE_TO_LOG, ''

        return True, '', img_s3_location_hash

    @classmethod
    def log_to_private_s3(cls, bucket_name, id, endpoint, image_name, image_extension, image_data):
        key_path = f"{id}/{endpoint}/{image_name}.{image_extension}"
        key_path = key_path.replace(' ', '-').replace(':', '-').replace('.', '-', 1)
        print(f"LOG - S3 @ '{bucket_name}' (Private) -> Attempting to log at key path '{str(key_path)}'")
        try:
            bucket = cls.__s3.Bucket(bucket_name)
            new_f = bucket.put_object(Key=key_path, Body=image_data)
            print(f"LOG - S3 @ '{bucket_name}' (Private) -> Success! Response: {str(new_f).replace('s3.Object', '')}")
        except Exception as e:
            print(f"LOG - S3 @ '{bucket_name}' (Private) -> Failed! Error: {str(e)}")
            return False, '', ''
        img_s3_location = new_f.key
        img_s3_location_hash = str(hashlib.md5(img_s3_location.encode()).hexdigest()) + '.' + image_extension
        return True, img_s3_location, img_s3_location_hash

    @classmethod
    def log_to_public_s3(cls, bucket_name, image_name, image_data):
        print(f"LOG - S3 @ '{bucket_name}' (Public)  -> Attempting to log at key path '{str(image_name)}'")
        try:
            bucket = cls.__s3.Bucket(bucket_name)
            new_f = bucket.put_object(Key=image_name, Body=image_data)
            print(f"LOG - S3 @ '{bucket_name}' (Public)  -> Success! Response: {str(new_f).replace('s3.Object', '')}")
        except Exception as e:
            print(f"LOG - S3 @ '{bucket_name}' (Public)  -> Failed! Error: {str(e)}")
            return False
        return True

    @classmethod
    def log_to_dynamo(cls,
                      table_name,
                      userId,
                      log_time,
                      reason,
                      api_metrics,
                      request_context,
                      identity,
                      img_meta_data,
                      img_s3_location,
                      img_s3_location_hash,
                      detect_faces_response='N.A.',
                      index_faces_response='N.A.',
                      search_faces_by_image_response='N.A.'
                      ):

        item = {
            'userId': userId,
            'time': log_time.replace(' ', '-').replace(':', '-').replace('.', '-'),
            'reason': reason,
            'request_context': request_context,
            'api_metrics': copy.copy(api_metrics),
            'identity': identity,
            'img_info': {
                'img_meta_data': img_meta_data,
                's3_path': img_s3_location,
                's3_path_hash': img_s3_location_hash
            },
            'rekognition_responses': {
                'detect_face': detect_faces_response,
                'index_faces': index_faces_response,
                'search_faces_by_imag': search_faces_by_image_response
            }
        }
        hl.convert_structure_to_dynamo_compatible(item)
        print(f"LOG - DynamoDB @ '{table_name}' -> Attempting to log item: {str(item)}")
        try:
            table = cls.__dynamodb.Table(table_name)
            response = table.put_item(Item=item)
            if response.get('ResponseMetadata') and response.get('ResponseMetadata').get('HTTPStatusCode') \
                    and response.get('ResponseMetadata').get('HTTPStatusCode') == 200:
                print(f"LOG - DynamoDB @ '{table_name}' ->  Success!: '{str(response)}'")
                return True
            else:
                print(f"LOG - DynamoDB @ '{table_name}' ->  Could NOT confirm log: '{str(response)}'")
                return False
        except Exception as e:
            print(f"LOG - DynamoDB @ '{table_name}' ->  ERROR: {str(e)}")
            return False

    @classmethod
    def delete_from_dynamo_by_hash(cls, table_name, user_id):
        table = cls.__dynamodb.Table(table_name)
        items = table.query(KeyConditionExpression=Key('userId').eq(user_id))
        keys = [{'hash': x.get('userId'), 'range': x.get('time')} for x in items.get('Items')]
        print(f"DAO - Deleting from dynamo querried {len(keys)} item(s) under hash key '{user_id}': {str(keys)}")
        print(f"DAO - Deleting querried items...")

        for entry in keys:
            try:
                response = table.delete_item(
                    Key={
                        'userId': entry.get('hash'),
                        'time': entry.get('range'),
                    }
                )
                print(f"DAO - Successfully deleted HASH '{entry.get('hash')}' | RANGE '{entry.get('range')}'. "
                      f"Response: {response.get('ResponseMetadata')}")
            except Exception as e:
                print('DAO - Error: unable to delete item from DynamoDB: ' + str(e))
                return False
        return True




