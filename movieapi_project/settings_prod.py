from .settings import *

DEBUG = False

ALLOWED_HOSTS = ['movieapi.flowfelis.com', 'www.movieapi.flowfelis.com']

SECRET_KEY = os.environ.get('MOVIEAPI_SECRET_KEY')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'moviedb',
        'USER': 'moviedbuser',
        'PASSWORD': os.environ.get('MOVIEAPI_DB_PASSWORD'),
        'HOST': 'localhost'
    }
}
