# Minimal settings for the demo — in-memory SQLite, just DRF + our one app.
SECRET_KEY = "insecure-test-key-do-not-use-in-prod"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "demoapp",
]
MIDDLEWARE = []
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
ROOT_URLCONF = "demoproj.urls"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
REST_FRAMEWORK = {"UNAUTHENTICATED_USER": None}
