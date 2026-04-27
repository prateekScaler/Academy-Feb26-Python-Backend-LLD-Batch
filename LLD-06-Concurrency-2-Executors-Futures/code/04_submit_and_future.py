"""
04_submit_and_future.py — submit() and Future objects
======================================================
executor.map() is simple but limited.
executor.submit() gives you a Future — a "promise" of a result.
"""

import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


def timestamp():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def slow_task(name, duration):
    """Simulate work that takes 'duration' seconds."""
    print(f"  [{timestamp()}] {name}: started (will take {duration}s)")
    time.sleep(duration)
    result = f"{name} completed!"
    print(f"  [{timestamp()}] {name}: done")
    return result


# ===========================================================================
# SUBMIT returns a Future
# ===========================================================================
print("=" * 60)
print("STEP 1: submit() returns a Future object")
print("=" * 60)
print()

executor = ThreadPoolExecutor(max_workers=3)

future = executor.submit(slow_task, "TaskA", 2)

print(f"  [{timestamp()}] submit() returned immediately!")
print(f"  [{timestamp()}] Type of future: {type(future)}")
print(f"  [{timestamp()}] future = {future}")
print()


# ===========================================================================
# FUTURE LIFECYCLE: done() and result()
# ===========================================================================
print("=" * 60)
print("STEP 2: Check .done() and get .result()")
print("=" * 60)
print()

# Check immediately — probably not done yet
print(f"  [{timestamp()}] future.done() = {future.done()}  (still running)")

# Wait a bit and check again
time.sleep(1)
print(f"  [{timestamp()}] future.done() = {future.done()}  (still running)")

# Get the result — this BLOCKS until the task finishes
print(f"  [{timestamp()}] Calling future.result() — this blocks until done...")
result = future.result()
print(f"  [{timestamp()}] future.result() = '{result}'")
print(f"  [{timestamp()}] future.done() = {future.done()}  (now it's True!)")
print()


# ===========================================================================
# MULTIPLE FUTURES
# ===========================================================================
print("=" * 60)
print("STEP 3: Multiple submit() calls = Multiple Futures")
print("=" * 60)
print()

futures = {}

futures["fast"]   = executor.submit(slow_task, "Fast",   1)
futures["medium"] = executor.submit(slow_task, "Medium", 2)
futures["slow"]   = executor.submit(slow_task, "Slow",   3)

print(f"  [{timestamp()}] All submitted! Futures:")
for name, f in futures.items():
    print(f"    {name}: done={f.done()}")

print(f"\n  [{timestamp()}] Waiting for all results...")
for name, f in futures.items():
    result = f.result()  # blocks until this specific future is done
    print(f"  [{timestamp()}] {name}: '{result}'")
print()


# ===========================================================================
# TIMEOUT
# ===========================================================================
print("=" * 60)
print("STEP 4: result(timeout=...) — Don't wait forever")
print("=" * 60)
print()

future = executor.submit(slow_task, "SlowOne", 5)

time.sleep(0.5)  # Let it start

try:
    print(f"  [{timestamp()}] Trying result(timeout=1)...")
    result = future.result(timeout=1)
    print(f"  [{timestamp()}] Got: {result}")
except TimeoutError:
    print(f"  [{timestamp()}] TimeoutError! Task not done in 1 second.")
    print(f"  [{timestamp()}] Task is still running: done={future.done()}")

# Clean up — wait for it to actually finish
future.result()
print(f"  [{timestamp()}] Now it's done: done={future.done()}")
print()


# ===========================================================================
# FUTURE LIFECYCLE DIAGRAM
# ===========================================================================
print("=" * 60)
print("FUTURE LIFECYCLE")
print("=" * 60)
print("""
  executor.submit(fn, args)
         |
         v
    +-----------+       Worker thread picks it up
    | PENDING   | ----------------------------+
    +-----------+                              |
                                               v
                                        +-----------+
                                        | RUNNING   |
                                        +-----------+
                                         /         \\
                              Success   /           \\  Exception
                                       v             v
                               +-----------+   +-----------+
                               | FINISHED  |   | FINISHED  |
                               | (result)  |   | (error)   |
                               +-----------+   +-----------+

  Methods:
    future.done()              -> True/False
    future.result()            -> blocks, returns value (or raises exception)
    future.result(timeout=N)   -> blocks for N seconds, then TimeoutError
    future.cancel()            -> cancel if still PENDING (not if RUNNING)
""")

executor.shutdown(wait=True)
