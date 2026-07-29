"""
LLD-39 | Logging & Monitoring -- Demo 3: django_request_logging.py
==================================================================

Production-style REQUEST logging in Django -- in ONE self-contained file.

    Needs:    pip install Django          (see requirements.txt / venv)
    Run it:   python3 django_request_logging.py runserver 127.0.0.1:8039 --noreload

    Then, from a second terminal:
        curl -i http://127.0.0.1:8039/ok      # normal request
        curl -i http://127.0.0.1:8039/slow    # watch duration_ms jump
        curl -i http://127.0.0.1:8039/boom    # a 500 + traceback in the log
        curl -i -H "X-Request-ID: my-trace-123" http://127.0.0.1:8039/ok
                                              # your id is honored end-to-end

What this demonstrates (the industry-standard "access log" pattern):
  1. EVERY request produces exactly ONE structured JSON line:
         method, path, status, duration_ms, request_id
  2. request_id: generated per request (or taken from the incoming
     X-Request-ID header, so a frontend/gateway can stitch traces), and
     echoed back in the response headers -- users can report it to support.
  3. Errors: Django's own django.request logger prints the traceback,
     while OUR middleware still emits its one-line summary for the 500.
"""

import json
import logging
import sys
import time
import uuid
from datetime import datetime, timezone

import django
from django.conf import settings

# ===========================================================================
# PART 1 -- A JSON formatter using ONLY the stdlib
# ===========================================================================
# Aggregators want JSON (see structured_logging.py). Django's LOGGING config
# accepts any logging.Formatter subclass -- so we write a tiny one ourselves
# instead of pulling in another dependency.

# Every LogRecord is born with ~20 bookkeeping attributes (lineno, thread,
# process, ...). Anything BEYOND those was passed by us via `extra={...}`.
# We snapshot the standard set once, from a blank record:
_STANDARD_ATTRS = set(
    logging.LogRecord("", 0, "", 0, "", None, None).__dict__
) | {"message", "asctime", "taskName"}


class JsonFormatter(logging.Formatter):
    """Render each log record as one JSON object per line."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "level": record.levelname.lower(),
            "logger": record.name,
            "event": record.getMessage(),
        }
        # Merge in the custom fields (whatever the log call passed as extra=)
        for key, value in record.__dict__.items():
            if key not in _STANDARD_ATTRS and not key.startswith("_"):
                payload[key] = value
        # If an exception is attached, include the traceback as a field
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload)


# ===========================================================================
# PART 2 -- Settings, incl. the LOGGING dict (single-file Django pattern)
# ===========================================================================
settings.configure(
    DEBUG=False,                          # prod-style: no yellow debug pages
    SECRET_KEY="dev-only-not-secret",     # placeholder; real key comes from env
    ALLOWED_HOSTS=["*"],                  # fine for a localhost demo
    ROOT_URLCONF=__name__,                # "the URL table is in THIS file"
    MIDDLEWARE=[
        # Our middleware wraps EVERYTHING below it in the stack, so the
        # timer starts before -- and stops after -- all other work.
        f"{__name__}.RequestLogMiddleware",
    ],
    LOGGING={
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            # "()" = "build the formatter by calling this" -> our class above
            "json": {"()": JsonFormatter},
            # Human-readable format for Django's own error reports, so the
            # traceback stays easy to read during class.
            "plain": {"format": "%(asctime)s %(levelname)-8s %(name)s - %(message)s"},
        },
        "handlers": {
            "console_json": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",   # stdout: the container way
                "formatter": "json",
            },
            "console_plain": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "plain",
            },
        },
        "loggers": {
            # OUR access log: one JSON line per request (see middleware)
            "request_log": {
                "handlers": ["console_json"],
                "level": "INFO",
                "propagate": False,
            },
            # Django announces unhandled view exceptions here (with traceback)
            "django.request": {
                "handlers": ["console_plain"],
                "level": "WARNING",
                "propagate": False,
            },
            # Silence runserver's built-in "GET /ok 200" lines -- our JSON
            # access log REPLACES them (else every request logs twice).
            "django.server": {
                "handlers": ["console_plain"],
                "level": "WARNING",
                "propagate": False,
            },
        },
        "root": {"handlers": ["console_plain"], "level": "WARNING"},
    },
)
django.setup()

# These imports need settings to exist, so they come AFTER configure():
from django.http import HttpResponse, JsonResponse   # noqa: E402
from django.urls import path                          # noqa: E402

access_log = logging.getLogger("request_log")


# ===========================================================================
# PART 3 -- The middleware: one JSON access-log line per request
# ===========================================================================
class RequestLogMiddleware:
    """Assign a request_id, time the request, log ONE summary line.

    Django calls __call__ once per request. Everything before
    self.get_response(request) runs on the way IN; everything after it
    runs on the way OUT (view + other middleware already finished).
    """

    def __init__(self, get_response):
        self.get_response = get_response      # the rest of the stack

    def __call__(self, request):
        # --- way in -------------------------------------------------------
        # Honor an id from the caller (gateway/frontend) or mint a fresh one.
        # This is how ONE user action gets traced across MANY services.
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        request.request_id = request_id       # views could log with it too
        started = time.perf_counter()

        # --- run the actual view (and everything else) ----------------------
        # If the view raises, Django's exception handling turns it into a
        # 500 response BEFORE control returns here -- so we still log it.
        response = self.get_response(request)

        # --- way out --------------------------------------------------------
        duration_ms = round((time.perf_counter() - started) * 1000, 1)
        access_log.info(
            "request_handled",
            extra={                            # extra= -> JSON fields
                "request_id": request_id,
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        # Echo the id back -- callers/support can quote it when reporting bugs.
        response["X-Request-ID"] = request_id
        return response


# ===========================================================================
# PART 4 -- Three tiny views to exercise the log
# ===========================================================================
def ok(request):
    """The happy path: fast 200."""
    return JsonResponse({"message": "hello", "request_id": request.request_id})


def slow(request):
    """Simulates a slow dependency (DB, external API). Watch duration_ms."""
    time.sleep(1.2)
    return JsonResponse({"message": "that took a while", "request_id": request.request_id})


def boom(request):
    """An unhandled bug. Django logs the traceback; we still log the 500."""
    raise ValueError("simulated bug: inventory count went negative")


urlpatterns = [
    path("ok", ok),
    path("slow", slow),
    path("boom", boom),
]


# ===========================================================================
# PART 5 -- Entry point (manage.py, minus the file)
# ===========================================================================
if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    print("=" * 70)
    print("Django request-logging demo (LLD-39)")
    print("  start:  python3 django_request_logging.py runserver 127.0.0.1:8039 --noreload")
    print("  try:    curl -i http://127.0.0.1:8039/ok")
    print("          curl -i http://127.0.0.1:8039/slow")
    print("          curl -i http://127.0.0.1:8039/boom")
    print("          curl -i -H 'X-Request-ID: my-trace-123' http://127.0.0.1:8039/ok")
    print("  watch THIS terminal: one JSON line per request.")
    print("=" * 70)
    execute_from_command_line(sys.argv)
