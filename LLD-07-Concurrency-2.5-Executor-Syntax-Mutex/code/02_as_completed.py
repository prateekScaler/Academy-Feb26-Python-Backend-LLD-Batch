"""
as_completed() — Process results as they finish (not as submitted)
===================================================================
Real-world: You fire off 5 API calls. Why wait for the slowest
before processing the fastest? as_completed() gives you results
in the order they FINISH.
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def call_service(name, duration):
    """Simulate calling an external service."""
    print(f"  [{time.strftime('%H:%M:%S')}] Starting: {name} (will take {duration}s)")
    time.sleep(duration)
    print(f"  [{time.strftime('%H:%M:%S')}] Finished: {name}")
    return f"{name}: OK"


# Five services with DIFFERENT response times
tasks = [
    ("SMS Gateway",   0.5),
    ("Razorpay",      3.0),
    ("Email Service", 1.0),
    ("Push Notif",    2.0),
    ("Analytics",     1.5),
]


print("=" * 60)
print("APPROACH 1: as_completed() — results in COMPLETION order")
print("=" * 60)

start = time.time()
executor = ThreadPoolExecutor(max_workers=5)

# Submit all tasks and remember which future belongs to which task
future_to_name = {}
for name, duration in tasks:
    future = executor.submit(call_service, name, duration)
    future_to_name[future] = name

# Process results AS THEY COMPLETE (fastest first!)
print(f"\n[Main] Waiting for results...\n")
for i, future in enumerate(as_completed(future_to_name), 1):
    name = future_to_name[future]
    result = future.result()
    elapsed = time.time() - start
    print(f"  Result #{i} at {elapsed:.1f}s: {result}")

print(f"\n[Main] Total time: {time.time() - start:.1f}s")
executor.shutdown()


print("\n" + "=" * 60)
print("APPROACH 2: Iterating futures list — waits in SUBMISSION order")
print("=" * 60)

start = time.time()
executor = ThreadPoolExecutor(max_workers=5)

# Submit in same order
futures = []
for name, duration in tasks:
    future = executor.submit(call_service, name, duration)
    futures.append((name, future))

# Process in SUBMISSION order — must wait for each in sequence
print(f"\n[Main] Waiting for results...\n")
for i, (name, future) in enumerate(futures, 1):
    result = future.result()  # Blocks until THIS specific future is done
    elapsed = time.time() - start
    print(f"  Result #{i} at {elapsed:.1f}s: {result}")

print(f"\n[Main] Total time: {time.time() - start:.1f}s")
executor.shutdown()


print("\n" + "=" * 60)
print("KEY TAKEAWAY")
print("=" * 60)
print("""
  as_completed():        SMS(0.5s) -> Email(1s) -> Analytics(1.5s) -> Push(2s) -> Razorpay(3s)
  Submission order:      SMS(0.5s) -> Razorpay(3s!) -> Email(1s) -> Push(2s) -> Analytics(1.5s)

  as_completed() lets you START PROCESSING early.
  Example: Show the user partial results while waiting for slower services.
""")
