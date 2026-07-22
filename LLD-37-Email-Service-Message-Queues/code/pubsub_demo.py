"""
================================================================================
 pubsub_demo.py  --  WORK QUEUE  vs.  PUB/SUB FAN-OUT
================================================================================

Run it:
    python3 pubsub_demo.py

No installs, stdlib only. This file exists to kill one very common confusion:
"a queue" and "pub/sub" are NOT the same thing. They answer different questions.

--------------------------------------------------------------------------------
 THE ONE-LINE DIFFERENCE
--------------------------------------------------------------------------------
   WORK QUEUE   : one message  ->  handled by EXACTLY ONE of the consumers.
                  (goal: share load across workers; each job done once.)

   PUB / SUB    : one event    ->  a COPY delivered to EVERY subscriber.
                  (goal: broadcast a fact; each subscriber reacts independently.)

Picture ordering food at a counter:

   WORK QUEUE  = a stack of tickets and 3 cooks. Each ticket is grabbed by ONE
                 cook. Three cooks => you get through the tickets ~3x faster.
                 Nobody cooks the same ticket twice.

   PUB / SUB   = the manager announces "table 5 just paid!" over the intercom.
                 The kitchen hears it, the accountant hears it, the loyalty-points
                 system hears it. ONE announcement, EVERYONE reacts. Adding a
                 listener does not make anything faster -- it adds a reaction.

Real email-service tie-in:
   * Sending the welcome email is WORK-QUEUE work: exactly one worker should
     send it (send it twice => the user gets two emails).
   * "user.signed_up" is a great PUB/SUB EVENT: the email service sends a
     welcome mail, analytics logs a signup, and the CRM starts an onboarding
     drip -- three independent reactions to one fact.
================================================================================
"""

import queue
import threading
import time

START = time.monotonic()
_print_lock = threading.Lock()


def log(who, msg):
    with _print_lock:
        elapsed = time.monotonic() - START
        print(f"  [t+{elapsed:5.2f}s] {who:<14} | {msg}")


# ============================================================================
# PART 1 -- WORK QUEUE  (competing consumers; each message handled once)
# ============================================================================
def work_queue_demo():
    print("=" * 78)
    print(" PART 1 -- WORK QUEUE: one shared queue, 3 competing workers")
    print("   Expect: the 9 jobs get SPLIT across the workers; each job runs ONCE.")
    print("=" * 78)

    q = queue.Queue()
    NUM_WORKERS = 3
    NUM_JOBS = 9
    SHUTDOWN = object()

    # Each worker keeps a private tally of which jobs IT handled, so at the end
    # we can prove the work was shared and nothing was done twice.
    handled = {f"worker-{i+1}": [] for i in range(NUM_WORKERS)}

    def worker(name):
        while True:
            job = q.get()
            if job is SHUTDOWN:
                q.task_done()
                return
            # A single .get() removes the item from the queue, so no other
            # worker can ever see this same job. That is the whole guarantee.
            handled[name].append(job)
            log(name, f"handling {job}")
            time.sleep(0.03)          # pretend the job takes a little work
            q.task_done()

    threads = [threading.Thread(target=worker, args=(f"worker-{i+1}",))
               for i in range(NUM_WORKERS)]
    for t in threads:
        t.start()

    # PRODUCER: drop 9 jobs onto the ONE shared queue.
    log("producer", f"publishing {NUM_JOBS} jobs onto ONE shared queue")
    for i in range(1, NUM_JOBS + 1):
        q.put(f"job-{i}")

    q.join()                          # wait until every job is done
    for _ in threads:
        q.put(SHUTDOWN)
    for t in threads:
        t.join()

    print("-" * 78)
    total = 0
    for name, jobs in handled.items():
        total += len(jobs)
        log(name, f"handled {len(jobs)} jobs: {jobs}")
    print(f"\n   => {total} jobs done in total across {NUM_WORKERS} workers "
          f"(each job exactly once).")
    print(f"   => Notice NO job appears under two workers. Work was SHARED,")
    print(f"      not duplicated. Add more workers => finish faster.\n")


# ============================================================================
# PART 2 -- PUB/SUB FAN-OUT  (every subscriber gets its OWN copy of each event)
# ============================================================================
class EventBus:
    """
    A minimal publish/subscribe broker. The trick that makes it "fan-out":
    every subscriber gets its OWN queue. Publishing an event pushes a COPY of
    that event into each subscriber's queue, so subscribers never compete for
    or steal each other's messages.
    """
    def __init__(self):
        self._subscribers = {}        # name -> that subscriber's private Queue

    def subscribe(self, name):
        inbox = queue.Queue()
        self._subscribers[name] = inbox
        return inbox

    def publish(self, event):
        log("event-bus", f"publishing '{event}' -> fan-out to "
                          f"{len(self._subscribers)} subscribers")
        # ONE event in, N copies out -- one per subscriber.
        for inbox in self._subscribers.values():
            inbox.put(event)


def pubsub_demo():
    print("=" * 78)
    print(" PART 2 -- PUB/SUB: one event bus, 3 independent subscribers")
    print("   Expect: EVERY subscriber receives EVERY event (its own copy).")
    print("=" * 78)

    bus = EventBus()
    SHUTDOWN = object()

    # Three unrelated services all care about signups, for different reasons.
    subscriber_names = ["email-service", "analytics", "crm-onboarding"]
    received = {name: [] for name in subscriber_names}

    def subscriber(name, inbox):
        while True:
            event = inbox.get()
            if event is SHUTDOWN:
                return
            received[name].append(event)
            log(name, f"reacted to '{event}'")
            time.sleep(0.02)

    inboxes = {name: bus.subscribe(name) for name in subscriber_names}
    threads = [threading.Thread(target=subscriber, args=(name, inboxes[name]))
               for name in subscriber_names]
    for t in threads:
        t.start()

    # PUBLISHER: emit 3 events. Each one fans out to ALL subscribers.
    events = ["user.signed_up:aisha", "user.signed_up:bhavya", "user.signed_up:chen"]
    for e in events:
        bus.publish(e)
        time.sleep(0.03)              # small gap just so the log reads cleanly

    # Let everyone drain, then shut down.
    time.sleep(0.2)
    for name in subscriber_names:
        inboxes[name].put(SHUTDOWN)
    for t in threads:
        t.join()

    print("-" * 78)
    for name in subscriber_names:
        log(name, f"received {len(received[name])} events: {received[name]}")
    print(f"\n   => {len(events)} events were published, but each subscriber saw")
    print(f"      ALL {len(events)} of them. 3 events * 3 subscribers = 9 reactions.")
    print(f"   => Nobody 'stole' an event from anyone else. That is fan-out.\n")


def main():
    print(__doc__)
    work_queue_demo()
    pubsub_demo()
    print("=" * 78)
    print(" SIDE BY SIDE")
    print("-" * 78)
    print("   WORK QUEUE : 9 jobs  + 3 workers      = 9 units of work  (SHARED)")
    print("   PUB / SUB  : 3 events + 3 subscribers = 9 reactions      (COPIED)")
    print()
    print("   Same count, opposite meaning:")
    print("     - More WORKERS on a work queue  => the SAME work finishes faster.")
    print("     - More SUBSCRIBERS on a topic   => MORE total work (one per sub).")
    print("=" * 78)


if __name__ == "__main__":
    main()
