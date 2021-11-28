"""
Django settings for mediagallery project.

Generated by 'django-admin startproject' using Django 3.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path

import django_heroku  # install pip in PC and venv

# Build paths inside the project like this: BASE_DIR / 'subdir'.

BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-&7g@%cp4_a(pn-!gr5r9e4r-q!2*8c9ru6&t5gsqam0n%os$4k'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# ALLOWED_HOSTS = ['*'] for all
ALLOWED_HOSTS = ['127.0.0.1', 'authentication-my-app.herokuapp.com', 'localhost']

INSTALLED_APPS = [
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Admin
    'django.contrib.admin',
    # <---   Allauth  --->
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # providers
    # selected providers, more at https://django-allauth.readthedocs.io/en/latest/installation.html
    'allauth.socialaccount.providers.facebook',  # if you need FB api
    'allauth.socialaccount.providers.google',  # if you need google api

    # 'custom_account.apps.AccountConfig',
    'custom_account',
    'mediaapp',
    'django_cleanup',  # should be placed after your app
    'crispy_forms',
    'widget_tweaks',

]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

AUTH_USER_MODEL = 'custom_account.User'  # change from built-in user model to ours
# <app_name>.custom_model_name


# for capital or small letter email1234
AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    'django.contrib.auth.backends.AllowAllUsersModelBackend',
    # Needed to login by email_phone in Django admin, regardless of `allauth`
    'custom_account.backends.EmailBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)


SITE_ID = 1

ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False


ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'none'
# Redirect after login
LOGIN_REDIRECT_URL = '/'

# Redirect after logout
LOGOUT_REDIRECT_URL = '/'

SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        # 'METHOD': 'js_sdk',
        # 'SDK_URL': '//connect.facebook.net/{locale}/sdk.js',
    },

}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # whitenoise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mediagallery.urls'  # Change project name

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mediagallery.wsgi.application'  # Change project name

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases


# For mongodb connections
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        "CLIENT": {
            "name": "media_gallery",
            "host": os.environ['mongoDB_host'],
            "username": os.environ['mongoDB_username'],
            "password": os.environ['mongoDB_password'],
            "authMechanism": "SCRAM-SHA-1",
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Dhaka'

USE_I18N = True
'''
{% load i18n %} is needed for internationalization. The purpose of internationalization 
is to allow a single application to read in multiple languages. In order to do this: you 
need a few hooks called translation strings. To give your template access to these tags, 
put {% load i18n %} toward the top of your template..
'''
DATE_INPUT_FORMATS = ['%d-%m-%Y']  # only works with forms.Form but not in form.ModelForm
USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

MEDIA_ROOT = os.path.join(BASE_DIR, 'media_mediagallery')


MEDIA_URL = '/media_mediagallery/'
django_heroku.settings(locals())
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ['email']
EMAIL_HOST_PASSWORD = os.environ['pass']
DEFAULT_FROM_EMAIL = 'no-reply<no_reply@domain.com>'


ACCOUNT_ADAPTER = "custom_account.my_account_adapter.MyAppAccountAdapter"
SOCIALACCOUNT_ADAPTER = "custom_account.my_account_adapter.MyAppSocialAccountAdapter"

import dj_database_url

db_from_env = dj_database_url.config(conn_max_age=600)
DATABASES['default'].update(db_from_env)

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
# Auto-create primary key used when not defining a primary key type warning in Django
