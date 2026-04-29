"""
executor.submit() — How to hand off work to a thread pool
==========================================================
submit() gives you a Future object — a "receipt" for work in progress.
You can check if it's done, wait for the result, or set a timeout.
"""

import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError

def fetch(url):
    """Simulate fetching a URL (takes 2 seconds)."""
    print(f"  [Worker] Starting fetch: {url}")
    time.sleep(2)
    print(f"  [Worker] Done fetching: {url}")
    return f"Data from {url}"


print("=" * 60)
print("PART 1: Submit a task and inspect the Future")
print("=" * 60)

executor = ThreadPoolExecutor(max_workers=2)

start = time.time()
future = executor.submit(fetch, "https://api.example.com/menu")

# The future is returned IMMEDIATELY — the work happens in background
print(f"\n[Main] future.done() right after submit: {future.done()}")
print(f"[Main] Type of future: {type(future)}")

# Wait a bit and check again
time.sleep(3)
print(f"[Main] future.done() after 3 seconds:    {future.done()}")

# Get the result (already done, so returns instantly)
result = future.result()
print(f"[Main] future.result() = '{result}'")
print(f"[Main] Total time: {time.time() - start:.1f}s")

executor.shutdown()


print("\n" + "=" * 60)
print("PART 2: future.result() BLOCKS until the task finishes")
print("=" * 60)

executor = ThreadPoolExecutor(max_workers=2)

start = time.time()
future = executor.submit(fetch, "https://api.example.com/orders")

print(f"\n[Main] Calling future.result() immediately...")
result = future.result()  # This line WAITS until the worker is done
print(f"[Main] Got result: '{result}'")
print(f"[Main] Total time: {time.time() - start:.1f}s  (blocked for ~2s)")

executor.shutdown()


print("\n" + "=" * 60)
print("PART 3: Timeout — don't wait forever!")
print("=" * 60)

def slow_fetch(url):
    """This one takes 5 seconds."""
    print(f"  [Worker] Slow fetch starting: {url}")
    time.sleep(5)
    return f"Data from {url}"

executor = ThreadPoolExecutor(max_workers=2)

start = time.time()
future = executor.submit(slow_fetch, "https://api.slow-server.com")

print(f"\n[Main] Waiting with timeout=2 seconds...")
try:
    result = future.result(timeout=2)
    print(f"[Main] Got result: {result}")
except TimeoutError:
    print(f"[Main] TIMEOUT! Task didn't finish in 2 seconds.")
    print(f"[Main] Task is still running in background: done={future.done()}")

print(f"[Main] Total time: {time.time() - start:.1f}s")

executor.shutdown(wait=True)  # Wait for background task to finish cleanly
print(f"[Main] After shutdown: done={future.done()}")


print("\n" + "=" * 60)
print("LIFECYCLE SUMMARY")
print("=" * 60)
print("""
  executor.submit(fn, args)
       |
       v
  Future object returned IMMEDIATELY
       |
       |--- future.done()        --> True/False (non-blocking check)
       |--- future.result()      --> BLOCKS until done, returns value
       |--- future.result(timeout=N) --> BLOCKS up to N seconds, then TimeoutError
       |--- future.exception()   --> Returns exception if task failed
""")
