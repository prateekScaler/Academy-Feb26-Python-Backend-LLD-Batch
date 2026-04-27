"""
03_threadpool_intro.py — ThreadPoolExecutor basics
====================================================
The clean, modern way to run tasks in threads.
"""

import time
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


def timestamp():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


# ---------------------------------------------------------------------------
# Simulated I/O task
# ---------------------------------------------------------------------------
def download_url(url):
    """Simulate downloading a URL. Returns the result."""
    delay = random.uniform(0.5, 2.0)
    print(f"  [{timestamp()}] Starting {url}")
    time.sleep(delay)
    page_size = random.randint(1000, 50000)
    print(f"  [{timestamp()}] Finished {url} ({page_size} bytes, {delay:.1f}s)")
    return f"{url} -> {page_size} bytes"


URLS = [f"https://example.com/page/{i}" for i in range(10)]


# ===========================================================================
# APPROACH 1: The old painful way (for comparison)
# ===========================================================================
print("=" * 60)
print("OLD WAY: Sequential (no concurrency)")
print("=" * 60)

start = time.perf_counter()
sequential_results = []
for url in URLS:
    result = download_url(url)
    sequential_results.append(result)
sequential_time = time.perf_counter() - start
print(f"\n  Total: {sequential_time:.2f}s\n")


# ===========================================================================
# APPROACH 2: ThreadPoolExecutor with map()
# ===========================================================================
print("=" * 60)
print("NEW WAY: ThreadPoolExecutor + map()")
print("=" * 60)

start = time.perf_counter()

# That's it. Three lines.
with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(download_url, URLS))

pool_time = time.perf_counter() - start

print(f"\n  Total: {pool_time:.2f}s")
print(f"  Speedup: {sequential_time / pool_time:.1f}x faster!\n")


# ===========================================================================
# RESULTS ARE IN ORDER
# ===========================================================================
print("=" * 60)
print("RESULTS (returned in submission order)")
print("=" * 60)
for r in results:
    print(f"  {r}")
print()


# ===========================================================================
# CODE COMPARISON
# ===========================================================================
print("=" * 60)
print("CODE COMPARISON")
print("=" * 60)
print("""
  MANUAL THREADS (10+ lines):          THREADPOOLEXECUTOR (3 lines):
  --------------------------------      --------------------------------
  import threading                      from concurrent.futures import
  threads = []                              ThreadPoolExecutor
  results = [None] * len(urls)
  for i, url in enumerate(urls):        with ThreadPoolExecutor(5) as ex:
      def worker(u, idx):                   results = list(
          results[idx] = download(u)            ex.map(download, urls)
      t = Thread(target=worker,             )
               args=(url, i))
      threads.append(t)
      t.start()
  for t in threads:
      t.join()

  10 lines of boilerplate     vs       3 clean lines
  Manual result storage       vs       Automatic return values
  No error handling           vs       Built-in error propagation
  No pool limit               vs       max_workers controls concurrency
""")
