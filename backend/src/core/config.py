import os
from dotenv import load_dotenv

load_dotenv()


class Config(object):
    DATABASE_URL = os.getenv('DATABASE_URL')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')
    JWT_EXPIRE_MINUTES = int(os.getenv('JWT_EXPIRE_MINUTES'))
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = int(os.getenv('REDIS_PORT'))
    REDIS_CLUSTER_QUEUE_PREFIX = os.getenv('REDIS_CLUSTER_QUEUE_PREFIX')
    SCHEDULER_RETRY_INTERVAL = int(os.getenv('SCHEDULER_RETRY_INTERVAL'))