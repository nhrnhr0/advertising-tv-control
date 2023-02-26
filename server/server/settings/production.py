
from .base import *

DEBUG = False

ALLOWED_HOSTS = ['gold-tv-server.boost-pop.com', 'gold-tv.boost-pop.com']
CSRF_TRUSTED_ORIGINS = ['https://gold-tv-server.boost-pop.com','http://gold-tv-server.boost-pop.com', 'https://gold-tv.boost-pop.com', 'http://gold-tv.boost-pop.com']


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

# add to the start of  INSTALLED_APPS "daphne",
# INSTALLED_APPS.insert(0, "daphne")