"""
LLD-38  |  Cloud-native patterns (adapted for Python)
=====================================================
DELIVERABLE 2 — THE PRODUCTION RESILIENCE STACK (real libraries)

circuit_breaker.py showed the breaker built by hand so you can SEE the state
machine. In real code you compose SEVERAL resilience patterns using proven
libraries. This file wraps a call to a flaky "service B" with four layers,
from the INSIDE out:

    ┌─────────────────────────────────────────────────────────────┐
    │ 4. FALLBACK        return a cached/default answer if all else │
    │                    fails, so the caller degrades gracefully   │
    │  ┌──────────────────────────────────────────────────────────┐│
    │  │ 3. CIRCUIT BREAKER  (pybreaker) once B looks dead, OPEN    ││
    │  │                     and fail fast — don't even retry it    ││
    │  │  ┌───────────────────────────────────────────────────────┐││
    │  │  │ 2. RETRIES        (tenacity) exponential backoff+jitter│││
    │  │  │                   retry ONLY transient errors          │││
    │  │  │  ┌────────────────────────────────────────────────────┐│││
    │  │  │  │ 1. TIMEOUT     (httpx) a single call can never hang ││││
    │  │  │  │                forever — bail after N seconds       ││││
    │  │  │  └────────────────────────────────────────────────────┘│││
    │  │  └───────────────────────────────────────────────────────┘││
    │  └──────────────────────────────────────────────────────────┘│
    └─────────────────────────────────────────────────────────────┘

WHY THIS ORDER?
  * TIMEOUT is innermost: every individual attempt is time-bounded.
  * RETRIES wrap the timeout: a transient blip (one 503 / one timeout) is
    smoothed over by trying again with growing, jittered backoff.
  * The CIRCUIT BREAKER wraps the WHOLE retry loop: if the retries keep failing,
    that counts as ONE failure against the breaker. After enough of them the
    breaker OPENS and short-circuits — so we stop hammering (and stop retrying)
    a dependency that is clearly down.
  * FALLBACK is outermost: whether the breaker refused or the retries were
    exhausted, we return a sane default instead of throwing in the user's face.

"Service B" is a tiny HTTP server we start in a background thread, so this file
is fully self-contained: just run `python resilient_client.py`. Its behaviour is
driven by an explicit PHASE (healthy -> flaky -> down -> recovered), never by
real randomness, so the trace is identical every run.
"""

import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import httpx
import pybreaker
from tenacity import (retry, retry_if_exception, stop_after_attempt,
                      wait_exponential_jitter)


# ===========================================================================
# "SERVICE B" — a local HTTP endpoint whose health we script via a phase.
# ===========================================================================
# Shared, mutable "world state" the handler reads. The demo flips `phase` and
# resets `counter` so each phase behaves deterministically.
B_STATE = {"phase": "healthy", "counter": 0}


class ServiceBHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        phase = B_STATE["phase"]
        B_STATE["counter"] += 1
        n = B_STATE["counter"]

        if phase == "healthy":
            return self._ok(f"quote: 'ship it' (call #{n})")

        if phase == "flaky":
            # Deterministic transient trouble on the first two attempts of a
            # logical call, then success — so you SEE a timeout and a 503 get
            # retried away.
            if n == 1:
                time.sleep(1.0)                      # slower than client timeout
                return self._ok("late response B never sends in time")
            if n == 2:
                return self._fail(503, "temporarily overloaded")
            return self._ok(f"quote: 'measure twice' (call #{n})")

        if phase == "down":
            return self._fail(503, "B is DOWN")      # every attempt fails

        # phase == "recovered"
        return self._ok(f"quote: 'welcome back' (call #{n})")

    # -- helpers --
    def _ok(self, body):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(body.encode())

    def _fail(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(body.encode())

    def log_message(self, *args):
        pass  # keep B silent; ALL narration comes from the client side below


class QuietServiceB(ThreadingHTTPServer):
    # When the client TIMES OUT it closes the socket; B's later write then hits a
    # BrokenPipe. That's expected in the flaky phase, so we swallow it instead of
    # dumping a scary traceback into our clean narrated trace.
    def handle_error(self, request, client_address):
        pass


def start_service_b():
    """Start B on an ephemeral localhost port in a daemon thread. Returns base URL."""
    server = QuietServiceB(("127.0.0.1", 0), ServiceBHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    host, port = server.server_address
    return server, f"http://{host}:{port}/quote"


# ===========================================================================
# LAYER 2 — WHICH ERRORS ARE "TRANSIENT" (worth retrying)?
# ===========================================================================
# Golden rule: retry only things that might succeed if you try again.
#   * network timeouts / connection errors  -> transient  (retry)
#   * HTTP 5xx (server had a bad moment)     -> transient  (retry)
#   * HTTP 4xx (bad request, not found, ...) -> PERMANENT  (do NOT retry)
def is_transient(exc: BaseException) -> bool:
    if isinstance(exc, (httpx.TimeoutException, httpx.ConnectError, httpx.ReadError)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code >= 500
    return False


def _describe(exc):
    if isinstance(exc, httpx.HTTPStatusError):
        return f"HTTP {exc.response.status_code}"
    if isinstance(exc, httpx.TimeoutException):
        return "timeout"
    if isinstance(exc, httpx.ConnectError):
        return "connection refused"
    return type(exc).__name__


# Tracks how many retry attempts actually ran for the CURRENT logical call, so
# we can tell "the breaker was already OPEN, we failed fast without touching B"
# apart from "we retried, exhausted, and THAT failure just tripped the breaker".
_attempts_this_call = 0


# -- tenacity narration hooks so students see each attempt + backoff --
def _before(rs):
    global _attempts_this_call
    _attempts_this_call = rs.attempt_number
    print(f"        [retry ] attempt {rs.attempt_number} -> calling B ...")


def _before_sleep(rs):
    exc = rs.outcome.exception()
    sleep_s = rs.next_action.sleep
    print(f"        [retry ] attempt {rs.attempt_number} FAILED ({_describe(exc)}); "
          f"backoff {sleep_s:.2f}s (exp+jitter), then retry")


# LAYER 1 + 2 together: a time-bounded call to B, retried on transient errors
# with exponential backoff + jitter, up to 3 attempts. reraise=True means the
# LAST real exception (e.g. the 503) propagates out — which is what the breaker
# above will count as a failure.
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=0.05, max=0.4, jitter=0.05),
    retry=retry_if_exception(is_transient),
    before=_before,
    before_sleep=_before_sleep,
    reraise=True,
)
def call_b_with_retries(client: httpx.Client, url: str) -> str:
    # LAYER 1: httpx timeout — this single attempt cannot hang forever.
    resp = client.get(url, timeout=0.3)
    resp.raise_for_status()          # 4xx/5xx -> HTTPStatusError
    return resp.text


# ===========================================================================
# LAYER 3 — CIRCUIT BREAKER (pybreaker), wrapping the whole retry loop.
# ===========================================================================
class BreakerNarrator(pybreaker.CircuitBreakerListener):
    """Prints breaker state transitions so the OPEN/HALF-OPEN/CLOSED journey
    is visible in the trace."""
    def state_change(self, cb, old_state, new_state):
        old = old_state.name if old_state else "?"
        print(f"        [breaker] state {old.upper()} -> {new_state.name.upper()}")


# fail_max=2  -> after 2 failed logical calls the breaker OPENS.
# reset_timeout=1.0 -> after 1s OPEN it goes HALF-OPEN and allows one trial call.
breaker = pybreaker.CircuitBreaker(
    fail_max=2, reset_timeout=1.0, listeners=[BreakerNarrator()], name="B"
)


# ===========================================================================
# LAYER 4 — FALLBACK. The single entry point the rest of the app would call.
# ===========================================================================
_last_good_quote = None   # tiny cache of the last successful answer


def get_quote(client: httpx.Client, url: str) -> str:
    """Resilient call to B. Always returns SOMETHING (never raises): a live
    answer, or a graceful fallback (last-good cache or a static default)."""
    global _last_good_quote, _attempts_this_call
    _attempts_this_call = 0
    try:
        # breaker.call runs the retrying function ONLY if the breaker is closed
        # or half-open; if it's OPEN it raises CircuitBreakerError immediately.
        result = breaker.call(call_b_with_retries, client, url)
        _last_good_quote = result           # remember it for future fallbacks
        print(f"      RESULT: LIVE  -> {result}")
        return result
    except pybreaker.CircuitBreakerError:
        fb = _fallback()
        if _attempts_this_call == 0:
            # Breaker was already OPEN: we failed fast WITHOUT touching B.
            print(f"      RESULT: FALLBACK (breaker OPEN — failed fast, B not called) -> {fb}")
        else:
            # We retried, exhausted, and that final failure TRIPPED the breaker open.
            print(f"      RESULT: FALLBACK (retries exhausted; that failure TRIPPED the "
                  f"breaker OPEN) -> {fb}")
        return fb
    except httpx.HTTPError as exc:
        # Retries were exhausted against a real error. Degrade gracefully.
        fb = _fallback()
        print(f"      RESULT: FALLBACK (retries exhausted: {_describe(exc)}) -> {fb}")
        return fb


def _fallback() -> str:
    if _last_good_quote is not None:
        return f"[cached] {_last_good_quote}"
    return "[default] service unavailable, try later"


# ===========================================================================
# DEMO — run this file directly:  python3 resilient_client.py
# ===========================================================================
def _phase(name):
    """Switch service B to a new phase and reset its per-phase counter."""
    B_STATE["phase"] = name
    B_STATE["counter"] = 0


def demo():
    server, url = start_service_b()
    print("=" * 74)
    print("RESILIENT CLIENT DEMO   (httpx timeout + tenacity retries + pybreaker")
    print("+ fallback).  Breaker: fail_max=2, reset_timeout=1.0s.  B @", url)
    print("=" * 74)

    with httpx.Client() as client:
        # ---- PHASE 1: HEALTHY -> clean success, no retries ----
        _phase("healthy")
        print("\n[PHASE 1] B is HEALTHY — calls just succeed:")
        for i in (1, 2):
            print(f"\n  call {i}: (breaker={breaker.current_state})")
            get_quote(client, url)

        # ---- PHASE 2: FLAKY -> a timeout + a 503, retried away ----
        _phase("flaky")
        print("\n[PHASE 2] B is FLAKY — 1st attempt times out, 2nd is 503, "
              "3rd succeeds. Watch retries win:")
        print(f"\n  call 1: (breaker={breaker.current_state})")
        get_quote(client, url)

        # ---- PHASE 3: DOWN -> retries exhaust, breaker OPENS, fallback ----
        _phase("down")
        print("\n[PHASE 3] B is DOWN — every attempt 503s. Retries exhaust, the")
        print("          breaker trips OPEN, then calls FAIL FAST into the fallback:")
        for i in (1, 2, 3, 4):
            print(f"\n  call {i}: (breaker={breaker.current_state})")
            get_quote(client, url)

        # ---- PHASE 4: RECOVERED -> breaker half-opens, trial succeeds, CLOSED ----
        _phase("recovered")
        print("\n[PHASE 4] B RECOVERED. We wait out the 1.0s reset_timeout so the")
        print("          breaker can HALF-OPEN, send a trial call, and CLOSE again:")
        time.sleep(1.1)
        for i in (1, 2, 3):
            print(f"\n  call {i}: (breaker={breaker.current_state})")
            get_quote(client, url)

    server.shutdown()
    print("\n" + "=" * 74)
    print("Done. The app NEVER hung and NEVER surfaced a raw error to the caller:")
    print("it retried blips, stopped hammering a dead B, and degraded gracefully.")
    print("=" * 74)


if __name__ == "__main__":
    demo()
