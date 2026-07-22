# LLD-37 — Email Service & Intro to Message Queues

> **Module 4, session 7 — going asynchronous.** The auth arc is done; now the shift every real backend makes: **stop doing slow work on the request thread.** We start from a bug you *will* ship — a signup that hangs while it sends an email — and build up to message queues: producers, consumers, retries, dead-letter queues, and idempotency, ending in a runnable **email service in Django + Celery + Redis**.

**How to use this class:** open `index.html` for the interactive page (diagrams, scenario quizzes, and a live demo runbook). Everything is beginner-first. Two runnable demos live in [`code/`](code/): a 100-line **pure-Python queue** you can read top to bottom with zero installs, and a production-shaped **Django + Celery + Redis** email service.

---

## Why not send email on the request thread?
A signup view that calls `send_welcome_email()` *inline* (before returning) is a trap:
- The SMTP call takes seconds; the user watches a spinner for an email they don't need *right now*.
- If the mail server is slow or down, the request **times out → 500**, even though the account was created fine.
- Web threads are scarce. One parked on a slow SMTP socket serves nobody else — a signup burst can exhaust the pool and take the **whole site** down.

The email is **slow, flaky, and not urgent** — three properties that say "don't do this inline." Return as soon as the *critical* work is done, and hand the email to something else.

## First — what are your options? (the decision ladder)
A message queue isn't the only way to run work later, and not always the right one. Climb the ladder from simplest to most robust, and pick deliberately:
1. **Inline (synchronous)** — do it in the handler before responding. Great for *fast, must-finish* work (charge the card, write the row). Bad for slow/flaky/not-urgent work — it blocks the user.
2. **Background thread** — spawn a thread in the web process and return. Fine for *fire-and-forget, low-stakes* work. But a crash loses it, no retries, no visibility, and it can't scale across machines.
3. **DB table + poller (the "poor-man's queue")** — write the job as a row, a worker polls the table. **Durable** and you already have a DB. Great for low volume / delay-tolerant work (nightly digests, retrying webhooks). The catch: *polling latency* (a job waits for the next tick), *DB contention* (workers fight over row locks on the same hot rows, load lands on your primary DB), and you *hand-roll* locking/retries/backoff/dead-lettering that a broker ships for free.
4. **Message queue** — a purpose-built broker + worker fleet with durability, retries, backoff, DLQ, and horizontal scaling already solved. Reach for it when work is slow/flaky **and** must-not-be-lost, and/or high-volume, and/or needs independent scaling & visibility.

**The decision, out loud:** must it finish before you reply? → *inline*. Can you lose it, tiny volume? → *thread*. Must survive restarts, modest volume? → *DB table*. Slow + flaky + must-not-lose + busy? → *message queue*.

## Message queues — producer, broker, consumer
- **Producer** — creates work (your web view) and drops a small message on the queue, then returns.
- **Broker / Queue** — the durable middle-man (Redis, RabbitMQ, SQS…) that stores messages until a consumer takes them, surviving restarts.
- **Consumer / Worker** — a separate process that pulls messages and does the slow work; add more workers to go faster.

