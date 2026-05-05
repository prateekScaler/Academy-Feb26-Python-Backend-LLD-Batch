"""
Async vs Threading - Same Problem, Both Approaches
====================================================
Fetch 10 URLs (simulated). Compare threading vs async.
Both finish in ~1 second, but async uses 0 extra threads.
"""

import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor

NUM_URLS = 10

# --- Threading approach ---
def fetch_threading(url_id):
    """Simulate fetching with blocking sleep."""
    time.sleep(1)
    return f"Result-{url_id}"

print("=" * 50)
print(f"THREADING - ThreadPoolExecutor({NUM_URLS} workers)")
print("=" * 50)

start = time.time()
with ThreadPoolExecutor(max_workers=NUM_URLS) as pool:
    futures = [pool.submit(fetch_threading, i) for i in range(NUM_URLS)]
    results_t = [f.result() for f in futures]
threading_time = time.time() - start

thread_count = threading.active_count()
print(f"Results: {len(results_t)} fetched")
print(f"Time: {threading_time:.2f}s")
print(f"Threads used: {NUM_URLS} worker threads")

# --- Async approach ---
async def fetch_async(url_id):
    """Simulate fetching with non-blocking sleep."""
    await asyncio.sleep(1)
    return f"Result-{url_id}"

async def run_async():
    tasks = [fetch_async(i) for i in range(NUM_URLS)]
    return await asyncio.gather(*tasks)

print("\n" + "=" * 50)
print(f"ASYNC - asyncio.gather()")
print("=" * 50)

start = time.time()
results_a = asyncio.run(run_async())
async_time = time.time() - start

print(f"Results: {len(results_a)} fetched")
print(f"Time: {async_time:.2f}s")
print(f"Threads used: 0 extra threads (single-threaded event loop)")

print(f"\n--- Comparison ---")
print(f"{'':20} {'Threading':>12} {'Async':>12}")
print(f"{'-'*20} {'-'*12} {'-'*12}")
print(f"{'Time':20} {threading_time:>11.2f}s {async_time:>11.2f}s")
print(f"{'Extra threads':20} {NUM_URLS:>12} {'0':>12}")
print(f"{'Memory overhead':20} {'Higher':>12} {'Lower':>12}")
print(f"{'Best for':20} {'Blocking I/O':>12} {'Async I/O':>12}")

print(f"\nBoth ~1 second. Async uses 0 extra threads!")
print(f"Use threading when your library is blocking (requests, psycopg2).")
print(f"Use async when your library supports it (aiohttp, asyncpg).")
