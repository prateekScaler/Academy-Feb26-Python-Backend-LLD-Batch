"""
================================================================================
 pure_python_queue.py  --  A message queue, built from scratch, in ~1 file.
================================================================================

Run it:
    python3 pure_python_queue.py

No pip installs. No Redis. No Celery. No Django. Just the Python standard
library. The point is to SEE the machinery that "real" queues (Celery + Redis,
RabbitMQ, SQS, Kafka) hide from you, so that when we use the real thing later
in this class it is not magic.

--------------------------------------------------------------------------------
 THE MENTAL MODEL
--------------------------------------------------------------------------------
A message queue has three roles:

    PRODUCER  --->  [ BROKER / QUEUE ]  --->  CONSUMER(s)
    (puts jobs)      (holds jobs until       (pull jobs and do the
                      someone is free)        actual work)

The whole reason this pattern exists: the producer should be able to say
"please send this welcome email" and immediately move on WITHOUT waiting for
the email to actually be sent. The slow work happens later, on a different
thread/process (a "worker"). In a web app the producer is your HTTP request
handler -- you do NOT want the user's browser spinning for 3 seconds while an
SMTP server wakes up.

Here the BROKER is a `queue.Queue` (thread-safe, built in) and the CONSUMERS
are a handful of worker THREADS. In production the broker is a separate service
(Redis) and the consumers are separate PROCESSES, but the ideas are identical.

--------------------------------------------------------------------------------
 WHAT THIS FILE DEMONSTRATES  (each is narrated live in the terminal)
--------------------------------------------------------------------------------
 1. WORK QUEUE            one job -> handled by EXACTLY ONE of N competing
                          workers (load sharing).
 2. RETRIES + BACKOFF     a flaky job fails a couple of times, then succeeds;
                          the wait between retries doubles (exponential backoff).
 3. DEAD-LETTER QUEUE     a "poison" job that can never succeed is parked in a
                          DLQ after its retries are exhausted (instead of
                          looping forever or crashing the worker).
 4. ACK / AT-LEAST-ONCE   a job is only removed from the broker after the worker
                          ACKNOWLEDGES it. If a worker "crashes" before acking,
                          the broker REDELIVERS the job. => delivered at least
                          once, possibly more than once.
 5. IDEMPOTENCY           because at-least-once means duplicates are possible, a
                          well-behaved consumer keeps an "already done" set keyed
                          by a stable id, so a redelivered/duplicate job is a
                          harmless no-op the second time.

Everything is DETERMINISTIC: whether a job fails is decided by a fixed rule
based on the job's id (not random()), so every run tells the same story and the
final tally is always the same.
================================================================================
"""

import queue
import threading
import time

# --------------------------------------------------------------------------
# Tunables -- kept tiny so the whole demo finishes in a couple of seconds.
# --------------------------------------------------------------------------
NUM_WORKERS = 3          # how many competing consumers pull from the broker
MAX_RETRIES = 3          # transient failures allowed before a job is dead-lettered
FLAKY_FAILS = 2          # the flaky job fails this many times, then succeeds
BASE_BACKOFF = 0.05      # seconds; real delay = BASE_BACKOFF * 2**(attempt-1)
SEND_COST = 0.02         # pretend "sending an email" takes this long (I/O)

START = time.monotonic()
_print_lock = threading.Lock()   # so worker log lines don't interleave mid-line


def log(who, msg):
    """Thread-safe, timestamped print so the narration is readable."""
    with _print_lock:
        elapsed = time.monotonic() - START
        print(f"  [t+{elapsed:5.2f}s] {who:<9} | {msg}")


# --------------------------------------------------------------------------
# Two kinds of failure, so the code can react differently to each.
# --------------------------------------------------------------------------
class TransientError(Exception):
    """A temporary failure (SMTP timeout, network blip). Worth RETRYING."""


class WorkerCrash(Exception):
    """
    Simulates the worker PROCESS dying mid-job -- e.g. someone runs `kill`, or
    the machine loses power -- AFTER the side effect happened but BEFORE it
    could acknowledge the job. The broker never heard "done", so it will
    REDELIVER. This is what makes a queue "at-least-once".
    """


# --------------------------------------------------------------------------
# The Message envelope. In a real broker this is a serialized blob; here it is
# a small object that also carries its own bookkeeping.
# --------------------------------------------------------------------------
class Message:
    def __init__(self, key, kind, payload, max_retries=MAX_RETRIES):
        self.key = key            # STABLE idempotency id (survives redelivery)
        self.kind = kind          # "ok" | "flaky" | "poison" | "crashy"
        self.payload = payload    # e.g. the email address
        self.max_retries = max_retries
        self.attempts = 0         # processing attempts so far (drives backoff)
        self.deliveries = 0       # times handed to a consumer (>1 == redelivered)

    def __repr__(self):
        return f"<{self.key}>"


