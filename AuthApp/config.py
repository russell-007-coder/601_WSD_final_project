from datetime import timedelta
import json
import os


class BaseConfig(object):
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'DEBUG'

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@mysql_db/mydb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'russellpinto996@gmail.com'
    MAIL_PASSWORD = '9653211668'
    MAIL_DEFAULT_SENDER = MAIL_USERNAME

    SECRET_KEY = 'insecurekeyfordev'
    
    SEED_ADMIN_EMAIL = 'russellpinto996@gmail.com'
    SEED_ADMIN_PASSWORD = '9653211668'
    
    REMEMBER_COOKIE_DURATION = timedelta(days=90)


class DevConfig(BaseConfig):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@mysql_db/mydb" # f'sqlite:///{os.getcwd()}/site.db'

class ProdConfig(BaseConfig):
    DEBUG = False
    TESTING = True