What the middle-man buys you: **decoupling** (deploy/scale each side independently), **load leveling** (a spike becomes a deep queue drained at a steady pace), **durability** (a crash doesn't vaporize pending work), and **independent scaling** (scale the bottleneck, not everything). Mental model: the queue is a **to-do list that survives restarts** — producers add, workers cross off, neither needs the other online at the same moment.

## Getting it there reliably: acks, retries & dead letters
- **Acknowledgements** — the broker holds a message until the worker sends an **ack**. Crash before ack → **redeliver**. Nothing is lost — this is **at-least-once delivery** (and why duplicates are normal).
- **Retries with exponential backoff** — most failures are transient; retry after a *growing* delay (1s, 2s, 4s…) so a struggling dependency can recover. Add **jitter** so a mass of jobs don't retry in the same instant.
- **Dead-letter queue (DLQ)** — after *N* attempts a job that never succeeds (corrupt payload, invalid address) is shunted to a separate queue instead of being retried forever. Nothing lost, workers freed, a human can inspect it. A poison message with infinite retries is a slow-motion outage.

## Duplicates are normal → make consumers idempotent
At-least-once means your consumer *will* see some messages twice. You don't fix that at the broker — you make the effect **idempotent** (doing it twice = doing it once). The standard tool is an **idempotency key**: give each job a stable unique id, check whether it was already handled before doing the effect, and record the key *atomically* (a DB unique constraint is bulletproof). This turns at-least-once **delivery** into effectively-once **processing** — the outcome you actually wanted.

## Two shapes, two myths
- **Work queue** (point-to-point): one message → *exactly one* of the competing workers. Use for *tasks to do once*; scale by adding workers.
- **Pub/Sub** (fan-out): one event → *every* subscriber gets its own copy. Use when one event triggers many independent reactions (`order.placed` → email + analytics + inventory + push, each decoupled).
- **Ordering myth** — a work queue with competing workers gives *no* global order. Strict order costs throughput (single consumer, or per-key partitioning). Usually you need *per-entity* order, not total order — route by key.
- **Exactly-once myth** — exactly-once *delivery* over a network is effectively impossible (a lost ack looks like lost work). You pick **at-least-once + idempotent consumers**, which gives exactly-once *processing*.

## The broker landscape & Celery
| Broker | In one line | Reach for it when… |
|---|---|---|
| **Redis** | in-memory store that doubles as a fast, simple queue | you want to start quickly; great default for Celery |
| **RabbitMQ** | dedicated AMQP broker with rich routing | you need flexible routing, priorities, per-message controls |
| **Kafka** | a distributed, replayable **log** (not a classic queue) | high-volume event streams; consumers rewind & replay |
| **AWS SQS** | fully-managed cloud queue, nothing to run | you're on AWS and want zero-ops queuing (built-in DLQ) |

**Celery** is the standard Python task queue: write a function, mark it `@shared_task`, call `.delay(...)` to enqueue (returns in ~1ms). A broker holds the job; a **Celery worker** pulls and runs it, with retries/backoff/DLQ built in. `acks_late=True` means a mid-send crash gets the job redelivered.

## Kafka, one level deeper (optional)
- **A partition is an append-only *log*, not a queue.** A **topic** splits into **partitions**; each partition is an ordered log where producers append at the tail and every message gets an **offset**. Nothing is deleted on read — each consumer tracks *its own* offset, so it can rewind and **replay**.
- **Consumer groups** are how Kafka parallelises: within a group, each partition → *exactly one* consumer, so parallelism caps at the **partition count** (a 4th consumer on a 3-partition topic sits idle). A *different* group reads the same partitions independently (the pub/sub side).
- **Terms:** broker (a server) / cluster (many brokers) / key (same key → same partition → ordered) / replication (leader + followers, so a broker can die) / retention (kept for N days regardless of reads) / rebalance (reshuffle partitions when a consumer joins/leaves).
- **Common confusions:** it's a *log* not a queue; more consumers ≠ more throughput past #partitions; ordering is *per-partition* only (use a key); it's high-throughput, not low-latency RPC (consumers poll); exactly-once is subtle — the everyday answer is at-least-once + idempotent consumers; modern Kafka uses **KRaft**, not ZooKeeper.
- **Play with it:** [Aiven](https://aiven.io/tools/kafka-visualization) and [SoftwareMill](https://softwaremill.com/kafka-visualisation/) both offer interactive in-browser Kafka visualisers.

---

## `code/` — two runnable demos

> Run order and expected output are spelled out in the interactive page's **Demo** section and in each project's own notes.

| What | Runs with | Demonstrates |
|---|---|---|
| [`pure_python_queue.py`](code/pure_python_queue.py) | `python3` (no installs) | A queue built from `queue.Queue` + worker threads: retries with backoff, a poison job that dead-letters, and a duplicate skipped by an idempotency key |
| [`pubsub_demo.py`](code/pubsub_demo.py) | `python3` (no installs) | Work-queue (one message → one consumer) vs pub/sub fan-out (one event → every subscriber), side by side |
| [`email_service_django/`](code/email_service_django/) | Django + Celery + Redis | A signup endpoint that enqueues a task and **returns instantly**; a worker sends the mail off-thread, **retries** a flaky address, **dead-letters** a permanent failure, and **skips duplicates** |

```bash
# the real thing — four terminals
cd code/email_service_django
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
redis-server                       # terminal A: the broker
celery -A config worker -l info    # terminal B: the consumer
python manage.py runserver         # terminal C: the producer
# terminal D:
curl "http://127.0.0.1:8000/signup/?email=alice@example.com"   # returns {"status":"queued"} instantly
# then watch terminal B send it; try fail@ (retries) and poison@ (dead-letters)
```

## Homework
1. **Toy queue:** run `pure_python_queue.py`. Drop `max_retries` to 1 and watch a recoverable job land in the DLQ instead. Remove the idempotency check and watch a redelivered job double-send.
2. **Email service:** run the Django + Celery + Redis demo end to end. Curl `alice@`, `fail@`, `poison@` and narrate the worker log for each. Fire `alice@` twice; confirm the second is skipped.
3. **Stretch:** add an `order.placed` pub/sub example — one publish, two subscriber tasks (email + analytics) — and confirm both run from a single event.
4. **Think:** where in a system you've built would a queue have helped (image processing? reports? webhooks?). Write down the producer, the message, and the consumer for one.

**Next class — Cloud-native patterns (adapted for Python):** now that work runs in the background across many processes, how do they find config, discover each other, and stay resilient when a dependency wobbles?
