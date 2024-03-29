"""
Django settings for universityofbigdata project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os, sys
from pathlib import Path
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(os.path.normpath(BASE_DIR))

APPS_DIR = BASE_DIR / 'apps'
sys.path.insert(0, os.path.normpath(APPS_DIR))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/


# SECURITY WARNING: don't run with debug turned on in production!
# from .settings_sw import *


# Application definition
AUTH_USER_MODEL = 'accounts.User'

# ソーシャル認証
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',  # Google OAuth2用
    'django.contrib.auth.backends.ModelBackend',  # デフォルトバックエンド、必須。
)

INSTALLED_APPS = [
    'accounts.apps.AccountsConfig', # ユーザー/チーム管理追加
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_bootstrap5',
    'django_pandas',  # 設定
    'social_django',  # ソーシャル認証用追加
    'django_cleanup.apps.CleanupConfig',  # django-cleanup
    'competitions.apps.CompetitionsConfig', # コンペ用追加
    'discussion.apps.DiscussionConfig', # 議論
    'django_apscheduler', # 定期実行処理(コンペの更新など)
    'management.apps.ManagementConfig',
    'authentication.apps.AuthenticationConfig',
    'log_viewer',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', # 追加
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',  # 追加
]

ROOT_URLCONF = 'universityofbigdata.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',  # 追加
                'social_django.context_processors.login_redirect', # 追加
            ],
        },
    },
]
WSGI_APPLICATION = 'wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'data' / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 30,
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/
LANGUAGE_CODE = 'ja'  # もとの値: 'en-us'
TIME_ZONE = 'Asia/Tokyo'  # もとの値: 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = os.path.join(BASE_DIR, 'data', 'static')

""" --------------追記----------------"""

# ファイル保存設定
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'data', 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 言語変換設定
LOCALE_PATHS = [
    BASE_DIR / 'locale'
]
LANGUAGES = [
    ('ja', _('日本語')),
    ('en', _('英語')),
]

# ソーシャル認証設定
#LOGIN_URL = 'login_google' # google認証用
#LOGIN_REDIRECT_URL = 'login_required' # 認証後遷移
LOGIN_URL = 'login' # google認証用
LOGIN_REDIRECT_URL = 'signup_google'
LOGOUT_REDIRECT_URL = '/'

# logger 用設定
LOG_DIR = BASE_DIR / 'data' / 'log' / 'apps'
LOG_FILE = LOG_DIR / 'log.json'
LOG_BACKUP_COUNT = 10
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s a',
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(message)s a'
        },
        'json': {
            '()': 'universityofbigdata.utils.CustomJSONFormatter',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': LOG_FILE,
            'formatter': 'json',
            # 'class': 'logging.handlers.RotatingFileHandler',
            # 'filename': LOG_FILE,
            # 'formatter': 'json',
            # 'backupCount': LOG_BACKUP_COUNT,
            # 'maxBytes': 5*1024*1024,  # 5 MB
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
        'competitions': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'accounts': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'discussion': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'management': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'authentication': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    }
}
LOG_VIEWER_FILES = []
LOG_VIEWER_FILES_PATTERN = '*.json*'
LOG_VIEWER_FILES_DIR = LOG_DIR
LOG_VIEWER_PAGE_LENGTH = 25       # total log lines per-page
LOG_VIEWER_MAX_READ_LINES = 1000  # total log lines will be read
# Max log files loaded in Datatable per page
LOG_VIEWER_FILE_LIST_MAX_ITEMS_PER_PAGE = 25
LOG_VIEWER_PATTERNS = [""]
# String regex expression to exclude the log from line
LOG_VIEWER_EXCLUDE_TEXT_PATTERN = None

# Djangoシークレットキー
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# Google OAuth2 のキー
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')

# デバッグ設定
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')
