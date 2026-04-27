"""
09_map_vs_submit.py — When to use map() vs submit()
=====================================================
Both are useful. Here's when to pick which.
"""

import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


def timestamp():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


# ---------------------------------------------------------------------------
# Sample tasks
# ---------------------------------------------------------------------------
def fetch_user_profile(user_id):
    """Simulate fetching a user profile from an API."""
    time.sleep(0.5)
    return {"id": user_id, "name": f"User_{user_id}", "active": user_id % 2 == 0}


USER_IDS = [101, 102, 103, 104, 105, 106, 107, 108]


# ===========================================================================
# map() — Same function, many inputs, ordered results
# ===========================================================================
print("=" * 60)
print("executor.map() — Simple and ordered")
print("=" * 60)
print()

start = time.perf_counter()

with ThreadPoolExecutor(max_workers=4) as executor:
    # One line: apply function to each input
    profiles = list(executor.map(fetch_user_profile, USER_IDS))

elapsed = time.perf_counter() - start

for profile in profiles:
    status = "ACTIVE" if profile["active"] else "inactive"
    print(f"  {profile['name']} (ID: {profile['id']}) - {status}")

print(f"\n  Time: {elapsed:.2f}s")
print(f"  Results are in the SAME order as USER_IDS\n")


# ===========================================================================
# submit() — More control, unordered with as_completed
# ===========================================================================
print("=" * 60)
print("executor.submit() — Flexible and powerful")
print("=" * 60)
print()

start = time.perf_counter()

with ThreadPoolExecutor(max_workers=4) as executor:
    # Submit each task individually — get a Future back
    future_to_id = {
        executor.submit(fetch_user_profile, uid): uid
        for uid in USER_IDS
    }

    # Process in completion order
    for future in as_completed(future_to_id):
        uid = future_to_id[future]
        try:
            profile = future.result()
            status = "ACTIVE" if profile["active"] else "inactive"
            print(f"  [{timestamp()}] {profile['name']} - {status}")
        except Exception as e:
            print(f"  [{timestamp()}] User {uid} failed: {e}")

elapsed = time.perf_counter() - start
print(f"\n  Time: {elapsed:.2f}s")
print(f"  Results came in COMPLETION order (not submission order)\n")


# ===========================================================================
# submit() with DIFFERENT functions
# ===========================================================================
print("=" * 60)
print("submit() can run DIFFERENT functions (map() can't!)")
print("=" * 60)
print()

def check_inventory(item_id):
    time.sleep(0.3)
    return f"Item {item_id}: 42 in stock"

def send_notification(user_id):
    time.sleep(0.5)
    return f"Notification sent to user {user_id}"

def generate_report(report_type):
    time.sleep(0.8)
    return f"{report_type} report: 15 pages generated"

start = time.perf_counter()

with ThreadPoolExecutor(max_workers=4) as executor:
    # Three DIFFERENT functions submitted to the same pool
    futures = [
        executor.submit(check_inventory, 42),
        executor.submit(send_notification, 101),
        executor.submit(generate_report, "Sales"),
        executor.submit(check_inventory, 99),
        executor.submit(send_notification, 102),
    ]

    for future in as_completed(futures):
        result = future.result()
        print(f"  [{timestamp()}] {result}")

elapsed = time.perf_counter() - start
print(f"\n  Time: {elapsed:.2f}s")
print(f"  ^ map() can't do this — it only takes ONE function!\n")


# ===========================================================================
# DECISION GUIDE
# ===========================================================================
print("=" * 60)
print("WHEN TO USE WHICH")
print("=" * 60)
print("""
  executor.map(fn, iterable):
  ---------------------------
  + Clean, simple syntax (one line)
  + Results come back in INPUT order
  + Great for: "apply same function to a list of inputs"
  + Like Python's built-in map(), but parallel
  - Can only call ONE function
  - Can't use as_completed()
  - Less error control

  executor.submit(fn, *args):
  ---------------------------
  + Returns a Future (full control)
  + Can call DIFFERENT functions in the same pool
  + Works with as_completed() for fastest-first processing
  + Better error handling (try/except per task)
  + Can check .done(), use .cancel(), set timeouts
  - More verbose
  - Must manage Futures yourself

  SIMPLE RULE:
    Same function + ordered results  -->  map()
    Anything else                    -->  submit()
""")
