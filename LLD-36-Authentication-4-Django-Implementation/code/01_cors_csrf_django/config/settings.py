"""
Minimal Django 5.x settings for a CSRF / CORS / SameSite teaching demo.

Everything lives in this one file so you can read it top-to-bottom.
"""
from pathlib import Path

# BASE_DIR points at the folder containing manage.py
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

# DEMO ONLY. In a real project this comes from an environment variable and is
# never committed to git. Django uses it to sign cookies, CSRF tokens, etc.
SECRET_KEY = "django-insecure-DEMO-KEY-do-not-use-in-prod"

DEBUG = True

# "*" = accept any Host header. Fine for a local demo, never in production.
ALLOWED_HOSTS = ["*"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Apps
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "corsheaders",  # third-party: adds the Access-Control-Allow-* headers
]

# ---------------------------------------------------------------------------
# Middleware  (order matters!)
# ---------------------------------------------------------------------------
# A request travels DOWN this list, and the response travels back UP.
# CorsMiddleware must be as early as possible so that its CORS headers are
# attached even to responses produced by later middleware (e.g. a 403 from
# CsrfViewMiddleware). Otherwise the browser hides the real error from you.

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",              # 1. CORS headers first
    "django.contrib.sessions.middleware.SessionMiddleware",  # 2. loads request.session
    "django.middleware.common.CommonMiddleware",          # 3. URL normalisation etc.
    "django.middleware.csrf.CsrfViewMiddleware",          # 4. checks the CSRF token
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # 5. request.user
]

ROOT_URLCONF = "config.urls"

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # where index.html lives
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
            ],
        },
    },
]

# ---------------------------------------------------------------------------
# Database (sqlite, created by `python manage.py migrate`)
# ---------------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------

STATIC_URL = "static/"

# ---------------------------------------------------------------------------
# CORS  (Cross-Origin Resource Sharing)
# ---------------------------------------------------------------------------
# MENTAL MODEL: CORS is a *browser* rule about who may READ the response.
# It is NOT server-side authentication. The request still reaches your view and
# still runs. A non-browser client (curl, Postman, a Python script) completely
# ignores CORS -- try `curl http://127.0.0.1:8001/api/ping/` and you get the
# JSON no matter what is configured below.
#
# So: use CORS to let *your own* frontend on another origin read your API.
# Never use it as a security boundary.

# Only these origins are allowed to read responses from this server.
# (An "origin" = scheme + host + port. http://localhost:5500 is a typical
# VS Code Live Server address -- handy for testing a cross-origin page.)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
"http://127.0.0.1:8000"
]

# DANGEROUS SHORTCUT -- do not do this:
# CORS_ALLOW_ALL_ORIGINS = True
# It lets any website on the internet read your API responses from a logged-in
# user's browser. Always list the origins you actually own.

# ---------------------------------------------------------------------------
# Cookie flags: session cookie
# ---------------------------------------------------------------------------

# HttpOnly: JavaScript cannot read this cookie -> blocks an XSS script from
# stealing the session id via document.cookie.
SESSION_COOKIE_HTTPONLY = True

# SameSite="Lax": the browser will NOT attach this cookie to cross-site POSTs
# -> blocks the classic CSRF attack where evil.com auto-submits a form to you.
SESSION_COOKIE_SAMESITE = "Lax"

# Secure: send the cookie only over HTTPS -> blocks network sniffing.
# False here because the demo runs on plain http://127.0.0.1. Set True in prod.
SESSION_COOKIE_SECURE = False

# ---------------------------------------------------------------------------
# Cookie flags: CSRF cookie
# ---------------------------------------------------------------------------

# HttpOnly=True: JS cannot read the CSRF cookie. Safe here because our HTML
# form gets the token from {% csrf_token %}, not from the cookie.
# NOTE: if a JS single-page app needs to read the cookie to set the
# X-CSRFToken header, this must be False.
CSRF_COOKIE_HTTPONLY = True

# SameSite="Lax": the CSRF cookie is not sent on cross-site POSTs -> a forged
# request cannot even reach the state where the token would be compared.
CSRF_COOKIE_SAMESITE = "Lax"

# Secure: HTTPS-only. False for local http development, True in production.
CSRF_COOKIE_SECURE = False
