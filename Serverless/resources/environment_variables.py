import os


class EnvironmentVariables:

    __env_var = dict(os.environ.items())

    BASE_NAME = __env_var.get('BASE_NAME')
    BUCKET_NAME = __env_var.get('BUCKET_NAME')
    THUMBNAIL_BUCKET_NAME = __env_var.get('THUMBNAIL_BUCKET_NAME')
    PICTURES_TABLE_NAME = __env_var.get('PICTURES_TABLE_NAME')
    CELEBRITIES_TABLE_NAME = __env_var.get('CELEBRITIES_TABLE_NAME')
    PUBLIC_IMG_BASE_ADDRESS = __env_var.get('PUBLIC_IMG_BASE_ADDRESS')
    PUBLIC_THUMBNAIL_BASE_ADDRESS = __env_var.get('PUBLIC_THUMBNAIL_BASE_ADDRESS')
    SMALL_THUMBNAIL_SUFFIX = __env_var.get('SMALL_THUMBNAIL_SUFFIX')
    ADD_PICTURE_QUEUE_NAME = __env_var.get('ADD_PICTURE_QUEUE_NAME')
    WEB_SCRAP_QUEUE_NAME = __env_var.get('WEB_SCRAP_QUEUE_NAME')
    QUEUE_BASE_URL = __env_var.get('QUEUE_BASE_URL')

    @classmethod
    def get(cls, env_var):
        return cls.__env_var.get(env_var)