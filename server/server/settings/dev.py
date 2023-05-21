from .base import *
from .secrects import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

DEBUG = True

# CORS_ORIGIN_WHITELIST = ['http://localhost:5173',]
ALLOWED_HOSTS = ['127.0.0.1', 'testing.boost-pop.com','office-testing.boost-pop.com','localhost', '*',]
CSRF_TRUSTED_ORIGINS = ['http://localhost:5173', 'https://testing.boost-pop.com','https://office-testing.boost-pop.com','http://']


CORS_ALLOW_ALL_ORIGINS = True # If this is used then `CORS_ALLOWED_ORIGINS` will not have any effect
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = ['http://127.0.0.1:5173',]
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }
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
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# django-debug-toolbar
INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]