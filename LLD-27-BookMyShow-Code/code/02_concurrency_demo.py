"""
LLD-27 · BookMyShow — the concurrency TOURNAMENT (live demo).

Many users race for ONE seat. Every *correct* approach issues exactly ONE ticket;
the naive one double-books. Same race, swap the approach, watch what happens.

Every approach answers the SAME question a different way:
    "How do we make 'check the seat is free' AND 'take it' one un-interruptible step?"

A tiny RACE_GAP between the read and the write forces the threads to interleave,
so the result is deterministic — not luck.

Run it:
    python3 02_concurrency_demo.py                 # the scoreboard — every approach
    python3 02_concurrency_demo.py --racers 50     # crank up the contention
    python3 02_concurrency_demo.py optimistic       # run ONE, with a live trace

Approach keys:  naive · lock · pessimistic · optimistic · unique · redis
"""

from __future__ import annotations

import sys
import threading
import time
from dataclasses import dataclass

RACE_GAP = 0.02                       # forces threads to interleave: read ... write
_print_lock = threading.Lock()


def say(verbose: bool, msg: str) -> None:
    """Print a trace line (only in single-approach mode), one line at a time."""
    if verbose:
        with _print_lock:
            print(f"      {msg}")


@dataclass
class Seat:
    """The single seat everyone is fighting over."""
    status: str = "AVAILABLE"         # AVAILABLE | BOOKED
    owner: str | None = None
    version: int = 0                  # used only by the optimistic approach


# === The approaches ==========================================================
# Each is a class with one method:  book(user) -> True if THIS user got the seat.

class Naive:
    key, name = "naive", "Naive — no protection"
    when = "never (the bug we're fixing)"

    def __init__(self):
        self.seat = Seat()

    def book(self, user, verbose):
        if self.seat.status == "AVAILABLE":                 # 1. check
            say(verbose, f"{user}: sees AVAILABLE")
            time.sleep(RACE_GAP)                            #    ...others check too
            self.seat.status, self.seat.owner = "BOOKED", user   # 2. take (too late!)
            say(verbose, f"{user}: writes BOOKED (thinks it won!)")
            return True
        return False


class InProcessLock:
    key, name = "lock", "In-process lock (threading.Lock)"
    when = "one process / single server, in-memory"

    def __init__(self):
        self.seat = Seat()
        self.lock = threading.Lock()

    def book(self, user, verbose):
        with self.lock:                                     # one thread at a time
            say(verbose, f"{user}: holds the lock")
            if self.seat.status != "AVAILABLE":
                say(verbose, f"{user}: seat already taken, backs off")
                return False
            time.sleep(RACE_GAP)
            self.seat.status, self.seat.owner = "BOOKED", user
            say(verbose, f"{user}: BOOKED")
            return True


class PessimisticRowLock:
    key, name = "pessimistic", "Pessimistic row lock (SELECT ... FOR UPDATE)"
    when = "one DB, many app servers; high contention"

    def __init__(self):
        self.seat = Seat()
        self.row_lock = threading.Lock()                    # the DB locks THIS row

    def book(self, user, verbose):
        say(verbose, f"{user}: SELECT ... FOR UPDATE (waits its turn)")
        with self.row_lock:                                 # others queue here until COMMIT
            say(verbose, f"{user}: now holds the row lock")
            if self.seat.status != "AVAILABLE":
                say(verbose, f"{user}: row already BOOKED -> ROLLBACK")
                return False
            time.sleep(RACE_GAP)
            self.seat.status, self.seat.owner = "BOOKED", user
            say(verbose, f"{user}: UPDATE -> BOOKED, COMMIT")
            return True


class Optimistic:
    key, name = "optimistic", "Optimistic concurrency (version / CAS)"
    when = "conflicts are RARE; you want speed, no waiting"

    def __init__(self):
        self.seat = Seat()
        self.cas = threading.Lock()                         # guards only the tiny swap

    def book(self, user, verbose):
        seen = self.seat.version                            # 1. read the version, NO lock
        if self.seat.status != "AVAILABLE":
            return False
        say(verbose, f"{user}: read version={seen}, doing work UNLOCKED...")
        time.sleep(RACE_GAP)                                # 2. slow work, still no lock
        with self.cas:                                      # 3. book only if version unchanged
            if self.seat.version == seen and self.seat.status == "AVAILABLE":
                self.seat.status, self.seat.owner = "BOOKED", user
                self.seat.version += 1
                say(verbose, f"{user}: version still {seen} -> BOOKED (now v{seen + 1})")
                return True
        say(verbose, f"{user}: version changed under me -> lost, abort")
        return False


