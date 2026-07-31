# LLD-40 — Containerization (Docker): Code Demos

Three tiers, in order. Each folder is self-contained with its own README,
commands, and expected outputs.

| Tier | Folder | One line |
|------|--------|----------|
| 1 | `01-first-container/` | One tiny script, host vs container: hostname, Python, and env-config all change while the code does not. |
| 2 | `02-django-docker/` | A real single-file Django app + the best-practice Dockerfile: layer cache, non-root user, HEALTHCHECK, stdout logs. |
| 3 | `03-compose-stack/` | web + redis with docker-compose: service discovery by DNS, healthy-not-just-started, and volumes that outlive containers. |
| 4 | `04-dockerfile-line-by-line/` | The guide's Django Dockerfile as SEVEN step-files — build one instruction at a time, watch `docker history` grow a layer per line, catch the cache, prove EXPOSE opens nothing, and settle CMD vs ENTRYPOINT. |

## Install Docker

Get **Docker Desktop** (macOS / Windows) from
https://www.docker.com/products/docker-desktop/ — it bundles the engine,
the `docker` CLI, and `docker compose`. On Linux, install Docker Engine +
the compose plugin from https://docs.docker.com/engine/install/.
Verify with:

```bash
docker --version
docker compose version
```

## No Docker? Read along anyway

Every README marks its Docker output blocks as
**"expected output (run on a machine with Docker)"** — captured so you can
follow the whole story without installing anything. And every tier's app
also runs natively (`python3 ...`, plus a local `redis-server` for Tier 3);
the native runs shown in the READMEs are REAL outputs from our machine.
