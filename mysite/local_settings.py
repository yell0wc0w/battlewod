# from settings import PROJECT_ROOT, SITE_ROOT
import os

DEBUG = True
TEMPLATE_DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        'NAME': 'cfbdb',
        'USER': 'hoang.ngo',
        'PASSWORD': 'hoangngo',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}