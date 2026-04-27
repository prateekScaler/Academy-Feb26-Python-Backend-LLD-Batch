"""
02_manual_threads_pain.py — The problem that Executors solve
=============================================================
Manual thread management is tedious and error-prone.
Let's feel the pain so we appreciate the solution.
"""

import time
import threading
import random
from datetime import datetime


def timestamp():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


# ---------------------------------------------------------------------------
# Simulated I/O task: "download" a URL
# ---------------------------------------------------------------------------
def download_url(url):
    """Simulate downloading a URL. Returns the page size."""
    delay = random.uniform(0.5, 2.0)
    time.sleep(delay)  # Simulate network I/O
    page_size = random.randint(1000, 50000)
    return f"{url} -> {page_size} bytes in {delay:.1f}s"


URLS = [f"https://example.com/page/{i}" for i in range(10)]


# ===========================================================================
# PAIN POINT 1: So much boilerplate just to run threads
# ===========================================================================
print("=" * 60)
print("PAIN POINT 1: Manual thread boilerplate")
print("=" * 60)
print()

start = time.perf_counter()

# Step 1: Create a list to hold threads
threads = []

# Step 2: Create each thread, giving it the target function and args
for url in URLS:
    t = threading.Thread(target=download_url, args=(url,))
    threads.append(t)

# Step 3: Start each thread (can't forget this!)
for t in threads:
    t.start()

# Step 4: Wait for ALL threads to finish
for t in threads:
    t.join()

elapsed = time.perf_counter() - start
print(f"  Done in {elapsed:.2f}s")
print(f"  But... where are the results? We can't get return values!\n")


# ===========================================================================
# PAIN POINT 2: No way to get return values
# ===========================================================================
print("=" * 60)
print("PAIN POINT 2: Getting return values is ugly")
print("=" * 60)
print()

# The workaround: use a shared list and pass the index
results = [None] * len(URLS)

def download_url_with_storage(url, index, results_list):
    """Same task but we manually store the result."""
    delay = random.uniform(0.5, 2.0)
    time.sleep(delay)
    page_size = random.randint(1000, 50000)
    results_list[index] = f"{url} -> {page_size} bytes"  # Manual storage!

start = time.perf_counter()
threads = []
for i, url in enumerate(URLS):
    t = threading.Thread(target=download_url_with_storage, args=(url, i, results))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

elapsed = time.perf_counter() - start
print("  Results (via shared list workaround):")
for r in results:
    print(f"    {r}")
print(f"\n  Time: {elapsed:.2f}s")
print(f"  Works, but look at all that extra code!\n")


# ===========================================================================
# PAIN POINT 3: No error handling
# ===========================================================================
print("=" * 60)
print("PAIN POINT 3: Errors silently disappear")
print("=" * 60)
print()

def download_url_flaky(url):
    """Sometimes fails. The error just vanishes with threads."""
    time.sleep(0.5)
    if "page/3" in url or "page/7" in url:
        raise ConnectionError(f"Failed to connect to {url}")
    return f"{url} -> OK"

threads = []
for url in URLS:
    t = threading.Thread(target=download_url_flaky, args=(url,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("  All threads finished. No errors reported... right?")
print("  WRONG! page/3 and page/7 CRASHED but we never knew!")
print("  The exceptions were silently swallowed.\n")


# ===========================================================================
# SUMMARY
# ===========================================================================
print("=" * 60)
print("THE PAIN SUMMARY")
print("=" * 60)
print("""
  Manual thread management problems:

  1. BOILERPLATE   - Create list, append, start loop, join loop
                     (4 steps every single time)

  2. NO RETURNS    - Thread.target can't return values
                     Must use shared lists, queues, or globals

  3. NO ERRORS     - Exceptions in threads are silently lost
                     No way to know what failed

  4. NO LIMITS     - Easy to accidentally spawn 10,000 threads
                     No built-in pool/throttling

  There MUST be a better way...
  --> ThreadPoolExecutor (next file!)
""")
