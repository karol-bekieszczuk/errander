from errander.settings.base import *

SECRET_KEY = 'some_secret_key'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025

GOOGLE_API_KEY = '*your google api key*'