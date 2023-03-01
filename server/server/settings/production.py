
from .secrects import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
from .base import *

DEBUG = False

ALLOWED_HOSTS = ['gold-tv-server2.boost-pop.com', 'gold-tv.boost-pop.com']
CSRF_TRUSTED_ORIGINS = ['https://gold-tv-server2.boost-pop.com', 'http://gold-tv-server2.boost-pop.com',
                        'https://gold-tv2.boost-pop.com', 'http://gold-tv2.boost-pop.com']

DATABASES = {
    "default": {
        "ENGINE": 'django.db.backends.postgresql_psycopg2',
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
    }
}
