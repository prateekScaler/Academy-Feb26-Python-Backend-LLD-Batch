# Email Service — Django + Celery + Redis

A tiny, real email service that demonstrates the one idea this class is about:

> **An HTTP request enqueues a "send welcome email" job and returns INSTANTLY,
> while a Celery worker sends the mail off the request thread — with retries,
> exponential backoff, a dead-letter path, and idempotency.**

If you have already run `pure_python_queue.py` (the from-scratch, no-dependency
version), this is the same story told with the tools you'd actually use in
production. Nothing here is magic once you've seen the pure-Python one.

---

## The moving parts

```
   Browser / curl                 Redis                    Celery worker
  ┌──────────────┐   .delay()   ┌────────┐   picks up    ┌──────────────┐
  │  POST /signup│ ───────────▶ │ broker │ ────────────▶ │ send_welcome │
  │  (Django)    │ ◀─────────── │ (queue)│               │   _email     │
  └──────────────┘   returns    └────────┘               └──────┬───────┘
        202 "queued" in ~5 ms                                    │
        (does NOT wait for the email!)                           ▼
                                                    console backend prints
                                                    the email to THIS log
```

- **Django** (`emails/views.py`) is the **producer**. `signup()` calls
  `send_welcome_email.delay(email)` and returns `202 {"status":"queued"}`
  immediately. It never touches SMTP.
- **Redis** is the **broker** — the queue that holds jobs until a worker is free.
- **Celery worker** (`emails/tasks.py`) is the **consumer**. It runs
  `send_welcome_email` off the request thread.
- **Email backend** is Django's **console backend**, so a "sent" email is just
  printed to the worker's terminal. No SMTP account needed. (See
  `config/settings.py` for the 6 lines that swap in real SMTP for production.)

### The demo's "magic" email addresses

The task decides what happens based on the address, so you can trigger every
path on demand:

| Address                | What happens                                             | Proves            |
|------------------------|----------------------------------------------------------|-------------------|
| `normal@example.com`   | sends on the first try                                   | happy path        |
| `fail@example.com`     | fails twice (transient), then succeeds on attempt 3      | retry + backoff   |
| `poison@example.com`   | always fails → after 4 attempts lands in `DeadLetter`    | dead-letter queue |
| any address, sent twice| second send is skipped                                   | idempotency       |

---

## Prerequisites

- Python 3.10+
- Redis installed (`redis-server` on your PATH). Any recent version is fine.

---

## Run it live (copy-paste, in order)

You'll use **three terminals**. Do steps 1–3 once; then keep A and B running.

### 0. (once) create a virtualenv and install deps

```bash
cd email_service_django
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

> The `venv/` folder is git-ignored — never commit it.

### 1. Start Redis (the broker)

In its own terminal (or as a background service):

```bash
redis-server
```

Leave it running. (If port 6379 is busy, run `redis-server --port 6390` and set
`export CELERY_BROKER_URL=redis://localhost:6390/0` in terminals A and B below.)

### 2. Create the database tables

```bash
python manage.py makemigrations      # already committed; safe to re-run (no-op)
python manage.py migrate
```

You should see `Applying emails.0001_initial... OK`. This creates the
`SentEmail` (idempotency ledger) and `DeadLetter` tables in a local `db.sqlite3`.

### 3. Terminal A — start the Celery worker (the consumer)

```bash
celery -A config worker -l info
```

**What you should SEE:** a banner listing the broker
(`transport: redis://localhost:6379/0`), the registered task
(`. emails.tasks.send_welcome_email`), and finally `celery@... ready.` The
worker is now sitting idle, waiting for jobs. Keep this terminal visible —
this is where all the action prints.

> **macOS note:** if the worker crashes the moment a task runs with an error
> about `fork()` / `__NSPlaceholderDate`, start it with the fork-safety guard:
> ```bash
> OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES celery -A config worker -l info
> ```

### 4. Terminal B — start the web server (the producer)

```bash
python manage.py runserver
```

Serves on `http://127.0.0.1:8000/`. Open `/` in a browser for a help page.

### 5. Terminal C — hit the endpoint and WATCH terminal A

