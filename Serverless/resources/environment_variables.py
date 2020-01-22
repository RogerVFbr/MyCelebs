import os


class EnvironmentVariables:

    __env_var = dict(os.environ.items())

    BASE_NAME = __env_var.get('BASE_NAME')
    BUCKET_NAME = __env_var.get('BUCKET_NAME')
    TABLE_NAME = __env_var.get('TABLE_NAME')
    PUBLIC_IMG_BASE_ADDRESS = __env_var.get('PUBLIC_IMG_BASE_ADDRESS')


    @classmethod
    def get(cls, env_var):
        return cls.__env_var.get(env_var)