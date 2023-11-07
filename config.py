import logging.config

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'stream_format': {
            'format': '%(asctime)s [%(levelname)s] %(message)s',
            'datefmt': '%d-%m-%Y %H:%M:%S',
        },
    },
    'handlers': {
        'stream_handler': {
            'formatter': 'stream_format',
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        'my_logger': {
            'handlers': [
                'stream_handler',
            ],
            'level': 'DEBUG',
            'propagate': True,
        }
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('my_logger')


class AppSettings(BaseSettings):
    mongo_host: str = 'mongo'
    mongo_port: int = 27017
    mongo_database: str = 'sample_database'
    mongo_collection: str = 'sample_collection'
    mongo_username: str
    mongo_password: SecretStr

    bot_token: SecretStr

    model_config = SettingsConfigDict(env_file='.env')


app_settings = AppSettings()
