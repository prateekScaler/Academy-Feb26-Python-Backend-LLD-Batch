# LLD-40 — Containerization: Docker, Compose & Beyond

> **Module 4, session 10 — the finale.** Your service is tested, secure, async, resilient, observable… and it runs on *your* machine. Today we fix the last gap: pack the app, its dependencies and its config contract into one **image** that runs identically on your laptop, CI, and prod — and see how everything from LLD-38/39 (config injection, health checks, stdout logs, saturation metrics) becomes a one-line container feature.

**Supplementary reading:** [`containerization_guide/`](containerization_guide/index.html) — the 7-part reference guide from the Aug'25 batch (history, commands, Docker Desktop alternatives, Dockerfiles, hands-on lab, Kubernetes, cheat sheet) — plus [`docker-basics.html`](docker-basics.html), a one-page fundamentals summary. The interactive class page below is the primary material; these are for revision.

**How to use this class:** open `index.html` for the interactive page — 15 diagrams, 12 think-first scenario quizzes (every quiz sits *before* its topic), and a 📌 scenario on each concept, including a dedicated **"Observing containers"** section that re-tests LLD-39's metrics/alerting through container incidents. Demos live in [`code/`](code/) as three tiers; they need **Docker Desktop** (free), and every command's expected output is documented so you can read along without it.

---

## The problem: "works on my machine"
The code was never the problem — everything *around* it was: Python 3.12 vs 3.9, brew's libjpeg vs the server's, a `.env` with 14 variables vs none. `requirements.txt` pins packages, not the world.
**The fix is the shipping-container move (1956 → 2013):** standardize the *box*, and every port/crane/ship — laptop/CI/cloud — handles any cargo identically. The **image** is the box: app + interpreter + OS libs + config contract, one immutable versioned artifact. A **container** is a running instance of an image; a **registry** (Docker Hub/ECR/GHCR) is the warehouse.

## What a container actually is
Not a small VM. A VM boots a full guest OS per app (minutes, GBs); a container is a **normal process on the host kernel** wearing two kernel tricks:
- **Namespaces** — what it can *see*: its own PID list ("I'm PID 1"), filesystem root, network stack, hostname.
- **cgroups** — what it can *use*: memory cap (then OOM-kill), CPU share — *the LLD-38 bulkhead, kernel edition*.

Run `ps aux` on the host and your "containerized" python process is right there. Isolation ≠ virtualization: VMs simulate hardware; containers lie to a process. That's why 30 containers fit where 4 VMs choke, and why `docker run` takes ~50 ms — there is nothing to boot. (Flip side: a shared kernel is a weaker isolation boundary than a VM — why multi-tenant clouds add gVisor/Firecracker.)

**Plot twist — "Docker on a Mac":** containers are a *Linux-kernel* feature, and macOS/Windows have no namespaces/cgroups. Docker Desktop quietly runs **one hidden Linux VM**, and every container is a process inside *that* (one fixed VM cost, then cheap processes — not one VM per app; also why Mac bind-mount I/O is slow). In prod (Linux) the VM disappears. Two products share the name: **Docker Engine** (Linux daemon, free, what prod runs) vs **Docker Desktop** (Mac/Win app + VM + GUI — *paid for larger companies since 2021*, hence often banned). Free swaps running the same VM+engine: **Rancher Desktop**, **Colima** (`brew install colima`), **Podman**, **WSL2** — your Dockerfiles work unchanged on all of them (OCI standards).

## Images, layers & registries
- An image is a **stack of read-only layers** — each Dockerfile instruction bakes one; layers are content-hashed. Change one line of code → only that thin layer rebuilds and re-ships (`docker push` of a 900 MB image in 2 s — the registry already has the rest). Containers add a thin **writable top layer** that dies with them.
- **Deploys become**: `docker pull app:v43 && docker run`. **Rollback becomes**: `docker run app:v42` — the exact bytes that worked yesterday.
- **Pin your tags** (`python:3.12-slim`, never `:latest`) — same reproducibility rule as pinned requirements (LLD-38).

