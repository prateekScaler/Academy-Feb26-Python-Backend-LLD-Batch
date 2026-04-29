"""
executor.map() — The simplest way to parallelize a loop
========================================================
map() is like Python's built-in map(), but runs tasks in parallel.
Results always come back in SUBMISSION order.
"""

import time
from concurrent.futures import ThreadPoolExecutor

def fetch(url):
    """Simulate fetching a URL (takes 1 second each)."""
    start = time.time()
    print(f"  [{time.strftime('%H:%M:%S')}] Fetching: {url}")
    time.sleep(1)
    return f"Data from {url}"


urls = [
    "https://api.example.com/page/1",
    "https://api.example.com/page/2",
    "https://api.example.com/page/3",
    "https://api.example.com/page/4",
    "https://api.example.com/page/5",
    "https://api.example.com/page/6",
    "https://api.example.com/page/7",
    "https://api.example.com/page/8",
    "https://api.example.com/page/9",
    "https://api.example.com/page/10",
]


print("=" * 60)
print("SEQUENTIAL: 10 URLs, one at a time")
print("=" * 60)

start = time.time()
results = []
for url in urls:
    results.append(fetch(url))

print(f"\nGot {len(results)} results in {time.time() - start:.1f}s")
print(f"(10 tasks x 1s each = ~10s sequential)")


print("\n" + "=" * 60)
print("PARALLEL: 10 URLs, 5 workers with executor.map()")
print("=" * 60)

start = time.time()

with ThreadPoolExecutor(max_workers=5) as executor:
    # map() returns results in the SAME ORDER as the input
    results = list(executor.map(fetch, urls))

print(f"\nGot {len(results)} results in {time.time() - start:.1f}s")
print(f"(10 tasks, 5 workers, 1s each = ~2s parallel)")

print("\nResults (always in submission order):")
for i, result in enumerate(results, 1):
    print(f"  {i}. {result}")


print("\n" + "=" * 60)
print("HOW IT WORKS")
print("=" * 60)
print("""
  10 tasks, 5 workers:

  Time 0s:  Worker1=page/1  Worker2=page/2  Worker3=page/3  Worker4=page/4  Worker5=page/5
  Time 1s:  Worker1=page/6  Worker2=page/7  Worker3=page/8  Worker4=page/9  Worker5=page/10
  Time 2s:  All done!

  Sequential: 10 x 1s = 10s
  Parallel:   10 / 5  =  2s  (roughly)
""")
