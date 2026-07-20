"""
Settings for the "Login with Google" (OAuth 2.0 Authorization Code + PKCE) demo.

Kept deliberately small so the OAuth parts are easy to spot.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Demo value only. In a real project this comes from an environment variable
# and is never committed to git.
SECRET_KEY = "django-insecure-demo-key-for-oauth-class-do-not-use-in-prod"

DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # SessionMiddleware is REQUIRED here: we stash the PKCE code_verifier and
    # the anti-CSRF `state` in request.session between the two halves of the
    # OAuth flow (the redirect out to Google, and the callback coming back).
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------------------------
# Google OAuth 2.0 configuration
# ---------------------------------------------------------------------------
# You get these two from Google Cloud Console (see README.md).
# Read from the environment so real secrets never live in source control.
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "PASTE_YOUR_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "PASTE_YOUR_CLIENT_SECRET")

# Where Google sends the browser back after the user consents.
# This string must match EXACTLY (scheme, host, port, trailing slash) what you
# registered as an "Authorized redirect URI" in Google Cloud Console.
GOOGLE_REDIRECT_URI = "http://127.0.0.1:8000/oauth/callback/"

# Step 1 endpoint: we send the USER'S BROWSER here. Google shows the login +
# consent screen. Google is the only party that ever sees the password.
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"

# Step 2 endpoint: our SERVER calls this (back-channel, no browser involved)
# to trade the one-time `code` + our `code_verifier` for an access token.
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

# Step 3 endpoint: our server calls this with the access token to read the
# user's basic profile (name, email, picture).
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
