"""
LLD-39 | Logging & Monitoring -- Demo 2: structured_logging.py
==============================================================

"Logs a MACHINE can query" -- structured (JSON) logging with structlog.

    Needs:    pip install structlog     (see requirements.txt / venv)
    Run it:   python3 structured_logging.py

The story so far (from logging_basics.py): our lines have timestamps,
levels and request ids. But they are still SENTENCES. To find slow
payments you end up writing regexes over English text. Fragile.

Structured logging flips the model: a log line is not a sentence,
it is an EVENT with FIELDS -- one JSON object per line. Log
aggregators (ELK, Grafana Loki, Datadog, CloudWatch) then treat your
logs like a database table you can filter, group and graph:

    event="payment_failed" AND amount_inr > 1000     <- a QUERY, not a regex
"""

import time
import uuid

import structlog

BAR = "=" * 70


# ===========================================================================
# PART 1 -- The same event, told twice
# ===========================================================================
print(BAR)
print("PART 1: the same event -- as a sentence vs as data")
print(BAR)

# The classic, human-first line (what logging_basics.py produced):
print('\ntext: 2026-07-25 19:04:11 INFO payment ok order=4021 user=88 amount=499 in 231ms')

# The structured, machine-first version of the SAME event:
print('json: {"event": "payment_succeeded", "order_id": 4021, "user_id": 88,'
      ' "amount_inr": 499, "duration_ms": 231, "level": "info",'
      ' "timestamp": "2026-07-25T19:04:11Z"}')

print("""
Same information. But ask each version a real production question:
  "average payment duration today?"     text -> regex + prayer
                                        json -> avg(duration_ms), one query
  "all failures above 1000 INR?"        text -> grep and hope the wording
                                             never changed
                                        json -> filter on two FIELDS
Fields survive rewording; regexes do not. That is the whole pitch.
""")


# ===========================================================================
# PART 2 -- Configure structlog (minimal, line-by-line)
# ===========================================================================
print(BAR)
print("PART 2: configuring structlog -- a pipeline of processors")
print(BAR)
print()

# structlog works as a PIPELINE: each log call passes an event-dict through
# the processors below, top to bottom, and the last one renders the output.
structlog.configure(
    processors=[
        # 1) stamp the level onto the event dict: {"level": "info"}
        structlog.processors.add_log_level,
        # 2) stamp an ISO-8601 UTC timestamp: {"timestamp": "...Z"}
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        # 3) render the final dict as ONE JSON object per line
        structlog.processors.JSONRenderer(),
    ],
)
# That's it. Three processors: level -> timestamp -> JSON out.

log = structlog.get_logger()

# Keyword arguments become JSON fields. No string formatting anywhere.
log.info("service_started", service="checkout", version="1.4.2")


# ===========================================================================
# PART 3 -- bind(): attach context ONCE, it appears on EVERY line
# ===========================================================================
print()
print(BAR)
print("PART 3: bind() -- say request_id ONCE, get it on every line")
print(BAR)
print()

def run_checkout(user_id: int, amount_inr: int, card_ok: bool) -> None:
    """A mini checkout flow. Watch what we do NOT have to repeat."""

    # bind() returns a logger that carries these fields from now on.
    # This is Chapter 6 of logging_basics.py (contextvar filter) -- but
    # built into the library and per-field instead of hand-rolled.
    rlog = log.bind(
        request_id=uuid.uuid4().hex[:12],
        user_id=user_id,
    )

    started = time.perf_counter()                    # for duration_ms later

    rlog.info("cart_loaded", items=3, amount_inr=amount_inr)
    rlog.info("payment_started", gateway="razorpay")

    if card_ok:
        rlog.info(
            "payment_succeeded",
            amount_inr=amount_inr,
            duration_ms=round((time.perf_counter() - started) * 1000, 2),
        )
    else:
        # Failures carry WHY (error field) and HOW LONG we spent finding out.
        rlog.error(
            "payment_failed",
            error="card_declined",
            gateway_code="E1042",
            amount_inr=amount_inr,
            duration_ms=round((time.perf_counter() - started) * 1000, 2),
        )


# A happy checkout -- note request_id + user_id ride along on every line,
# yet none of the log calls inside run_checkout() mention them:
run_checkout(user_id=88, amount_inr=499, card_ok=True)

print()  # visual gap between the two flows

# A failing checkout -- different request_id, error fields on the last line:
run_checkout(user_id=91, amount_inr=1999, card_ok=False)

print("""
Read the failing flow above: same request_id on all three lines (grep one
request's story), and the last line is a QUERYABLE fact:
    event="payment_failed" AND amount_inr > 1000  -> alert the payments team.
""")


# ===========================================================================
# PART 4 -- Where do these lines GO in production?
# ===========================================================================
print(BAR)
print("PART 4: the production note")
print(BAR)
print("""
In containers/Kubernetes you do NOT open log files yourself:

    your app  --prints JSON to stdout-->  container runtime captures it
              --log agent (Fluent Bit / promtail / Datadog agent) ships it-->
              aggregator (ELK / Loki / CloudWatch) indexes every FIELD

Your only job: one JSON object per line, on stdout. The platform does
collection, storage, search and retention. That is why this whole file
never called open() -- stdout IS the log file now.
""")
