"""
Which Tool Should I Use? - Decision Guide
==========================================
CPU-bound         -> ProcessPoolExecutor
I/O + blocking    -> ThreadPoolExecutor
I/O + async lib   -> asyncio
Limit concurrency -> Semaphore
Mutual exclusion  -> Lock

This file runs ONE example of each to show them all.
"""

import asyncio
import math
import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

# ============================================================
# Helper functions (defined at module level for multiprocessing)
# ============================================================
def is_prime(n):
    """Check if n is prime (CPU-intensive for large numbers)."""
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def count_primes(limit):
    """Count primes up to limit."""
    return sum(1 for i in range(2, limit) if is_prime(i))

def fetch_blocking(url_id):
    """Simulate a blocking I/O call."""
    time.sleep(0.5)
    return f"data-{url_id}"

async def fetch_async(url_id):
    await asyncio.sleep(0.5)
    return f"data-{url_id}"

async def run_async_tasks():
    return await asyncio.gather(*[fetch_async(i) for i in range(10)])

# Must use if __name__ == '__main__' for ProcessPoolExecutor on macOS
if __name__ == '__main__':

    # ============================================================
    # 1. CPU-bound -> ProcessPoolExecutor
    # ============================================================
    print("1. CPU-BOUND -> ProcessPoolExecutor")
    print("-" * 40)
    chunks = [250_000, 500_000, 750_000, 1_000_000]
    start = time.time()
    with ProcessPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(count_primes, chunks))
    cpu_time = time.time() - start
    print(f"   Primes found: {results}")
    print(f"   Time: {cpu_time:.2f}s (4 processes, true parallelism)")

    # ============================================================
    # 2. I/O-bound + blocking lib -> ThreadPoolExecutor
    # ============================================================
    print(f"\n2. I/O + BLOCKING LIB -> ThreadPoolExecutor")
    print("-" * 40)
    start = time.time()
    with ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(fetch_blocking, range(10)))
    thread_time = time.time() - start
    print(f"   Fetched: {len(results)} results")
    print(f"   Time: {thread_time:.2f}s (10 tasks, 5 threads)")

    # ============================================================
    # 3. I/O-bound + async lib -> asyncio
    # ============================================================
    print(f"\n3. I/O + ASYNC LIB -> asyncio")
    print("-" * 40)
    start = time.time()
    results = asyncio.run(run_async_tasks())
    async_time = time.time() - start
    print(f"   Fetched: {len(results)} results")
    print(f"   Time: {async_time:.2f}s (10 tasks, 0 extra threads)")

    # ============================================================
    # 4. Limit concurrency -> Semaphore
    # ============================================================
    sem = threading.Semaphore(3)

    def limited_work(task_id):
        with sem:
            time.sleep(0.5)
            return f"done-{task_id}"

    print(f"\n4. LIMIT CONCURRENCY -> Semaphore")
    print("-" * 40)
    start = time.time()
    with ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(limited_work, range(9)))
    sem_time = time.time() - start
    print(f"   Completed: {len(results)} tasks")
    print(f"   Time: {sem_time:.2f}s (9 tasks, max 3 at a time)")

    # ============================================================
    # 5. Mutual exclusion -> Lock
    # ============================================================
    counter = 0
    lock = threading.Lock()

    def increment():
        global counter
        for _ in range(100_000):
            with lock:
                counter += 1

    print(f"\n5. MUTUAL EXCLUSION -> Lock")
    print("-" * 40)
    start = time.time()
    threads = [threading.Thread(target=increment) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    lock_time = time.time() - start
    print(f"   Counter: {counter} (correct! 4 threads x 100,000)")
    print(f"   Time: {lock_time:.2f}s")

    # ============================================================
    # Summary
    # ============================================================
    print(f"\n{'=' * 55}")
    print(f"  DECISION GUIDE")
    print(f"{'=' * 55}")
    print(f"  {'Problem':30} {'Tool':25}")
    print(f"  {'-'*30} {'-'*25}")
    print(f"  {'CPU-bound (math, hashing)':30} {'ProcessPoolExecutor':25}")
    print(f"  {'I/O + blocking library':30} {'ThreadPoolExecutor':25}")
    print(f"  {'I/O + async library':30} {'asyncio.gather()':25}")
    print(f"  {'Limit concurrent access':30} {'Semaphore':25}")
    print(f"  {'One-at-a-time access':30} {'Lock (Mutex)':25}")
    print(f"{'=' * 55}")
