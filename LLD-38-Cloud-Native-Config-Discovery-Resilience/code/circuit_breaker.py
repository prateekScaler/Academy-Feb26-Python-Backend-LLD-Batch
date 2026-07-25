"""
LLD-38  |  Cloud-native patterns (adapted for Python)
=====================================================
DELIVERABLE 1 — A CIRCUIT BREAKER, BUILT FROM SCRATCH (standard library only)

WHY DOES THIS PATTERN EXIST?
----------------------------
Imagine your service ("A") calls another service ("B") over the network.
One day B gets slow or starts throwing errors. If A keeps calling B blindly:

  * every request to A now waits on a doomed call to B (threads/connections pile up),
  * A itself becomes slow and starts failing -> the outage "cascades",
  * B, already on its knees, gets hammered by retries and never recovers.

A CIRCUIT BREAKER is the electrical-panel idea applied to software. When it
detects that B is failing repeatedly, it "trips" (opens) and A stops calling B
for a little while. Calls "fail fast" instead of hanging. After a cooldown the
breaker cautiously lets ONE request through to see if B is healthy again.

THE THREE STATES (this is the whole idea — learn this state machine):

    CLOSED     -> normal. Requests flow through to B.
                  We count CONSECUTIVE failures. Hit the threshold -> trip to OPEN.

    OPEN       -> tripped. We do NOT touch B at all; every call fails fast with
                  CircuitOpenError. This gives B time to breathe. After
                  `recovery_timeout` seconds we move to HALF_OPEN to test the water.

    HALF_OPEN  -> testing. We allow exactly ONE trial request through.
                  If it SUCCEEDS  -> B looks healthy again -> go back to CLOSED (reset).
                  If it FAILS     -> B is still sick       -> go back to OPEN (restart timer).

State diagram:

        (>= failure_threshold failures)
   CLOSED ───────────────────────────────▶ OPEN
     ▲                                       │
     │ (trial succeeds)                      │ (recovery_timeout elapsed)
     │                                       ▼
     └──────────────── HALF_OPEN ◀───────────┘
                          │
                          │ (trial fails)
                          └──────────────────▶ OPEN  (restart the cooldown timer)

We build it by hand so the state machine is completely transparent. In real
life you'd use a battle-tested library (pybreaker, resilience4j, Polly, Hystrix,
Envoy/Istio at the mesh level) — see resilient_client.py for the library version.
"""

import time
import threading


# ---------------------------------------------------------------------------
# A dedicated exception so callers can tell "the breaker refused" apart from
# "the dependency itself errored". Fallback logic often keys off this type.
# ---------------------------------------------------------------------------
class CircuitOpenError(Exception):
    """Raised when the breaker is OPEN and refuses to call the dependency."""
    pass


