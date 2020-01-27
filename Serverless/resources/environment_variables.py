import os


class EnvironmentVariables:

    __env_var = dict(os.environ.items())

    BASE_NAME = __env_var.get('BASE_NAME')
    BUCKET_NAME = __env_var.get('BUCKET_NAME')
    PICTURES_TABLE_NAME = __env_var.get('PICTURES_TABLE_NAME')
    NEW_ENTRIES_TABLE_NAME = __env_var.get('NEW_ENTRIES_TABLE_NAME')
    PUBLIC_IMG_BASE_ADDRESS = __env_var.get('PUBLIC_IMG_BASE_ADDRESS')
    ADD_PICTURE_QUEUE_NAME = __env_var.get('ADD_PICTURE_QUEUE_NAME')
    ADD_PICTURE_QUEUE_URL = __env_var.get('ADD_PICTURE_QUEUE_URL')

    @classmethod
    def get(cls, env_var):
        return cls.__env_var.get(env_var)