"""
LLD-39 | Logging & Monitoring -- Demo 4: alert_watcher.py
=========================================================

Monitoring + alerting in ONE file: a simulated incident, start to finish.

    Run it:   python3 alert_watcher.py       (stdlib only -- no installs!)

What you will watch (about 3 seconds of real time, ~135 simulated seconds):

  PHASE 1  healthy    ~1% errors     normal traffic, alert stays quiet
  PHASE 2  degrading  ~8% errors     a dependency starts failing...
  PHASE 3  outage     ~35% errors    full incident
  PHASE 4  recovery   ~1% errors     deploy rolled back, errors drain away

The monitor computes an SLI (Service Level Indicator):
      error_rate over a SLIDING 30-second window
and applies ONE alert rule:
      PAGE     when window error_rate > 5%  sustained for 10 seconds
      RESOLVED when it stays back under 5%  for 15 seconds

WHY "sustained for 10 seconds"? Because one bad second is NOT an incident:
a single timeout, a garbage-collection pause, one flaky client -- these
spike the error rate for a moment and heal themselves. If we paged on every
blip, engineers would get 40 pages a night, start ignoring them (alert
fatigue), and miss the real outage. The "for N seconds/minutes" clause and
the separate, LONGER resolve window also stop the alert from FLAPPING
(fire-resolve-fire-resolve) when the metric hovers near the threshold.
"""

import random
import time
from collections import deque

random.seed(39)          # deterministic: every run of this demo is identical

# ----------------------------- tuning knobs --------------------------------
WINDOW_SECONDS = 30      # SLI = error rate over the last 30s of traffic
THRESHOLD = 0.05         # alert if error rate > 5% ...
FIRE_AFTER = 10          # ... sustained for 10 consecutive seconds
RESOLVE_AFTER = 15       # ... and resolve after 15 consecutive healthy seconds

# (name, duration in simulated seconds, true error probability, base p95 ms)
PHASES = [
    ("healthy",   35, 0.01, 180),
    ("degrading", 25, 0.08, 320),
    ("outage",    30, 0.35, 900),
    ("recovery",  45, 0.01, 200),
]


def one_second_of_traffic(err_prob: float, base_p95: float):
    """Simulate one second of production traffic.

    Returns (requests, errors, p95_ms). In real life these numbers come
    from your metrics pipeline (statsd/Prometheus), not from random()."""
    requests = random.randint(45, 60)
    errors = sum(1 for _ in range(requests) if random.random() < err_prob)
    p95_ms = round(base_p95 * random.uniform(0.85, 1.25))
    return requests, errors, p95_ms


def main() -> None:
    # The sliding window: one (requests, errors) entry per second.
    # deque(maxlen=N) silently drops the oldest entry -- perfect for windows.
    window = deque(maxlen=WINDOW_SECONDS)

    firing = False        # is the PAGE currently active?
    breach_streak = 0     # consecutive seconds above threshold
    ok_streak = 0         # consecutive seconds below it (while firing)
    clock = 0             # simulated wall clock

    print("time  phase      req/s  err%   p95_ms | win30s_err%  alert")
    print("-" * 66)

    for phase_name, duration, err_prob, base_p95 in PHASES:
        for _ in range(duration):
            clock += 1
            requests, errors, p95_ms = one_second_of_traffic(err_prob, base_p95)
            window.append((requests, errors))

            # ---- the SLI: error rate over the whole window ----------------
            total_req = sum(r for r, _ in window)
            total_err = sum(e for _, e in window)
            window_rate = total_err / total_req if total_req else 0.0

            # ---- the alert rule (a tiny state machine) --------------------
            if window_rate > THRESHOLD:
                breach_streak += 1
                ok_streak = 0
            else:
                ok_streak += 1
                breach_streak = 0

            fired_now = resolved_now = False
            if not firing and breach_streak >= FIRE_AFTER:
                firing, fired_now = True, True
            elif firing and ok_streak >= RESOLVE_AFTER:
                firing, resolved_now = False, True

            # ---- one compact status line per simulated second --------------
            status = "PAGE!" if firing else "ok"
            print(f"{clock:3d}s  {phase_name:<9}  {requests:3d}   "
                  f"{errors / requests:5.1%}  {p95_ms:5d}   |   "
                  f"{window_rate:5.1%}     {status}")

            if fired_now:
                print("!" * 66)
                print(f"!!! PAGE: error_rate {window_rate:.1%} > 5% "
                      f"for {FIRE_AFTER}s  (t={clock}s) -- waking the on-call")
                print("!" * 66)
            if resolved_now:
                print("=" * 66)
                print(f"=== RESOLVED: error_rate {window_rate:.1%} healthy "
                      f"for {RESOLVE_AFTER}s  (t={clock}s)")
                print("=" * 66)

            time.sleep(0.02)      # 1 simulated second == 20ms real time

    print("-" * 66)
    print("""
What just happened, and why the rule is shaped this way:

  1. During 'degrading' the PER-SECOND err% jumped around a lot, but the
     30s WINDOW rate climbed smoothly -- windows turn noise into a trend.
  2. The page did NOT fire the instant we crossed 5%. It fired only after
     10 straight bad seconds: one bad second is a blip, ten is an incident.
  3. In 'recovery' the raw errors stopped almost immediately, but the alert
     resolved only after the window drained AND 15 clean seconds passed.
     Slow to fire, slower to resolve = no flapping, no alert fatigue.

  Vocabulary: the 30s error rate is an SLI (indicator you measure);
  "stay under 5%" would be an SLO (objective you promise);
  the PAGE rule is the ALERT that defends that promise.
""")


if __name__ == "__main__":
    main()
