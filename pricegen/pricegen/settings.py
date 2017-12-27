"""
Django settings for pricegen project.

Generated by 'django-admin startproject' using Django 2.0.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'wz0@*)0q$x66uk45(c3(ggjrn%=*nm_qv+=tgn_rumka0(2=!9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'users.apps.UsersConfig',
    'pricelists.apps.PricelistsConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pricegen.middleware.LoginRequiredMiddleware',
]

ROOT_URLCONF = 'pricegen.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'pricegen.context_processors.context_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'pricegen.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static_src/'),
    os.path.join(BASE_DIR, 'asset_src/'),
)
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
STATIC_URL = '/static/'

# MEDIA_ROOT to be in local_settings.py
#
MEDIA_URL = '/media/'

LOGIN_URL = "/login/"
LOGOUT_URL = "/logout/"

# Округление при вычислениях цен (10 в степени)
#
CALC_ROUND_EXPONENT = 0

# Зарезервированные имена и суффиксы
#
FS_LOG_FOLDER = 'log'
FS_VENDORS_FOLDER = 'vendors'
FS_SUPPLIERS_FOLDER = 'suppliers'
FS_VENDOR_OUTBOX_FOLDER = 'outbox'
FS_QUARANTINE_FOLDER = 'quarantine'
FS_TMP_FOLDER = 'tmp'
FS_ARCHIVE_FOLDER = 'archive'
FS_STAT_PREFIX = 'pricegen-stat-'
FS_LOG_PREFIX = 'pricegen-log-'
FS_ERROR_PREFIX = 'pricegen-error-'
FS_LOG_EXT = 'log'

# Команды архивации, деархивации
#
CMD_ZIP = 'xz -z'
CMD_UNZIP = 'xz -d'
# Расширение у архивированных файлов
ZIP_EXT = 'xz'

# ПАРАМЕТРЫ XLSX файлов --------------------------
#
# Максимальное число колонок в файлах Excel (16384),
# но здесь ограничиваем реальным числом
#
XLSX_MAX_COLS = 256

# Если организация не подала свое соответствие колонок
# в Excel файлах данным, то принимается такое
# (нумерация здесь, начиная с 1 !!!):

XLSX_COL_NUMBERS_DEFAULT = dict(
    inner_id_col=1,
    partnumber_col=2,
    brand_col=3,
    item_name_col=4,
    price_col=5,
    quantity_col=6,
    delivery_time_col=7
)
# Вычисляемые колонки. Будут только в вых. файлах
#
XLSX_OUTPUT_ONLY_COLS = ('delivery_time_col',)

# Вых. XLSX файл состоит из одного листа. Его имя:
#
XLSX_OUTPUT_SHEET_NAME = 'TDSheet'

# Длины и форматирование колонок в выходном файле
#
XLSX_COL_STYLES = dict(
    inner_id_col=dict(
        width=12,
        font=dict(
            name='Arial',
            size=9,
        ),
        alignment=dict(
            horizontal='left'
        ),
    ),
    partnumber_col=dict(
        width=18,
        font=dict(
            name='Arial',
            size=9,
        ),
        alignment=dict(
            horizontal='left'
        ),
    ),
    brand_col=dict(
        width=19,
        font=dict(
            name='Arial',
            size=9,
        ),
        alignment=dict(
            horizontal='left'
        ),
    ),
    item_name_col=dict(
        width=80,
        font=dict(
            name='Arial',
            size=9,
            bold=True,
        ),
        alignment=dict(
            horizontal='left'
        ),
    ),
    price_col=dict(
        width=12,
        font=dict(
            name='Arial',
            size=9,
        ),
        alignment=dict(
            horizontal='right'
        ),
    ),
    quantity_col=dict(
        width=10,
        font=dict(
            name='Arial',
            size=9,
        ),
        alignment=dict(
            horizontal='right'
        ),
    ),
    delivery_time_col=dict(
        width=12,
        font=dict(
            name='Arial',
            size=9,
        ),
        alignment=dict(
            horizontal='left'
        ),
    ),
)

# ------------------------------------------------

from pricegen.local_settings import *
