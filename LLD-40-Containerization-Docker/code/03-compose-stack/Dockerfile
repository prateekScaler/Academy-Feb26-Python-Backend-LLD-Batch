# ============================================================================
# LLD-40, Tier 3: same best-practice shape as Tier 2 -- read THAT Dockerfile
# for the full line-by-line lesson. Comments here only mark what is new.
# ============================================================================

FROM python:3.12-slim
# curl for the HEALTHCHECK (slim images do not ship it)
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# requirements BEFORE code = the pip layer stays cached across code edits
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY webapp.py .

RUN useradd --create-home appuser
USER appuser

EXPOSE 8040

# NEW vs Tier 2: /health now checks Redis too (readiness-style), so an
# unreachable Redis flips this container to "unhealthy" in `docker ps` --
# and compose's depends_on/service_healthy machinery keys off the same idea.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -fsS http://localhost:8040/health || exit 1

CMD ["python", "webapp.py", "runserver", "0.0.0.0:8040", "--noreload"]
