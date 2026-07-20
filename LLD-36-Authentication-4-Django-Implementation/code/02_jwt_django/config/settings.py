"""
Minimal Django settings for a JWT auth demo.

Everything here is squeezed into one file on purpose so you can read the whole
configuration top-to-bottom without jumping between modules.

DO NOT copy these values into a real project: the secret key is public, DEBUG is
on, and ALLOWED_HOSTS accepts anything.
"""

from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Core settings (demo values!)
# ---------------------------------------------------------------------------

# In a real project this comes from an environment variable and is kept secret.
# It matters a LOT here, because it is also the key used to SIGN our JWTs
# (see SIGNING_KEY below). Anyone with this key can forge valid tokens.
SECRET_KEY = "django-insecure-DEMO-KEY"

DEBUG = True

ALLOWED_HOSTS = ["*"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    # Django essentials. Note there is no `admin` app: we don't need it, and
    # leaving it out keeps the migration output short.
    "django.contrib.contenttypes",
    "django.contrib.auth",  # gives us the User model + create_user()
    "django.contrib.sessions",
    "django.contrib.staticfiles",  # needed for DRF's browsable API assets
    # Third party
    "rest_framework",
    "rest_framework_simplejwt",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

# The browsable API that DRF renders in a browser is a Django template, so we
# need a template engine configured. The two context processors below are the
# ones DRF's templates actually reach for.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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
# Database
# ---------------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

STATIC_URL = "static/"

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------

REST_FRAMEWORK = {
    # How does DRF figure out WHO is calling? For every request it runs this
    # list of authentication classes. JWTAuthentication looks for an
    # `Authorization: Bearer <token>` header, verifies the token's signature and
    # expiry, and sets request.user accordingly. If the header is missing or the
    # token is bad, request.user stays as AnonymousUser.
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    # What is a caller ALLOWED to do? Default: nothing unless logged in. This is
    # "secure by default" -- every view is protected unless it explicitly opts
    # out with permission_classes = [AllowAny].
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# ---------------------------------------------------------------------------
# SimpleJWT
# ---------------------------------------------------------------------------

SIMPLE_JWT = {
    # ---- Why two tokens with very different lifetimes? -------------------
    #
    # The ACCESS token is sent on every single API request. That means it gets
    # copied into logs, proxies, browser memory, mobile app storage... lots of
    # places it can leak from. It is also STATELESS: the server does not store
    # it anywhere, it just checks the signature. So there is no "logout" button
    # that can kill an access token early -- once issued, it is valid until it
    # expires. The only real defence is to make that window small. 15 minutes
    # means a stolen access token is worthless almost immediately.
    #
    # The REFRESH token is the opposite trade-off. It is sent RARELY (only to
    # /api/token/refresh/, only when the access token has expired), so it is far
    # less exposed. Because it lives in one place and is used once in a while,
    # we can afford to give it a long life -- and that long life is what stops
    # the user being asked to log in every 15 minutes.
    #
    # Short + noisy vs long + quiet. That is the whole idea.
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    # When True, calling /api/token/refresh/ hands back a BRAND NEW refresh
    # token alongside the new access token. Your client should throw away the
    # old one and store the new one. Why bother? It limits the damage if a
    # refresh token is stolen, and it means an active user's 7-day window keeps
    # sliding forward instead of hard-expiring mid-session.
    "ROTATE_REFRESH_TOKENS": True,
    # The prefix expected in the Authorization header. With ("Bearer",) the
    # header must read exactly:
    #     Authorization: Bearer eyJhbGciOi...
    # Get the word wrong (e.g. "Token") and SimpleJWT ignores the header
    # entirely, so you'll see a 401 that looks like a missing token.
    "AUTH_HEADER_TYPES": ("Bearer",),
    # The key used to sign tokens (HMAC-SHA256 by default). Reusing SECRET_KEY
    # is fine for a demo. Important consequence: change this value and every
    # token issued before the change instantly fails verification -- which is
    # the crude "log everybody out" lever in a JWT system.
    "SIGNING_KEY": SECRET_KEY,
}
