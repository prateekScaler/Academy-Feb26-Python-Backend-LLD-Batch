"""
LLD-40 | Containerization -- Tier 3: webapp.py (web + Redis, via compose)
=========================================================================

Tier 2's app, with ONE change that changes everything: the page-view counter
now lives in REDIS, not in Python memory.

Why that matters:
  - Tier 2's in-process counter dies with the container and cannot be shared.
  - State in Redis survives web restarts, and TEN web containers would all
    share the same count. Stateless web + stateful store = the scalable shape.

Where is Redis? We do NOT hardcode it. We read REDIS_HOST from the env:

  - Natively:    defaults to localhost (run your own redis-server).
  - In compose:  docker-compose.yml sets REDIS_HOST=redis -- the SERVICE
    NAME. Compose gives every service a DNS entry named after it, so "redis"
    simply resolves to the redis container's IP. That is service discovery
    by DNS -- the exact idea from LLD-38, provided free by Docker networks.

    Needs:    pip install -r requirements.txt   +   a reachable Redis
    Run it:   python3 webapp.py runserver 0.0.0.0:8040 --noreload
    Try it:   curl http://127.0.0.1:8040/        # counter: 1, 2, 3, ...
              curl -i http://127.0.0.1:8040/health   # 200, or 503 if Redis is down
"""

import json
import logging
import os
import socket
import sys
import time

import django
import redis
from django.conf import settings
from django.http import JsonResponse

SERVICE = "lld40-compose-web"

# ---------------------------------------------------------------------------
# Config from the environment (12-factor III). In docker-compose.yml the
# `environment:` block sets REDIS_HOST=redis; on your laptop the defaults
# point at a local redis-server.
# ---------------------------------------------------------------------------
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))

# One client for the whole process. decode_responses=True -> str, not bytes.
# Short timeouts so /health answers fast even when Redis is gone.
r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    socket_connect_timeout=2,
    socket_timeout=2,
    decode_responses=True,
)

# ---------------------------------------------------------------------------
# Django settings + the same stdout-JSON logging as Tier 2 (see Tier 2 for
# the full commentary; the rule is: containers log to stdout, full stop).
# ---------------------------------------------------------------------------
settings.configure(
    DEBUG=False,
    SECRET_KEY="dev-only-not-secret",
    ALLOWED_HOSTS=["*"],
    ROOT_URLCONF=__name__,
    MIDDLEWARE=[f"{__name__}.stdout_request_log"],
    LOGGING={
        "version": 1,
        "disable_existing_loggers": False,
        "loggers": {"django.server": {"handlers": [], "propagate": False}},
    },
)
django.setup()

log = logging.getLogger(SERVICE)
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler(sys.stdout))


def stdout_request_log(get_response):
    """One JSON line per request, to stdout -- `docker compose logs` shows it."""
    def middleware(request):
        started = time.monotonic()
        response = get_response(request)
        log.info(json.dumps({
            "event": "http_request",
            "service": SERVICE,
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
def home(request):
    # INCR is atomic on the Redis server: even with many web containers
    # hammering it concurrently, every hit gets a unique, in-order number.
    views = r.incr("page_views")
    return JsonResponse({
        "service": SERVICE,
        "hostname": socket.gethostname(),   # WHICH web container answered
        "page_views": views,                # SHARED count, lives in Redis
    })


def health(request):
    # READINESS-style check (LLD-39 callback): not just "is the process up?"
    # but "can I actually serve traffic?" -- and we cannot serve without
    # Redis. A load balancer / orchestrator seeing 503 stops sending traffic
    # here until the dependency is back. (Tier 2's /health was the LIVENESS
    # flavor: process-only, no dependency checks.)
    try:
        r.ping()
        return JsonResponse({"status": "ok", "redis": "connected"})
    except redis.exceptions.RedisError as exc:
        return JsonResponse(
            {"status": "degraded", "redis": f"unreachable: {type(exc).__name__}"},
            status=503,
        )


from django.urls import path                       # noqa: E402
urlpatterns = [
    path("", home),
    path("health", health),
]

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
