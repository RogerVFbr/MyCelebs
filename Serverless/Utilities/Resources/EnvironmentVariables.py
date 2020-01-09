import os


class EnvironmentVariables:

    __env_var = dict(os.environ.items())

    BASE_NAME = __env_var['BASE_NAME']
    GLOBAL_COLLECTIONS_NAME = __env_var['GLOBAL_COLLECTIONS_NAME']
    BUCKET_NAME = __env_var['BUCKET_NAME']
    FRONT_BUCKET_NAME = __env_var['FRONT_BUCKET_NAME']
    REGISTER_TABLE_NAME = __env_var['REGISTER_TABLE_NAME']
    ACTIVE_REGISTER_TABLE_NAME = __env_var['ACTIVE_REGISTER_TABLE_NAME']
    RECKON_TABLE_NAME = __env_var['RECKON_TABLE_NAME']
    FAILED_RECKON_TABLE_NAME = __env_var['FAILED_RECKON_TABLE_NAME']

    @classmethod
    def get(cls, env_var):
        return cls.__env_var[env_var]