class UniqueConstraint:
    key, name = "unique", "DB UNIQUE(show_id, seat_id) constraint"
    when = "always — the correctness FLOOR under every other approach"

    def __init__(self):
        self.seat = Seat()
        self.booked = set()                                 # the unique index
        self.db = threading.Lock()                          # the DB's INSERT is atomic

    def book(self, user, verbose):
        say(verbose, f"{user}: prepared the booking, doing work UNLOCKED...")
        time.sleep(RACE_GAP)                                # no app lock at all
        with self.db:
            if "seat" in self.booked:                       # the UNIQUE violation
                say(verbose, f"{user}: INSERT -> UNIQUE violation, rejected")
                return False
            self.booked.add("seat")
            self.seat.status, self.seat.owner = "BOOKED", user
            say(verbose, f"{user}: INSERT ok (the DB enforced uniqueness)")
            return True


class RedisLock:
    key, name = "redis", "Distributed lock (Redis SET NX + TTL)"
    when = "many services, no shared DB row to lock"

    def __init__(self):
        self.seat = Seat()
        self.held = False                                   # the lock key in Redis
        self.redis = threading.Lock()                       # SET key NX EX is atomic

    def book(self, user, verbose):
        with self.redis:                                    # try to grab the lock
            if self.held:
                say(verbose, f"{user}: lock already held -> abort")
                return False
            self.held = True
        say(verbose, f"{user}: got the distributed lock")
        try:
            if self.seat.status != "AVAILABLE":
                return False
            time.sleep(RACE_GAP)
            self.seat.status, self.seat.owner = "BOOKED", user
            say(verbose, f"{user}: BOOKED")
            return True
        finally:
            with self.redis:                                # release (real Redis: a TTL too)
                self.held = False


APPROACHES = [Naive, InProcessLock, PessimisticRowLock, Optimistic, UniqueConstraint, RedisLock]
BY_KEY = {a.key: a for a in APPROACHES}


# === The race harness ========================================================
def stampede(approach_cls, racers, verbose):
    """N users hit the SAME seat at once. Returns (approach, list-of-winners)."""
    app = approach_cls()
    winners = []
    add_winner = threading.Lock()
    gate = threading.Barrier(racers)                        # release everyone together

    def go(user):
        gate.wait()
        if app.book(user, verbose):
            with add_winner:
                winners.append(user)

    threads = [threading.Thread(target=go, args=(f"user{i + 1}",)) for i in range(racers)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return app, winners


def run_all(racers):
    print(f"\n  {racers} users race for ONE seat — same stampede, every approach.\n")
    print(f"  {'approach':46} {'tickets':>8}  {'losers':>7}   verdict")
    print("  " + "-" * 84)
    for cls in APPROACHES:
        _, winners = stampede(cls, racers, verbose=False)
        n = len(winners)
        verdict = "✅ exactly one wins" if n == 1 else f"❌ DOUBLE-BOOK ({n} tickets!)"
        print(f"  {cls.name:46} {n:>8}  {racers - n:>7}   {verdict}")
    print("\n  Recommendation — pick by your situation:")
    print("  " + "-" * 84)
    for cls in APPROACHES:
        if cls is not Naive:
            print(f"  • {cls.name:46} -> {cls.when}")
    print("""
  For BookMyShow (hot seats on a blockbuster release, one primary DB):
    1. ALWAYS add a UNIQUE(show_id, seat_id) constraint — the floor nothing gets past.
    2. Hot seats = high contention -> a short PESSIMISTIC row lock (or a brief Redis
       lock) gives a clean "seat taken" instead of optimistic retry-storms.
    3. Use OPTIMISTIC only where clashes are rare (e.g. editing a profile), not on
       the one seat everyone wants.
""")


def run_one(key, racers):
    cls = BY_KEY[key]
    print(f"\n  === {cls.name} ===")
    print(f"  best when: {cls.when}")
    print(f"  {racers} users race for one seat — watch them interleave:\n")
    app, winners = stampede(cls, racers, verbose=True)
    print(f"\n  result: {len(winners)} ticket(s) issued -> {winners}")
    print(f"  seat owner = {app.seat.owner!r}  ·  losers = {racers - len(winners)}")
    if len(winners) == 1:
        print("  ✅ correct — exactly one user got the seat.")
    else:
        print(f"  ❌ DOUBLE-BOOK — {len(winners)} users think they own the seat!\n")


def main():
    args = sys.argv[1:]
    racers = 6
    if "--racers" in args:
        i = args.index("--racers")
        racers = max(2, int(args[i + 1]))
        args = args[:i] + args[i + 2:]

    if args and args[0] in BY_KEY:
        run_one(args[0], racers)
    elif args:
        print(f"unknown approach {args[0]!r}; choose from: {', '.join(BY_KEY)}")
    else:
        run_all(racers)


if __name__ == "__main__":
    main()
