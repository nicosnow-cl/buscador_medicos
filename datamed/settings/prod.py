from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'c0ngia)xphe6o!wh0x2e*^g)-fzjuior4dc2$h^l6k*f!8p8i*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}