# Tier 3 — Multi-Container Stack with docker-compose

Two containers, one command. `web` (our Django app) + `redis` (the official
image), wired together by `docker-compose.yml`. The three lessons:

1. **Service discovery by DNS** — the app reaches Redis at hostname
   `redis`, the service NAME (LLD-38 callback).
2. **"started" is not "ready"** — `depends_on` + `condition: service_healthy`.
3. **Volumes** — the counter survives `down` + `up`, and dies with `down -v`.

## 0. Run it natively first (no Docker needed)

Terminal 1 — a scratch Redis on a non-default port:

```bash
redis-server --port 6390 --dir /tmp
```

Terminal 2 — the app, pointed at it via env (12-factor config):

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
REDIS_HOST=localhost REDIS_PORT=6390 python3 webapp.py runserver 0.0.0.0:8040 --noreload
```

Terminal 3 — real output from our machine:

```text
$ curl http://127.0.0.1:8040/
{"service": "lld40-compose-web", "hostname": "Prateek.local", "page_views": 1}
$ curl http://127.0.0.1:8040/
{"service": "lld40-compose-web", "hostname": "Prateek.local", "page_views": 2}
$ curl http://127.0.0.1:8040/
{"service": "lld40-compose-web", "hostname": "Prateek.local", "page_views": 3}
```

Now kill the redis-server (Ctrl+C in terminal 1) and probe /health — real
output:

```text
$ curl -i http://127.0.0.1:8040/health
HTTP/1.1 503 Service Unavailable
{"status": "degraded", "redis": "unreachable: ConnectionError"}
```

Start redis-server again:

```text
$ curl -i http://127.0.0.1:8040/health
HTTP/1.1 200 OK
{"status": "ok", "redis": "connected"}
```

That 503-when-dependency-down behavior is the READINESS check (LLD-39) that
compose's `service_healthy` machinery builds on.

## 1. The whole stack, one command

```bash
docker compose up --build
```

**Expected output (run on a machine with Docker) — note the ORDER:**

```text
[+] Building 1.2s (11/11) FINISHED
[+] Running 3/3
 ✔ Volume "03-compose-stack_redis-data"  Created
 ✔ Container 03-compose-stack-redis-1    Healthy
 ✔ Container 03-compose-stack-web-1      Started
redis-1  | 1:M * Ready to accept connections tcp
web-1    | Performing system checks...
web-1    | Starting development server at http://0.0.0.0:8040/
```

Read that middle block carefully: redis reaches **Healthy** BEFORE web is
even **Started**. That is `depends_on: condition: service_healthy` at work —
without it, compose would fire both at once and web could race a
not-yet-ready Redis. Logs from both containers then interleave, each line
prefixed with its service name (`redis-1 |`, `web-1 |`) — stdout again.

## 2. Hit it — and spot the DNS trick

```bash
curl http://127.0.0.1:8040/
curl http://127.0.0.1:8040/
curl http://127.0.0.1:8040/
```

**Expected (run on a machine with Docker):**

```text
{"service": "lld40-compose-web", "hostname": "d41f7b2a9c0e", "page_views": 1}
{"service": "lld40-compose-web", "hostname": "d41f7b2a9c0e", "page_views": 2}
{"service": "lld40-compose-web", "hostname": "d41f7b2a9c0e", "page_views": 3}
```

The counter lives in the OTHER container. How did web find it? The compose
file set `REDIS_HOST=redis`, and inside the compose network the hostname
`redis` resolves — by DNS — to the redis container. Service NAME = network
name of the service. No IP addresses anywhere in our config.

```bash
docker compose ps
```

```text
NAME                       IMAGE             STATUS                 PORTS
03-compose-stack-redis-1   redis:7-alpine    Up 2 minutes (healthy)   6379/tcp
03-compose-stack-web-1     03-compose-stack-web   Up 2 minutes (healthy)   0.0.0.0:8040->8040/tcp
```

Note redis publishes NO host port — only `web` can reach it, on the private
network. The database is not on the internet. Good.

## 3. The volume lesson: down, up, and down -v

Stop the stack (this REMOVES the containers — their writable layers are gone):

```bash
docker compose down
docker compose up
```

**Expected (run on a machine with Docker):**

```text
$ curl http://127.0.0.1:8040/
{"service": "lld40-compose-web", "hostname": "77e0c9a1b4f2", "page_views": 4}
```

New container (new hostname) — but the counter says **4**, not 1. The
containers died; the named volume `redis-data` did not, and Redis reloaded
its dump from it. State survived because it lived OUTSIDE the container.

Now delete the volume too:

```bash
docker compose down -v        # -v = also remove named volumes
docker compose up
```

```text
$ curl http://127.0.0.1:8040/
{"service": "lld40-compose-web", "hostname": "a2c5e8f1d7b3", "page_views": 1}
```

Back to 1. `down -v` deleted `redis-data`, so Redis started empty. That is
the whole storage model in two commands: **containers are ephemeral, volumes
are where state goes to survive.**

## 4. Clean up

```bash
docker compose down -v
```
