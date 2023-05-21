
from .secrects import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
from .base import *

DEBUG = False

ALLOWED_HOSTS = ['adv-tv-control.ms-global.co.il','adv-tv-control.boost-pop.com',]
CSRF_TRUSTED_ORIGINS = ['https://adv-tv-control.ms-global.co.il','https://kehilaton.ms-global.co.il',]
CORS_ORIGIN_WHITELIST = ['https://adv-tv-control.ms-global.co.il','https://kehilaton.ms-global.co.il',]
DATABASES = {
    "default": {
        "ENGINE": 'django.db.backends.postgresql',
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
        'CONN_MAX_AGE': 0,
    }
}

CHANNEL_LAYERS = {
        'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('localhost', 6379)],
        },
    },
}
