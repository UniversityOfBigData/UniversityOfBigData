"""Djangoのローカル設定."""
from .base import *  # noqa

""" 以下にローカル設定を記述してください. """

# サーバーのドメイン名として許可するもの ('*'は全て許可)
ALLOWED_HOSTS = ['*']

# postgresql
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql',
#        'NAME': 'django',
#        'USER': 'django',
#        'PASSWORD': 'django',
#        'HOST': 'db',
#        'PORT': 5432,
#    }
#}
