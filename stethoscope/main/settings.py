"""Top level application settings."""

import importlib.metadata
import os
from pathlib import Path

import environ
from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent

# Application metadata

dist = importlib.metadata.distribution('stethoscope')
VERSION = dist.metadata['version']
SUMMARY = dist.metadata['summary']

env = environ.Env()

# Core security settings

SECRET_KEY = os.environ.get('SECURE_SECRET_KEY', get_random_secret_key())
ALLOWED_HOSTS = env.list("SECURE_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", False)
SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", False)
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", 0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("SECURE_HSTS_SUBDOMAINS", False)

SECURE_REQUIRE_AUTH = env.bool("SECURE_REQUIRE_AUTH", True)

# App Configuration

AUTH_USER_MODEL = 'staff.User'
ROOT_URLCONF = 'stethoscope.main.urls'

INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'stethoscope.apps.licensing',
    'stethoscope.apps.staff',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "servestatic.middleware.ServeStaticMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# REST API settings

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': env.str('API_THROTTLE_ANON', '60/min'),
        'user': env.str('API_THROTTLE_USER', '60/min')
    },
}

# Database

DATABASES = {'default': {
    "ENGINE": "django.db.backends.postgresql",
    'NAME': env.str('DB_NAME', 'stethoscope'),
    'USER': env.str('DB_USER', ''),
    'PASSWORD': env.str('DB_PASSWORD', ''),
    'HOST': env.str('DB_HOST', 'localhost'),
    'PORT': env.str('DB_PORT', '5432'),
}}

# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files

STATIC_URL = '/static/'
STATIC_ROOT = Path(env.path('CONFIG_STATIC_DIR', BASE_DIR / 'static_files'))
STATIC_ROOT.mkdir(mode=0o770, parents=True, exist_ok=True)

STORAGES = {
    "staticfiles": {
        "BACKEND": "servestatic.storage.CompressedManifestStaticFilesStorage",
    },
}

# Admin dashboard styling

UNFOLD = {
    "SITE_TITLE": "Stethoscope",
    "SITE_HEADER": "Stethoscope",
    "SITE_SUBHEADER": "License Management",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "SHOW_BACK_BUTTON": False,
    "SITE_SYMBOL": "stethoscope",
    "BORDER_RADIUS": "6px",
    "SITE_URL": None,
    "COLORS": {
        "base": {
            "50": "oklch(98%   0.003 230)",
            "100": "oklch(95%   0.006 230)",
            "200": "oklch(90%   0.010 230)",
            "300": "oklch(83%   0.015 230)",
            "400": "oklch(70%   0.020 230)",
            "500": "oklch(56%   0.025 230)",
            "600": "oklch(44%   0.028 230)",
            "700": "oklch(36%   0.030 230)",
            "800": "oklch(27%   0.030 230)",
            "900": "oklch(20%   0.028 230)",
            "950": "oklch(13%   0.024 230)",
        },
        "primary": {
            "50": "oklch(97%   0.018 220)",
            "100": "oklch(93%   0.040 220)",
            "200": "oklch(88%   0.075 220)",
            "300": "oklch(80%   0.120 220)",
            "400": "oklch(68%   0.175 220)",
            "500": "oklch(56%   0.215 220)",
            "600": "oklch(47%   0.220 220)",
            "700": "oklch(40%   0.200 220)",
            "800": "oklch(33%   0.170 220)",
            "900": "oklch(27%   0.140 220)",
            "950": "oklch(18%   0.110 220)",
        },
        "font": {
            "subtle-light": "var(--color-base-500)",
            "subtle-dark": "var(--color-base-400)",
            "default-light": "var(--color-base-600)",
            "default-dark": "var(--color-base-300)",
            "important-light": "var(--color-base-900)",
            "important-dark": "var(--color-base-100)",
        },
    },
}