## The Dockerfile — two lines cause 90% of the pain
```dockerfile
FROM python:3.12-slim              # pinned base — never :latest
WORKDIR /app
COPY requirements.txt .            # deps first…
RUN pip install --no-cache-dir -r requirements.txt   # …so this layer caches
COPY . .                           # code last — it changes hourly
RUN useradd -m appuser
USER appuser                       # never run as root
EXPOSE 8040
HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:8040/health || exit 1
CMD ["python", "webapp.py", "runserver", "0.0.0.0:8040", "--noreload"]
```
1. **The layer cache reads top-down**: the first changed instruction invalidates everything below. `COPY . .` above `pip install` = full reinstall on every code edit (3-min builds); requirements-first = 2-second builds. Order lines least→most frequently changing.
2. **`COPY . .` ships secrets** if you let it: a `.env` baked into a pushed image is *burned* — old layers remain pullable forever (`docker history` walks them); deleting the file and re-pushing fixes nothing. **Rotate the keys**, add `.dockerignore` (venv, `.env`, `.git`, `__pycache__`), and inject secrets at *run* time — the LLD-38 12-factor ladder.

Also in the teaching Dockerfile: non-root `USER` (containers get compromised too), `HEALTHCHECK` (LLD-38's liveness, shipped inside the artifact), one process per container (`CMD`).

- **CMD vs ENTRYPOINT:** CMD = the *default* command (`docker run img sh` **replaces** it — easy debugging); ENTRYPOINT = the *fixed* program (extra args get **appended** — for CLI-tool images). Rule of thumb: app containers just use CMD (exec form); the override behaviour is what interviews probe.
- **Multi-stage builds:** build in a full image (gcc, headers, mess), `COPY --from=builder` only the installed artifacts into a slim runtime stage — 1.1 GB → 180 MB, faster pulls, smaller attack surface.
- **Size hygiene:** prefer `-slim` bases (alpine is smaller but musl-based — wheels may compile from source; try slim first); combine `apt-get install && rm -rf /var/lib/apt/lists/*` in **one** RUN or the cleanup saves nothing (each RUN is a layer).
- **Troubleshooting walls:** container exits instantly = its CMD ended (run servers foreground) · reachable inside but not from the browser = listen on `0.0.0.0` **and** map `-p` · "port already allocated" = usually your own old container · "my change isn't showing" = you ran the old image — rebuild (or bind-mount for dev).

## Running containers: data, config, ports
- **Data:** the writable layer is a post-it note — redeploy and it's gone (the vanished-uploads incident). Anything worth keeping lives in a **volume** (`-v uploads-data:/app/uploads`) or an external store. Containers stay **stateless** — cattle, not pets.
- **Config:** one image, all environments — inject env vars at run time (`docker run -e`, compose `environment:`, k8s ConfigMap/Secret). Never bake per-env images.
- **Ports:** private by default; `-p 8040:8040` opens the one door. Everyday four: `docker ps` / `logs` / `exec -it <c> sh` / `stop`.

## docker-compose: the stack in one file
`web + redis` with a private network (services reach each other **by service name** — compose runs DNS: LLD-38 service discovery, free), one mapped port, a named volume so data survives `down && up` (and resets on `down -v`).
**The trap:** `depends_on` waits for the container to *start*, not for the service to be *ready* — the "connection refused, but only sometimes" race. Fix: a healthcheck on the dependency + `condition: service_healthy` (readiness, LLD-38/39) — plus connection retries in the app (LLD-38 resilience).

## Observing containers — metrics & alerts, the essentials
Last class ended at logs, so the metrics-and-alerting essentials are taught *here*, question-first with the answers drawn as diagrams:
- **Logs:** stdout isn't a convention here, it's the API — `docker logs` → agent → aggregator all tail stdout. A tidy `/var/log/app.log` inside the container is invisible to the whole pipeline (a volume just makes it a *durable* black hole).
- **Percentiles beat averages:** 99 requests at 60 ms + 1 at 3 s still *averages* ~90 ms ("green!") while 1 user in 100 waits 3 seconds — and at ~30 requests/session, ~1 in 4 *sessions* hits that pain. Dashboards graph **p50/p95/p99**, never the average.
- **RED and USE:** **R**ate / **E**rrors / **D**uration per endpoint = the service as users feel it (120 req/s · 0.4% · p95 210 ms). **U**tilization / **S**aturation / **E**rrors = the resources underneath; *saturation = work waiting* is the early warning. They chain: p95 up (RED symptom) → which resource is saturated (USE cause) — the Friday-sale DB pool at 9/10 is tomorrow's outage, visible today.
- **Alerting in one line:** `errors/requests > 5% FOR 10m → page (+ runbook)` — a user-facing *ratio* + threshold + *duration* (one bad second is normal) + runbook. Slow causes (disk 82%, +1%/day) are tickets, not pages — every false page trains the on-call to ignore the next one.
- **The OOM story:** exit code **137** = 128+9 = SIGKILL at the cgroup memory limit — no traceback, no ERROR log; *only the memory gauge saw it coming* (`docker stats` → cAdvisor → Prometheus; USE applied to cgroups).
- **Health:** a `/health` that only proves "process up" is a rubber stamp. Readiness checks dependencies (Redis down → 503 → stop routing); liveness stays bare (restarts can't fix a dead dependency — don't restart-loop).

## Beyond one machine: Kubernetes (the teaser)
Compose is single-host by design — no scheduler, no failover, no rolling deploys. Kubernetes' core move: **declare desired state** ("3 replicas of web:v42"), a control loop makes reality match — node dies at 3 AM, replacement scheduled, nobody paged. You already know its vocabulary: Service = discovery DNS (LLD-38), probes = liveness/readiness (LLD-38/39), ConfigMap/Secret = 12-factor config (LLD-38), limits = cgroups (today). **Don't start there:** compose or a managed platform (Cloud Run/Fly/Render) first; k8s when multi-host problems are real.
**60-second history:** chroot (1979) → jails → namespaces+cgroups (Google) → **Docker assembles them + the image format (2013)** → **Kubernetes** (Borg, 2014, founds CNCF) → **OCI** standard (2015) → containerd/Podman/serverless containers — Docker-the-company faded; docker-the-format won.

## Containers in the AI era
- **Agent sandboxes:** LLM-written code is untrusted by definition — it runs in a throwaway container (no network, tight cgroup caps, deleted after). Today's namespaces/cgroups lesson *is* the safety model of every code-interpreter tool.
- **Model images:** inference server + CUDA + weights, one pinned image — "works on my GPU" is the old disease, same cure; scale = replicas behind a Service.
- **Cost bulkheads:** per-model cgroup limits + LLD-39 cost-burn alerts.
- **Reproducible experiments:** a training run pinned as an image is rerunnable in a year.

---

## `code/` — three tiers (need Docker Desktop; expected output documented at every step)

| Tier | What | The lesson |
|---|---|---|
| [`01-first-container/`](code/01-first-container/) | 15-line script + minimal Dockerfile | build/run; same image, different env (`-e GREETING=…`) — 12-factor live; container hostnames |
| [`02-django-docker/`](code/02-django-docker/) | single-file Django app, production Dockerfile | layer-cache order (watch CACHED on rebuild), `.dockerignore`, non-root, HEALTHCHECK, JSON logs on stdout via `docker logs` |
| [`03-compose-stack/`](code/03-compose-stack/) | Django + Redis page-counter | service-name DNS, readiness-gated `depends_on`, named volume (counter survives `down`/`up`, resets on `down -v`), `/health` flips 503 when Redis dies |

```bash
cd code/01-first-container && docker build -t hello-lld40 . && docker run hello-lld40
cd ../02-django-docker     && docker build -t webapp . && docker run -p 8040:8040 webapp
cd ../03-compose-stack     && docker compose up --build
```
> The Python apps themselves are verified natively (Python 3.14 + local Redis); Docker steps ship with documented expected output — run them on any machine with Docker Desktop.

## Homework
1. **Tier 1:** run it; run the image twice and explain why the hostnames differ.
2. **Tier 2:** edit one line of `webapp.py`, rebuild, read which layers say CACHED. Then move `COPY . .` above pip install and feel the difference.
3. **Tier 3:** counter → `down`/`up` (survives — why?) → `down -v` (resets — why?) → kill Redis, watch `/health` flip to 503.
4. **Break it:** add `mem_limit: 64m` to web and load it until the OOM-kill. Find the 137. Which gauge would have warned you?
5. **Ship it:** containerize *your* project with the production Dockerfile shape. That artifact is portfolio-grade.

**🏆 Module 4 complete:** testing → auth → async → cloud-native → observability → containers. That's the modern backend toolkit — run, broken, and fixed by your own hands. Next: revision, interview drills, capstone.
