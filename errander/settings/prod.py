from errander.settings.base import *
from decouple import config

SECRET_KEY = config('SECRET_KEY')

EMAIL_BACKEND = config('EMAIL_BACKEND')
EMAIL_USE_TLS = config('EMAIL_USE_TLS')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

DATABASES = {
    'default': {
        'ENGINE': config('PSQL_ENGINE'),
        'NAME': config('PSQL_DB_NAME'),
        'USER': config('PSQL_USER'),
        'PASSWORD': config('PSQL_PASSWORD'),
        'HOST': config('PSQL_HOST'),
        'PORT': '',
    }
}

GOOGLE_API_KEY = config('GOOGLE_API_KEY')
