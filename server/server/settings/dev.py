from .base import *

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'testing.boost-pop.com',]
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:5173', 'https://testing.boost-pop.com',]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
