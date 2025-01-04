import os
from dotenv import load_dotenv

load_dotenv()


class Config(object):
    DATABASE_URL = os.getenv('DATABASE_URL')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')
    JWT_EXPIRE_MINUTES = int(os.getenv('JWT_EXPIRE_MINUTES'))