# Tier 1 — Your First Container

One ~15-line script, two worlds. Run `app.py` on your host, then inside a
container, and watch the hostname, the Python version, and the config change
while the CODE stays identical. That is the whole pitch of Docker in one demo.

## 0. Run it on the host first (no Docker needed)

```bash
python3 app.py
```

Real output from our machine (yours will show YOUR hostname / Python):

```text
==============================================
  Hello from LLD-40!
==============================================
hostname : Prateek.local
python   : 3.14.5
GREETING : hello from the host
```

Note the three lines: your machine's name, your Python, the default greeting.
Remember them — every one of them changes inside the container.

## 1. Build the image

```bash
docker build -t hello-lld40 .
```

`-t hello-lld40` gives the image a name (a "tag"). The `.` says "the build
context is this folder" — that is where `COPY app.py .` reads from.

**Expected output (run on a machine with Docker):**

```text
[+] Building 4.2s (8/8) FINISHED
 => [internal] load build definition from Dockerfile              0.0s
 => [internal] load .dockerignore                                 0.0s
 => [1/3] FROM docker.io/library/python:3.12-slim                 2.9s
 => [internal] load build context                                 0.0s
 => => transferring context: 812B                                 0.0s
 => [2/3] WORKDIR /app                                            0.1s
 => [3/3] COPY app.py .                                           0.0s
 => exporting to image                                            0.1s
 => => naming to docker.io/library/hello-lld40                    0.0s
```

See `[1/3]`, `[2/3]`, `[3/3]`? Those are the three LAYERS from the
Dockerfile: FROM, WORKDIR, COPY. Run the build a second time without changing
anything and every step says `CACHED` — that cache is Tier 2's big lesson.

## 2. Run a container from the image

```bash
docker run hello-lld40
```

**Expected output (run on a machine with Docker):**

```text
==============================================
  Hello from LLD-40!
==============================================
hostname : 3f2a9c81d04e
python   : 3.12.11
GREETING : hello from the host
```

Compare with the host run:

| line     | on the host        | in the container                  |
|----------|--------------------|-----------------------------------|
| hostname | `Prateek.local`    | `3f2a9c81d04e` (the container id) |
| python   | `3.14.5` (yours)   | `3.12.11` (whatever the image ships) |
| GREETING | default            | default (we fix that next)        |

The container did not "see" your machine. It saw its own little world:
its own hostname, its own Python. Same script, different universe.

## 3. Same image, different config (the 12-factor callback)

```bash
docker run -e GREETING="config from outside" hello-lld40
```

**Expected output (run on a machine with Docker):**

```text
==============================================
  Hello from LLD-40!
==============================================
hostname : 8b1c22f5a970
python   : 3.12.11
GREETING : config from outside
```

We did NOT rebuild the image. `-e` injects an environment variable at RUN
time. This is 12-factor rule III from LLD-38: config lives in the
environment, so ONE image serves dev, staging, and prod — only the env
changes.

## 4. Run it twice — containers are disposable

```bash
docker run hello-lld40
docker run hello-lld40
```

**Expected output (run on a machine with Docker) — note the hostname line:**

```text
hostname : 5e77d1b2c3aa     <- first run
hostname : 91f04a6b8de2     <- second run
```

Each `docker run` creates a brand-new container with a brand-new identity
(the hostname IS the container id). Nothing carried over between the two
runs. Containers are cattle, not pets — which is exactly why anything you
want to KEEP must live outside the container (Tier 3's volume lesson).

## Clean up

```bash
docker ps -a          # see the exited containers piling up
docker container prune    # delete all stopped containers (asks first)
```
