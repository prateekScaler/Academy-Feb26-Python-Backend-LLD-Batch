"""
Semaphore + ThreadPoolExecutor
===============================
Pool has 20 worker threads, but Semaphore(5) ensures
only 5 run the critical section at a time.

Think: 20 waiters in a restaurant, but only 5 can
enter the kitchen at once.
"""

import time
from concurrent.futures import ThreadPoolExecutor

import threading

sem = threading.Semaphore(5)
active_count = 0
active_lock = threading.Lock()

def fetch_url(url_id):
    global active_count

    with sem:
        with active_lock:
            active_count += 1
            current = active_count

        print(f"  [{time.strftime('%H:%M:%S')}] URL-{url_id:2d} RUNNING  "
              f"(active: {current})")
        time.sleep(1)  # Simulate network call

        with active_lock:
            active_count -= 1

    return f"Result from URL-{url_id}"

NUM_URLS = 50
POOL_SIZE = 20
SEM_LIMIT = 5

print(f"ThreadPoolExecutor(max_workers={POOL_SIZE})")
print(f"Semaphore({SEM_LIMIT})")
print(f"Submitting {NUM_URLS} tasks...\n")

start = time.time()

with ThreadPoolExecutor(max_workers=POOL_SIZE) as executor:
    futures = [executor.submit(fetch_url, i) for i in range(NUM_URLS)]
    results = [f.result() for f in futures]

elapsed = time.time() - start

print(f"\nCompleted {len(results)} tasks in {elapsed:.1f}s")
print(f"Expected: {NUM_URLS}/{SEM_LIMIT} batches x 1s = ~{NUM_URLS // SEM_LIMIT}s")
print(f"\nKey insight:")
print(f"  - Pool has {POOL_SIZE} threads ready to work")
print(f"  - But semaphore only lets {SEM_LIMIT} do the actual work at once")
print(f"  - This controls load on the external resource (API, database, etc.)")