# --------------------------------------------------------------------------
# The Broker. A thin, teaching-sized wrapper around queue.Queue that adds the
# three things a real broker gives you but a bare Queue does not:
#   - explicit ACK (a job isn't "done" until the consumer says so)
#   - REDELIVERY (unacked work comes back)
#   - a DEAD-LETTER list for poison messages
# It also tracks how many messages are still "in flight" so main() knows when
# every job has reached a terminal state (acked or dead-lettered).
# --------------------------------------------------------------------------
class Broker:
    def __init__(self):
        self.q = queue.Queue()         # the actual FIFO buffer of ready messages
        self.dlq = []                  # dead-letter queue (poison messages)
        self._cond = threading.Condition()
        self._outstanding = 0          # published but not yet acked/dead-lettered

    def publish(self, msg):
        """Producer side: hand a NEW job to the broker."""
        with self._cond:
            self._outstanding += 1
        self.q.put(msg)

    def get(self):
        """Consumer side: block until a message is ready, then deliver it."""
        return self.q.get()

    def ack(self, msg):
        """Consumer says 'I finished this, drop it.' -> terminal state."""
        self._resolve()

    def redeliver(self, msg, delay=0.0):
        """
        Put a message BACK on the queue (used for retries and for redelivery
        after a crash). It is NOT resolved -- it's still outstanding. A positive
        `delay` schedules the re-put for later, which is how a broker implements
        a backoff / visibility timeout without tying up a worker.
        """
        if delay > 0:
            threading.Timer(delay, self.q.put, args=(msg,)).start()
        else:
            self.q.put(msg)

    def dead_letter(self, msg):
        """Give up on a message -- park it in the DLQ. -> terminal state."""
        with self._cond:
            self.dlq.append(msg)
        self._resolve()

    def _resolve(self):
        with self._cond:
            self._outstanding -= 1
            if self._outstanding == 0:
                self._cond.notify_all()

    def wait_until_drained(self):
        """Block main() until every published job has been acked or dead-lettered."""
        with self._cond:
            while self._outstanding > 0:
                self._cond.wait()


# --------------------------------------------------------------------------
# A tiny thread-safe tally so we can print an honest summary at the end.
# --------------------------------------------------------------------------
class Stats:
    def __init__(self):
        self._lock = threading.Lock()
        self.processed = 0     # successful, real sends
        self.retries = 0       # transient failures that were retried
        self.dead = 0          # messages dropped into the DLQ
        self.duplicates = 0    # redelivered/duplicate jobs skipped by idempotency
        self.crashes = 0       # simulated worker crashes (informational)

    def bump(self, field):
        with self._lock:
            setattr(self, field, getattr(self, field) + 1)


# The idempotency store. In real life this is a UNIQUE column in your DB, or a
# Redis SETNX -- something DURABLE and ATOMIC. Here a plain set + a lock plays
# both roles. A key in here means "this job's side effect has already happened."
SEEN = set()
SEEN_LOCK = threading.Lock()


def send_email(msg, who):
    """The actual 'side effect'. Pretend this talks to an SMTP server."""
    time.sleep(SEND_COST)
    log(who, f">>> SENT welcome email to {msg.payload}")


# --------------------------------------------------------------------------
# The consumer logic -- the heart of the demo. One call = one delivery attempt.
# --------------------------------------------------------------------------
def handle(msg, broker, stats, who):
    msg.attempts += 1
    log(who, f"picked up {msg.key}  (delivery #{msg.deliveries}, "
             f"attempt #{msg.attempts}, kind={msg.kind})")

    # ---- (5) IDEMPOTENCY: atomically CLAIM this key before doing any work ----
    # Check-and-set must be atomic, otherwise two workers could both pass the
    # check and both send. The lock here is our stand-in for a DB unique
    # constraint / Redis SETNX.
    with SEEN_LOCK:
        if msg.key in SEEN:
            log(who, f"duplicate {msg.key} -- already processed, skipping "
                     f"(idempotent no-op)")
            stats.bump("duplicates")
            broker.ack(msg)          # nothing to do, but we still must ack it
            return
        SEEN.add(msg.key)            # claim it; we roll this back if we fail

    try:
        # ---- decide the outcome deterministically from the job's kind ----
        if msg.kind == "flaky" and msg.attempts <= FLAKY_FAILS:
            raise TransientError("SMTP 421 -- service temporarily unavailable")
        if msg.kind == "poison":
            raise TransientError("SMTP 550 -- no such mailbox (never works)")

        # ---- the real work ----
        send_email(msg, who)
        stats.bump("processed")

        # ---- (4) simulate a crash AFTER the send but BEFORE the ack ----
        if msg.kind == "crashy" and msg.deliveries == 1:
            raise WorkerCrash("process killed after send, before ack")

        broker.ack(msg)              # tell the broker: done, drop it
        log(who, f"ACK {msg.key}")

    except WorkerCrash as exc:
        # We already ran the side effect AND recorded the idempotency key, so we
        # deliberately do NOT roll back SEEN. The broker never got the ack, so
        # it will hand the SAME message to someone again -> at-least-once.
        log(who, f"** {who} CRASHED on {msg.key}: {exc}")
        log(who, f"   broker never received an ACK -> it will REDELIVER {msg.key}")
        stats.bump("crashes")
        broker.redeliver(msg)

    except TransientError as exc:
        # The work did NOT happen, so un-claim the key -- the retry must be
        # allowed to actually run again (otherwise the retry would look like a
        # duplicate and skip forever).
        with SEEN_LOCK:
            SEEN.discard(msg.key)

        if msg.attempts > msg.max_retries:
            # ---- (3) retries exhausted -> DEAD-LETTER QUEUE ----
            log(who, f"{msg.key} failed attempt #{msg.attempts}: {exc}")
            log(who, f"   retries exhausted (max_retries={msg.max_retries}) "
                     f"-> DEAD-LETTER {msg.key}")
            stats.bump("dead")
            broker.dead_letter(msg)
        else:
            # ---- (2) retry with EXPONENTIAL BACKOFF ----
            backoff = BASE_BACKOFF * (2 ** (msg.attempts - 1))
            log(who, f"{msg.key} failed attempt #{msg.attempts}: {exc}")
            log(who, f"   will RETRY in {backoff:.3f}s "
                     f"(backoff doubles each time)")
            stats.bump("retries")
            broker.redeliver(msg, delay=backoff)


