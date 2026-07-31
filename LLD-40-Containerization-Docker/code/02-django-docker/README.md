# Tier 2 — Containerize a Real Django App

One Django service in one file (`webapp.py`), one best-practice `Dockerfile`,
one `.dockerignore`. The goals of this tier:

1. See the **layer cache** save you a full dependency install (the
   requirements-before-code trick).
2. Run the app as a **non-root** user with a **HEALTHCHECK**.
3. Watch **`docker logs`** — stdout is THE log stream (LLD-39 callback).

## 0. Run it natively first (no Docker needed)

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 webapp.py runserver 0.0.0.0:8040 --noreload
```

From a second terminal — real output from our machine:

```text
$ curl http://127.0.0.1:8040/
{"service": "lld40-webapp", "hostname": "Prateek.local", "requests_served": 1}
$ curl http://127.0.0.1:8040/
{"service": "lld40-webapp", "hostname": "Prateek.local", "requests_served": 2}
$ curl http://127.0.0.1:8040/health
{"status": "ok"}
```

And on the server's stdout, exactly ONE JSON line per request:

```text
{"event": "http_request", "method": "GET", "path": "/", "status": 200, "duration_ms": 0.4}
{"event": "http_request", "method": "GET", "path": "/", "status": 200, "duration_ms": 0.1}
{"event": "http_request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.1}
```

## 1. Build — and build AGAIN (the cache lesson)

```bash
docker build -t django-lld40 .
```

**Expected output, first build (run on a machine with Docker):**

```text
[+] Building 18.7s (11/11) FINISHED
 => [1/6] FROM docker.io/library/python:3.12-slim                  2.8s
 => [2/6] RUN apt-get update && apt-get install -y ... curl        6.1s
 => [3/6] WORKDIR /app                                             0.0s
 => [4/6] COPY requirements.txt .                                  0.0s
 => [5/6] RUN pip install --no-cache-dir -r requirements.txt       8.9s
 => [6/6] COPY webapp.py .                                         0.0s
 => exporting to image                                             0.4s
```

Now **edit `webapp.py`** (change the SERVICE string, anything) and rebuild:

```bash
docker build -t django-lld40 .
```

**Expected output, second build — read the CACHED lines:**

```text
[+] Building 1.1s (11/11) FINISHED
 => CACHED [2/6] RUN apt-get update && apt-get install -y ... curl 0.0s
 => CACHED [3/6] WORKDIR /app                                      0.0s
 => CACHED [4/6] COPY requirements.txt .                           0.0s
 => CACHED [5/6] RUN pip install --no-cache-dir -r requirements... 0.0s
 => [6/6] COPY webapp.py .                                         0.0s
```

18.7s down to 1.1s. `requirements.txt` did not change, so the pip-install
layer is `CACHED` — only the final `COPY webapp.py .` reran. This is WHY the
Dockerfile copies requirements before code. Flip the order and every code
edit costs you the full pip install.

## 2. Run it, publish the port

```bash
docker run -d --name web -p 8040:8040 django-lld40
```

`-d` = detached (background). `-p 8040:8040` = "host port 8040 -> container
port 8040" — THIS publishes the port; EXPOSE in the Dockerfile was only
documentation.

**Expected (run on a machine with Docker):**

```text
$ curl http://127.0.0.1:8040/
{"service": "lld40-webapp", "hostname": "9c4f1a2b3d5e", "requests_served": 1}
$ curl http://127.0.0.1:8040/health
{"status": "ok"}
```

Note `hostname` is now the container id, not your machine — same lesson as
Tier 1, but this time it is a real web service answering.

## 3. docker logs — stdout is the log stream

```bash
docker logs web
```

**Expected output (run on a machine with Docker):**

```text
Performing system checks...

System check identified no issues (0 silenced).
Starting development server at http://0.0.0.0:8040/
{"event": "http_request", "method": "GET", "path": "/", "status": 200, "duration_ms": 0.4}
{"event": "http_request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.1}
```

The app never opened a log file. It printed to stdout, and Docker captured
it. That is the container logging contract from LLD-39: app -> stdout ->
platform ships it to the aggregator. (`docker logs -f web` tails it live.)

## 4. Look inside — who is the process running as?

```bash
docker exec -it web sh
```

**Expected, inside the container (run on a machine with Docker):**

```text
$ whoami
appuser
$ ps aux
USER       PID %CPU %MEM    VSZ   RSS ... COMMAND
appuser      1  0.2  1.1  45120 38924 ... python webapp.py runserver 0.0.0.0:8040 --noreload
appuser     14  0.0  0.1   2576  1024 ... sh
$ exit
```

Two things worth staring at: the app is PID 1 (a container runs ONE process,
not a whole OS), and it runs as `appuser`, not root — that is the `USER`
instruction doing its job.

Also check the healthcheck's verdict:

```bash
docker ps
```

```text
CONTAINER ID   IMAGE          STATUS                   PORTS                    NAMES
9c4f1a2b3d5e   django-lld40   Up 2 minutes (healthy)   0.0.0.0:8040->8040/tcp   web
```

`(healthy)` = Docker has been curling /health every 30s and it keeps
returning 200.

## 5. Stop and clean up

```bash
docker stop web      # SIGTERM, then SIGKILL after 10s
docker rm web        # remove the stopped container
```
