"""
LLD-40 | Containerization -- Tier 2: webapp.py
==============================================

A REAL (if tiny) Django service in one file -- the thing we will put in a
container. Same single-file pattern as LLD-39's django_request_logging.py,
shrunk to the essentials.

    Needs:    pip install -r requirements.txt      (or: the Dockerfile does it)
    Run it:   python3 webapp.py runserver 0.0.0.0:8040 --noreload

    Then, from a second terminal:
        curl http://127.0.0.1:8040/           # service info + request counter
        curl http://127.0.0.1:8040/health     # liveness probe target

Two container rules are baked into this file:

  1. LOG TO STDOUT, NOTHING ELSE. No log files. A container's stdout IS its
     log stream: `docker logs <container>` replays it, and in production the
     platform ships it to the aggregator (the LLD-39 pipeline). If we wrote
     to app.log inside the container, it would die with the container.

  2. BIND TO 0.0.0.0, NOT 127.0.0.1. Inside a container, 127.0.0.1 means
     "the container itself" -- Docker's port mapping could never reach it.
     0.0.0.0 = "every interface", which is what lets -p 8040:8040 work.
"""

import json
import logging
import socket
import sys
import time

import django
from django.conf import settings
from django.http import JsonResponse

SERVICE = "lld40-webapp"

# ---------------------------------------------------------------------------
# Settings (single-file pattern: configure BEFORE importing anything that
# touches settings, then django.setup()).
# ---------------------------------------------------------------------------
settings.configure(
    DEBUG=False,                        # prod-style: no yellow debug pages
    SECRET_KEY="dev-only-not-secret",   # real key would come from env (12-factor)
    ALLOWED_HOSTS=["*"],                # fine for a class demo
    ROOT_URLCONF=__name__,              # the URL table lives in THIS file
    MIDDLEWARE=[f"{__name__}.stdout_request_log"],
    # Silence runserver's own plain-text access lines ("GET / HTTP/1.1" 200)
    # so each request produces exactly ONE log line: our JSON one.
    LOGGING={
        "version": 1,
        "disable_existing_loggers": False,
        "loggers": {"django.server": {"handlers": [], "propagate": False}},
    },
)
django.setup()

# ---------------------------------------------------------------------------
# Logging: one JSON line per request, to STDOUT (container rule #1).
# This is LLD-39's access-log middleware in miniature: no request ids, no
# custom Formatter class -- just the one-line-per-request habit.
# ---------------------------------------------------------------------------
log = logging.getLogger(SERVICE)
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler(sys.stdout))   # stdout, NOT a file


def stdout_request_log(get_response):
    """Middleware: time the request, then print ONE JSON line about it."""
    def middleware(request):
        started = time.monotonic()
        response = get_response(request)
        log.info(json.dumps({
            "event": "http_request",
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration_ms": round((time.monotonic() - started) * 1000, 1),
        }))
        return response
    return middleware


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------
REQUEST_COUNT = 0  # in-PROCESS counter: lives in this worker's memory only.
                   # Restart the container -> back to 0. Run two containers ->
                   # two independent counts. Tier 3 fixes this with Redis.


def home(request):
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    return JsonResponse({
        "service": SERVICE,
        # In a container this hostname is the container id -- proof of which
        # box answered you. Compare it with `docker ps`.
        "hostname": socket.gethostname(),
        "requests_served": REQUEST_COUNT,
    })


def health(request):
    # The HEALTHCHECK in our Dockerfile curls this URL every 30s.
    # LLD-39 callback: this is a LIVENESS-style probe -- "is the process up
    # and answering?" -- deliberately free of dependency checks. Tier 3 adds
    # a READINESS-style probe that inspects Redis too.
    return JsonResponse({"status": "ok"})


urlpatterns = []          # filled via django.urls after setup()
from django.urls import path                       # noqa: E402
urlpatterns = [
    path("", home),
    path("health", health),
]

# ---------------------------------------------------------------------------
# Entry point: hand argv to Django's manage.py machinery.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
