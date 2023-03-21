from .base import *

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'testing.boost-pop.com','office-testing.boost-pop.com',]
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:5173', 'https://testing.boost-pop.com','https://office-testing.boost-pop.com',]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
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