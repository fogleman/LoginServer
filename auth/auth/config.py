SECRET_KEY = 'CHANGE_ME'
SQLALCHEMY_DATABASE_URI = 'sqlite:///auth.db'
STATIC_ROOT = None

MAIL_SERVER = ''
MAIL_USERNAME = ''
MAIL_PASSWORD = ''
MAIL_DEFAULT_SENDER = ''

try:
    from config_local import *
except ImportError:
    pass
