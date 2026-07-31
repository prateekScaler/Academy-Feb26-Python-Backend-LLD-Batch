# Minimal Django settings -- just enough for runserver to serve one JSON view.
# (No database, no apps: the point of this project is the DOCKERFILE, not Django.)
SECRET_KEY = "dev-only-not-a-secret"
DEBUG = True
ALLOWED_HOSTS = ["*"]          # fine for a demo; never in production
ROOT_URLCONF = "mysite.urls"
INSTALLED_APPS = []
MIDDLEWARE = []
DATABASES = {}
USE_TZ = True
