from errander.settings.base import *
from decouple import config

SECRET_KEY = config('SECRET_KEY')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('PSQL_DB_NAME'),
        'USER': config('PSQL_USER'),
        'PASSWORD': config('PSQL_PASSWORD'),
        'HOST': config('PSQL_HOST'),
        'PORT': '',
    }
}

GOOGLE_API_KEY = config('GOOGLE_API_KEY')