def worker(name, broker, stats, shutdown):
    """A competing consumer. Loops forever pulling jobs until it sees the
    shutdown sentinel."""
    while True:
        msg = broker.get()
        if msg is shutdown:          # poison-pill sentinel -> time to stop
            return
        msg.deliveries += 1
        handle(msg, broker, stats, name)


def main():
    print(__doc__)
    print("=" * 78)
    print(f" Starting {NUM_WORKERS} worker threads (competing consumers)...")
    print("=" * 78)

    broker = Broker()
    stats = Stats()
    SHUTDOWN = object()              # unique sentinel object == "stop"

    # Start the consumers first so they are ready and waiting.
    workers = []
    for i in range(NUM_WORKERS):
        t = threading.Thread(target=worker,
                             args=(f"worker-{i+1}", broker, stats, SHUTDOWN))
        t.start()
        workers.append(t)

    # ---- The PRODUCER: enqueue a burst of jobs, then return immediately. ----
    # Note how fast this loop is: publishing does NOT wait for any email to be
    # sent. That is the entire selling point of a queue.
    jobs = [
        Message("welcome-1",  "ok",     "aisha@example.com"),
        Message("welcome-2",  "ok",     "bhavya@example.com"),
        Message("welcome-3",  "ok",     "chen@example.com"),
        Message("flaky-7",    "flaky",  "dan@example.com"),      # fails 2x, then ok
        Message("poison-99",  "poison", "nobody@invalid.invalid"),  # never works -> DLQ
        Message("crashy-5",   "crashy", "esha@example.com"),     # crash before ack
        Message("welcome-2",  "ok",     "bhavya@example.com"),   # DUPLICATE enqueue
    ]
    log("producer", f"enqueuing {len(jobs)} jobs and returning instantly...")
    for job in jobs:
        broker.publish(job)
    log("producer", "done enqueuing. (In a web app, the HTTP response returns HERE.)")
    print("-" * 78)

    # Wait for every job to reach a terminal state, then stop the workers.
    broker.wait_until_drained()
    for _ in workers:
        broker.q.put(SHUTDOWN)
    for t in workers:
        t.join()

    # ---------------------------- SUMMARY ---------------------------------
    print("-" * 78)
    print(" SUMMARY")
    print("-" * 78)
    print(f"   processed (real sends)       : {stats.processed}")
    print(f"   retried (transient failures) : {stats.retries}")
    print(f"   dead-lettered (poison)       : {stats.dead}")
    print(f"   duplicates skipped (idempot.): {stats.duplicates}")
    print(f"   simulated worker crashes     : {stats.crashes}")
    print()
    if broker.dlq:
        print("   DEAD-LETTER QUEUE contents (need a human / manual replay):")
        for m in broker.dlq:
            print(f"     - {m.key}  ->  {m.payload}   (gave up after "
                  f"{m.attempts} attempts)")
    else:
        print("   DEAD-LETTER QUEUE: (empty)")
    print("=" * 78)
    print(" Takeaways:")
    print("   * The producer never waited for a send -- work happened on the")
    print("     workers. That is how a web request can return in milliseconds.")
    print("   * Failures are normal. Retries + backoff absorb the transient")
    print("     ones; the DLQ quarantines the hopeless ones so one bad message")
    print("     can't block or crash the pipeline.")
    print("   * ACK + redelivery gives 'at-least-once', so duplicates WILL")
    print("     happen -- which is exactly why the consumer must be idempotent.")
    print("=" * 78)


if __name__ == "__main__":
    main()
