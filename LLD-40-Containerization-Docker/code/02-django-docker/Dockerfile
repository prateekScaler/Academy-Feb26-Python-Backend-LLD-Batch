# ============================================================================
# LLD-40, Tier 2: THE teaching Dockerfile -- every best practice, in order,
# with the reason next to it. Tier 1 showed the mechanics; this is the shape
# you should copy for real Python services.
# ============================================================================

# --- 1. Pinned, slim base image ---------------------------------------------
# Never `FROM python:latest`. `latest` is a moving target: the build that
# worked today silently gets Python 3.13 next month and breaks. Pin a
# version you actually tested. "slim" drops compilers/docs: ~120 MB vs ~1 GB,
# which means faster pulls, faster deploys, less to attack.
FROM python:3.12-slim

# curl is not in slim images; HEALTHCHECK below needs it. Install in one RUN
# and delete the apt cache IN THE SAME LAYER (a later `rm` cannot shrink an
# earlier layer -- layers are append-only).
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# --- 2. THE layer-cache lesson: requirements BEFORE code --------------------
# Docker reuses a cached layer only if the instruction AND the files it
# copies are unchanged -- and a cache miss invalidates every layer BELOW it.
#
# So we copy ONLY requirements.txt first, then pip install. You edit code
# 50 times a day; you edit requirements.txt once a week. With this order,
# 49 of those 50 builds hit the cache for the slow pip-install layer and
# rebuild in ~1 second. Copy the code first (or `COPY . .` here) and EVERY
# code edit re-downloads Django from scratch.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Only now the code -- the layer that changes on every edit sits LAST.
# (.dockerignore keeps venv/, .env, __pycache__/ out of this COPY.)
COPY webapp.py .

# --- 3. Don't run as root ---------------------------------------------------
# Default user in a container is root. A bug that lets an attacker run code
# in your app then runs it as root -- one kernel exploit away from the host.
# Create an unprivileged user and switch to it; everything after this line
# (including CMD) runs as appuser.
RUN useradd --create-home appuser
USER appuser

# --- 4. Documentation + health ----------------------------------------------
# EXPOSE is documentation ("this app listens on 8040") -- it does NOT
# publish the port. Publishing happens at run time with -p 8040:8040.
EXPOSE 8040

# HEALTHCHECK: Docker itself curls /health every 30s and marks the container
# healthy/unhealthy (see the STATUS column of `docker ps`). LLD-39 callback:
# this is the same liveness-probe idea -- "is the process up?" -- now
# enforced by the runtime instead of an external monitor. Orchestrators
# (compose in Tier 3, Kubernetes later) use it to gate traffic and restarts.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -fsS http://localhost:8040/health || exit 1

# --- 5. The command ---------------------------------------------------------
# 0.0.0.0, not 127.0.0.1 -- inside the container, 127.0.0.1 is unreachable
# from outside (webapp.py explains). runserver is fine for class; a real
# deployment would run gunicorn here.
CMD ["python", "webapp.py", "runserver", "0.0.0.0:8040", "--noreload"]
