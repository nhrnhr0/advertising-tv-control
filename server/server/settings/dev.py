from .base import *

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1',]
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:5173',]

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}