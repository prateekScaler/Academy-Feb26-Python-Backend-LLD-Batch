"""
Minimal Django settings for the "send welcome email off the request thread" demo.

Everything is in this one file on purpose so you can read the whole config top
to bottom. DO NOT ship these values: SECRET_KEY is public, DEBUG is on, and
ALLOWED_HOSTS accepts anything.

The parts that matter for THIS class are near the bottom:
  * EMAIL_BACKEND  -> where "sent" emails go (here: printed to the worker log)
  * the CELERY_*   -> how Django hands work to Redis and how the worker behaves
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Core (demo values -- never use in production)
# ---------------------------------------------------------------------------
SECRET_KEY = "django-insecure-DEMO-KEY-do-not-use"
DEBUG = True
ALLOWED_HOSTS = ["*"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = [
    # Django essentials needed for the ORM + migrations. No admin/staticfiles:
    # this service has no UI, it just accepts a request and enqueues a job.
    "django.contrib.contenttypes",
    "django.contrib.auth",
    # Our app: the email tasks + the two bookkeeping models (SentEmail, DeadLetter).
    "emails",
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

USE_TZ = True
TIME_ZONE = "UTC"

# ===========================================================================
# EMAIL -- this is the whole point of the class, so read the comment.
# ===========================================================================
#
# The CONSOLE backend does not talk to any SMTP server. Instead, every call to
# send_mail() prints the fully-rendered email to stdout. Because send_mail() is
# executed inside the Celery WORKER (not the web process), the email shows up in
# the WORKER's terminal -- which is exactly what we want students to watch.
#
# No SMTP account, no passwords, nothing to leak. Perfect for a lecture.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "no-reply@scaler.example"
#
# ---- HOW YOU'D SWAP IN REAL SMTP FOR PRODUCTION -------------------------
# Delete the line above and use these instead (values from env vars / secrets):
#
#   EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
#   EMAIL_HOST = os.environ["EMAIL_HOST"]            # e.g. smtp.sendgrid.net
#   EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
#   EMAIL_USE_TLS = True
#   EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
#   EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
#
# Nothing else in this project changes -- the task, retries, DLQ, idempotency
# all stay identical. Only the "how the bytes leave the building" backend swaps.
# -------------------------------------------------------------------------

# ===========================================================================
# CELERY -- keys are read by Celery because celery.py uses namespace="CELERY".
# So `CELERY_BROKER_URL` here becomes Celery's `broker_url`, etc.
# ===========================================================================

# The BROKER is where jobs wait until a worker is free. We use Redis. The URL is
# read from an env var so we can point at a throwaway Redis on a non-default
# port during testing without editing code.
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")

# Optional: store task return values so you can inspect them from a shell.
# Not required for .delay() to work; handy for teaching.
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)

# ---- These two settings make the retry/ack story HONEST -----------------
#
# acks_late = True: the message is acknowledged (removed from the broker) only
# AFTER the task finishes running, not the moment the worker picks it up. So if
# the worker is killed mid-task, Redis still has the job and another worker gets
# it -> at-least-once delivery (which is why our task is idempotent!).
CELERY_TASK_ACKS_LATE = True
#
# prefetch_multiplier = 1: each worker grabs ONE job at a time instead of
# greedily buffering a batch. With acks_late this means a crash can lose at most
# the single in-flight job, and it keeps the live demo easy to follow.
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
#
# If a worker process is lost while a job is running, re-queue that job.
CELERY_TASK_REJECT_ON_WORKER_LOST = True

CELERY_TIMEZONE = "UTC"

# ---------------------------------------------------------------------------
# Demo knobs for the fake failures (kept here so they're easy to find).
# ---------------------------------------------------------------------------
# Base seconds for exponential backoff: real wait = BASE * 2**retry_number,
# i.e. 1s, 2s, 4s, ... Small so a live demo doesn't drag.
EMAIL_RETRY_BASE_BACKOFF = float(os.environ.get("EMAIL_RETRY_BASE_BACKOFF", "1"))
# How many times a "fail@" address fails before it finally succeeds.
EMAIL_FAIL_TIMES = int(os.environ.get("EMAIL_FAIL_TIMES", "2"))
# How many retries before a job is dead-lettered (total attempts = this + 1).
EMAIL_MAX_RETRIES = int(os.environ.get("EMAIL_MAX_RETRIES", "3"))
