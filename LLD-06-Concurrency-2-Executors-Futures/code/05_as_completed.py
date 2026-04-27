"""
05_as_completed.py — Process results as they finish
=====================================================
as_completed() yields futures in COMPLETION order.
executor.map() returns results in SUBMISSION order.
Big difference!
"""

import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


def timestamp():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


# ---------------------------------------------------------------------------
# Tasks with different durations
# ---------------------------------------------------------------------------
TASKS = {
    "Login API":      1.0,
    "Payment API":    3.0,
    "Cache lookup":   0.5,
    "DB query":       2.0,
    "Send email":     1.5,
}

def call_api(name, duration):
    """Simulate an API call that takes 'duration' seconds."""
    time.sleep(duration)
    return f"{name} responded ({duration}s)"


# ===========================================================================
# APPROACH 1: executor.map() — results in SUBMISSION order
# ===========================================================================
print("=" * 60)
print("executor.map() -> Results in SUBMISSION order")
print("=" * 60)
print()

start = time.perf_counter()

with ThreadPoolExecutor(max_workers=5) as executor:
    names = list(TASKS.keys())
    durations = list(TASKS.values())

    # map() takes the function and iterables for each argument
    results = executor.map(call_api, names, durations)

    for i, result in enumerate(results):
        elapsed = time.perf_counter() - start
        print(f"  [{elapsed:5.2f}s] Result {i+1}: {result}")

print()
print("  ^ Notice: results come back in the ORDER WE SUBMITTED them.")
print("    Login (1s) comes first because it was submitted first,")
print("    even though Cache (0.5s) finished earlier.\n")


# ===========================================================================
# APPROACH 2: as_completed() — results in COMPLETION order
# ===========================================================================
print("=" * 60)
print("as_completed() -> Results in COMPLETION order")
print("=" * 60)
print()

start = time.perf_counter()

with ThreadPoolExecutor(max_workers=5) as executor:
    # submit() each task — store future -> name mapping
    future_to_name = {}
    for name, duration in TASKS.items():
        future = executor.submit(call_api, name, duration)
        future_to_name[future] = name

    # as_completed() yields futures as they FINISH
    for i, future in enumerate(as_completed(future_to_name)):
        result = future.result()
        elapsed = time.perf_counter() - start
        print(f"  [{elapsed:5.2f}s] Result {i+1}: {result}")

print()
print("  ^ Notice: fastest tasks come back FIRST!")
print("    Cache (0.5s) -> Login (1s) -> Email (1.5s) -> DB (2s) -> Payment (3s)\n")


# ===========================================================================
# SIDE BY SIDE COMPARISON
# ===========================================================================
print("=" * 60)
print("SIDE BY SIDE")
print("=" * 60)
print("""
  Submission order:               Completion order (as_completed):
  -------------------------------- --------------------------------
  1. Login API      (1.0s)         1. Cache lookup   (0.5s)  <-- fastest first!
  2. Payment API    (3.0s)         2. Login API      (1.0s)
  3. Cache lookup   (0.5s)         3. Send email     (1.5s)
  4. DB query       (2.0s)         4. DB query       (2.0s)
  5. Send email     (1.5s)         5. Payment API    (3.0s)  <-- slowest last

  USE map() WHEN:                  USE as_completed() WHEN:
  - You need results in order      - You want to process fast results first
  - Simple "same function,         - You need to show progress to users
    many inputs" pattern           - You want to cancel remaining tasks
                                     if one fails
""")