```bash
# happy path — returns instantly, then A prints the email
curl -i "http://127.0.0.1:8000/signup/?email=normal@example.com"

# retry + backoff — A prints "retry ... in 1s", "... in 2s", then "sent on attempt 3"
curl -i "http://127.0.0.1:8000/signup/?email=fail@example.com"

# dead-letter — A prints 4 failing attempts, then "[dead-letter] giving up"
curl -i "http://127.0.0.1:8000/signup/?email=poison@example.com"

# idempotency — send normal@ again; A prints "already sent -- skipping duplicate"
curl -i "http://127.0.0.1:8000/signup/?email=normal@example.com"
```

---

## What each step proves

**The response is instant (the whole point).** Every `curl` above returns
`HTTP/1.1 202 Accepted` with `{"status": "queued", ...}` in a few milliseconds —
*before* the email is sent. Note the word is `queued`, not `sent`: at the moment
the HTTP response leaves, nothing has been emailed yet. The request thread did
the cheap part (drop a message on Redis) and immediately moved on. Compare this
to sending inline: the user's browser would block for as long as the SMTP
handshake takes, and a slow or down mail server would make your whole site feel
slow or throw 500s.

**Watch terminal A to see the work happen later:**

- `normal@` → a printed email block (`Subject: Welcome to Scaler!` …) followed by
  `[sent] welcome email delivered to normal@example.com on attempt 1`.
- `fail@` → `[retry] ... failed on attempt 1 ... retrying in 1s`, then
  `... attempt 2 ... retrying in 2s`, then finally `[sent] ... on attempt 3`.
  The gap between retries **doubles** — that's exponential backoff, which stops a
  struggling mail server from being hammered.
- `poison@` → four failing attempts (backoff 1s, 2s, 4s), then
  `[dead-letter] giving up on poison@example.com after 4 attempts`. Crucially the
  worker does **not** crash and does **not** loop forever — the bad job is parked
  in the `DeadLetter` table for a human to inspect.
- `normal@` again → `[idempotent] normal@example.com already sent -- skipping
  duplicate`. Because delivery is *at-least-once*, duplicates are possible, so the
  task guards every send with a unique key in `SentEmail`.

### Peek at the tables

```bash
python manage.py shell -c "from emails.models import SentEmail, DeadLetter; \
print('sent:', list(SentEmail.objects.values_list('email', flat=True))); \
print('dead:', list(DeadLetter.objects.values_list('email','attempts')))"
```

You'll see `normal@` and `fail@` in `SentEmail`, and `poison@` in `DeadLetter`.

---

## Why the settings are the way they are

In `config/settings.py`:

- `CELERY_TASK_ACKS_LATE = True` — a job is acknowledged (removed from Redis)
  only **after** it finishes, not when it's picked up. So if a worker dies
  mid-job, Redis still has it and another worker retries → *at-least-once*
  delivery. This is exactly why `send_welcome_email` must be idempotent.
- `CELERY_WORKER_PREFETCH_MULTIPLIER = 1` — each worker holds one job at a time
  instead of greedily buffering a batch, so a crash can strand at most one job
  and the retry/ack story stays honest and easy to watch.
- `EMAIL_BACKEND = console` — "sends" by printing, so the demo needs no SMTP.

---

## Files

```
email_service_django/
├── manage.py                 # Django CLI
├── requirements.txt          # django, celery, redis
├── config/
│   ├── __init__.py           # imports the Celery app so @shared_task registers
│   ├── celery.py             # builds the Celery app; broker = Redis
│   ├── settings.py           # ALL config, incl. CELERY_* and EMAIL_BACKEND
│   ├── urls.py               # / and /signup/
│   └── wsgi.py
└── emails/
    ├── apps.py
    ├── models.py             # SentEmail (idempotency) + DeadLetter
    ├── tasks.py              # send_welcome_email: retry + backoff + DLQ + idempotent
    ├── views.py              # signup(): .delay() then return 202 immediately
    └── migrations/0001_initial.py
```

## Cleanup

Stop the worker and server with `Ctrl-C`. The generated `db.sqlite3`, `venv/`,
and `__pycache__/` are all git-ignored — safe to delete anytime.