# The three states. Plain strings keep the narrated demo output readable.
CLOSED = "CLOSED"
OPEN = "OPEN"
HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    """
    A minimal, thread-safe circuit breaker.

    Parameters
    ----------
    failure_threshold : int
        How many CONSECUTIVE failures (while CLOSED) trip the breaker to OPEN.
    recovery_timeout : float
        How many seconds to stay OPEN (failing fast) before we allow a single
        HALF_OPEN trial call.
    name : str
        Just a label for the narrated logs.
    """

    def __init__(self, failure_threshold=3, recovery_timeout=2.0, name="B"):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name

        # --- mutable state (guarded by the lock below) ---
        self._state = CLOSED
        self._consecutive_failures = 0
        # We use time.monotonic() (a clock that only ever moves forward and is
        # immune to NTP / system-clock changes) rather than time.time().
        # _opened_at marks WHEN we tripped to OPEN, so we can measure the cooldown.
        self._opened_at = 0.0

        # A single lock makes the state transitions atomic. For a teaching demo
        # we even hold it across the wrapped call, which serializes everything
        # and guarantees only ONE trial runs in HALF_OPEN. In a high-throughput
        # production breaker you would NOT hold a lock during the network call;
        # you'd instead hand out a single "trial permit" and call outside the lock.
        self._lock = threading.Lock()

    # -- tiny helper so every timestamp goes through one place --
    @staticmethod
    def _now():
        return time.monotonic()

    @property
    def state(self):
        with self._lock:
            return self._state

    # -----------------------------------------------------------------------
    # The heart of the breaker. Wrap ANY callable with this.
    # -----------------------------------------------------------------------
    def call(self, fn, *args, **kwargs):
        with self._lock:
            # STEP 1: If we're OPEN, has the cooldown elapsed? If so, promote to
            # HALF_OPEN so the request below becomes our single trial.
            if self._state == OPEN:
                elapsed = self._now() - self._opened_at
                if elapsed >= self.recovery_timeout:
                    self._state = HALF_OPEN
                    print(f"      [breaker:{self.name}] cooldown of "
                          f"{self.recovery_timeout}s elapsed "
                          f"({elapsed:.2f}s) -> state OPEN -> HALF_OPEN "
                          f"(allowing ONE trial call)")
                else:
                    # Still cooling down: fail fast WITHOUT touching the dependency.
                    remaining = self.recovery_timeout - elapsed
                    raise CircuitOpenError(
                        f"circuit '{self.name}' is OPEN; failing fast "
                        f"(~{remaining:.2f}s until a trial is allowed)"
                    )

            # STEP 2: We are CLOSED or HALF_OPEN -> actually attempt the call.
            trial = self._state == HALF_OPEN
            try:
                result = fn(*args, **kwargs)
            except Exception as exc:
                self._on_failure(trial, exc)
                raise
            else:
                self._on_success(trial)
                return result

    # -- called while holding the lock --
    def _on_success(self, trial):
        if trial:
            # A HALF_OPEN trial succeeded: the dependency looks healthy again.
            print(f"      [breaker:{self.name}] trial SUCCEEDED "
                  f"-> state HALF_OPEN -> CLOSED (circuit reset)")
            self._state = CLOSED
        # Any success in CLOSED clears the failure streak.
        self._consecutive_failures = 0

    # -- called while holding the lock --
    def _on_failure(self, trial, exc):
        if trial:
            # A HALF_OPEN trial failed: dependency still sick. Re-open and
            # restart the cooldown clock.
            print(f"      [breaker:{self.name}] trial FAILED ({exc}) "
                  f"-> state HALF_OPEN -> OPEN (restarting {self.recovery_timeout}s timer)")
            self._state = OPEN
            self._opened_at = self._now()
            return

        # A failure while CLOSED: bump the consecutive-failure counter.
        self._consecutive_failures += 1
        print(f"      [breaker:{self.name}] failure "
              f"{self._consecutive_failures}/{self.failure_threshold} while CLOSED ({exc})")
        if self._consecutive_failures >= self.failure_threshold:
            print(f"      [breaker:{self.name}] threshold reached "
                  f"-> state CLOSED -> OPEN (fail fast for {self.recovery_timeout}s)")
            self._state = OPEN
            self._opened_at = self._now()


# ===========================================================================
# DEMO — run this file directly:  python3 circuit_breaker.py
# ===========================================================================
#
# We drive failures with a FIXED SCHEDULE (not real randomness) so the output
# is identical every run and easy to reason about. The "service" is DOWN for
# its first 4 real invocations, then it recovers.
#
# Watch for this journey:
#   CLOSED --(3 failures)--> OPEN --(fail fast)--> HALF_OPEN --(trial fails)-->
#   OPEN --(fail fast)--> HALF_OPEN --(trial succeeds)--> CLOSED
# ---------------------------------------------------------------------------

class FlakyService:
    """A stand-in dependency 'B'. Deterministic: fails its first
    `fail_first_n` real invocations, then succeeds forever after."""

    def __init__(self, fail_first_n=4):
        self.fail_first_n = fail_first_n
        self.invocations = 0  # counts only calls that actually reach the service

    def __call__(self):
        self.invocations += 1
        if self.invocations <= self.fail_first_n:
            raise ConnectionError(f"B unavailable (real call #{self.invocations})")
        return f"200 OK from B (real call #{self.invocations})"


def demo():
    print("=" * 72)
    print("CIRCUIT BREAKER DEMO  (failure_threshold=3, recovery_timeout=0.6s)")
    print("The dependency 'B' is DOWN for its first 4 real calls, then recovers.")
    print("=" * 72)

    service = FlakyService(fail_first_n=4)
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=0.6, name="B")

    # Hammer the breaker in a loop. We sleep a tiny bit between attempts so the
    # OPEN cooldown can actually elapse mid-loop (sleeps stay small on purpose).
    attempts = 16
    for i in range(1, attempts + 1):
        state_before = breaker.state
        print(f"\nattempt {i:2d} | state before call = {state_before}")
        try:
            result = breaker.call(service)
            print(f"      RESULT: SUCCESS -> {result}")
        except CircuitOpenError as e:
            # Breaker refused without touching B.
            print(f"      RESULT: FAIL-FAST (breaker) -> {e}")
        except ConnectionError as e:
            # The dependency itself failed (this call really hit B).
            print(f"      RESULT: DEPENDENCY ERROR -> {e}")
        print(f"      state after call  = {breaker.state}")
        time.sleep(0.25)  # tiny; keeps the whole demo ~4s

    print("\n" + "=" * 72)
    print(f"Done. Real calls that reached B: {service.invocations} "
          f"(many attempts never touched B — that's the breaker protecting it).")
    print("=" * 72)


if __name__ == "__main__":
    demo()
