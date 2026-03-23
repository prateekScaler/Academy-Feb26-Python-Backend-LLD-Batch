"""
Django settings for restaurant_demo project.
Class 9: Exception Handling, Decorators & Middleware Demo
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-demo-key-for-class-only'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'menu',
]

# =============================================================================
# MIDDLEWARE - ORDER MATTERS!
# Request flows TOP to BOTTOM, Response flows BOTTOM to TOP
# =============================================================================
MIDDLEWARE = [
    # Our custom middleware for demo
    'restaurant_demo.middleware.RequestTimingMiddleware',
    'restaurant_demo.middleware.RequestLoggingMiddleware',

    # Django built-in middleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Uncomment to enable maintenance mode
    # 'restaurant_demo.middleware.MaintenanceModeMiddleware',
]

ROOT_URLCONF = 'restaurant_demo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'restaurant_demo.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# CUSTOM SETTINGS FOR DEMO
# =============================================================================

# Set to True to enable maintenance mode
MAINTENANCE_MODE = False
MAINTENANCE_MESSAGE = "Site is under maintenance. Please try again later."
