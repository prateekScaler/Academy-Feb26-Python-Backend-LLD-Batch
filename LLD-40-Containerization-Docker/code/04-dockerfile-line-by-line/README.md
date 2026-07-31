# Dockerfile, line by line — the live demo kit

Companion to the guide page **`containerization_guide/04_dockerfile.html`**. Seven Dockerfiles, one per instruction of the guide's "Simple Django Dockerfile" — build them in order and *watch the image grow a layer at a time*. Needs Docker Desktop (or Colima/Rancher); every expected output is noted so you can read along without it.

```
04-dockerfile-line-by-line/
├── manage.py · mysite/          ← a minimal real Django project (one JSON view)
├── requirements.txt             ← one dep (Django), on purpose
├── Dockerfile.1 … Dockerfile.7  ← the SAME file, one instruction added per step
├── Dockerfile                   ← the finished file (= step 7)
├── .dockerignore                ← what "COPY . ." must never pick up
└── cmd-vs-entrypoint/           ← the override-behaviour mini-demo
```

**Before the containers — prove the app is ordinary** (any machine with Python):
```bash
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
python manage.py runserver 8000        # then: curl localhost:8000
# → {"message": "hello from Django", "hostname": "<YOUR-laptop>", "python": "3.x.y"}
```
Remember that `hostname` — it changes once we're inside the box.

---

## The seven steps

Each `Dockerfile.N` has its build + observe commands in its own header comment. The storyline:

| Step | New line | Build | The observation that lands the lesson |
|---|---|---|---|
| 1 | `FROM python:3.12-slim` | `docker build -f Dockerfile.1 -t step1 .` | `docker run --rm step1 cat /etc/os-release` → **Debian, on your Mac**; `python -V` → the *image's* Python |
| 2 | `WORKDIR /app` | `… -f Dockerfile.2 -t step2 .` | `docker run --rm step2 pwd` → `/app`; `ls -la` → **empty** |
| 3 | `COPY requirements.txt .` | `… -t step3 .` | `ls -la` → *only* requirements.txt — one file, on purpose (cache!) |
| 4 | `RUN pip install …` | `… -t step4 .` *(slow once — watch pip run at BUILD time)* | `docker run --rm step4 pip list` → Django is IN the image. **Rebuild the same command → all CACHED, ~1 s** |
| 5 | `COPY . .` | `… -t step5 .` | `ls -la` → the project. **Edit `mysite/urls.py`, rebuild → steps 1–4 CACHED, only this layer rebuilds** |
| 6 | `EXPOSE 8000` | `… -t step6 .` | `docker inspect --format '{{.Config.ExposedPorts}}' step6` → `map[8000/tcp:{}]` — but run without `-p` and `curl` **fails**: documentation, not a door |
| 7 | `CMD [ … runserver 0.0.0.0:8000 ]` | `… -t step7 .` | `docker run --rm -p 8000:8000 step7` → `curl localhost:8000` → same JSON, but `hostname` is now the **container id** and `python` is the **image's**. `docker run -it step7 sh` → CMD replaced |

Two cross-cutting commands to run at *every* step:
```bash
docker history stepN     # watch the layer stack grow, one instruction = one layer
docker images | head     # watch the size: step1 ~130 MB → step4 jumps (+Django) → step5 barely moves
```

## CMD vs ENTRYPOINT (2 minutes, in `cmd-vs-entrypoint/`)
```bash
cd cmd-vs-entrypoint
docker build -f Dockerfile.cmd -t democmd .
docker run --rm democmd                    # → python received argv: ['args.py']
docker run --rm democmd echo hijacked      # → hijacked            (CMD fully REPLACED)

docker build -f Dockerfile.entrypoint -t demoentry .
docker run --rm demoentry                  # → python received argv: ['args.py']
docker run --rm demoentry other.py --x     # → python runs other.py --x   (ENTRYPOINT kept, args APPENDED)
```
One sentence to close it: **CMD is a suggestion, ENTRYPOINT is a decision.** App containers want the suggestion.

## Cleanup
```bash
docker rmi step1 step2 step3 step4 step5 step6 step7 democmd demoentry
```
> App verified natively (venv + runserver + curl). Docker steps documented; run them on any machine with Docker Desktop / Colima / Rancher.
