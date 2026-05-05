"""
asyncio.gather() - Run Multiple Tasks Concurrently
====================================================
Simulate fetching 5 APIs with different response times.
gather() runs them all at once -- total time = slowest one.
"""

import asyncio
import time

async def fetch_api(name, delay):
    """Simulate an API call that takes 'delay' seconds."""
    print(f"  [{time.strftime('%H:%M:%S')}] Started  {name} (will take {delay}s)")
    await asyncio.sleep(delay)
    print(f"  [{time.strftime('%H:%M:%S')}] Finished {name}")
    return {"api": name, "data": f"response from {name}", "took": delay}

apis = [
    ("Users API", 1.0),
    ("Products API", 2.0),
    ("Orders API", 1.5),
    ("Reviews API", 0.5),
    ("Analytics API", 3.0),
]

# --- Sequential ---
print("=" * 50)
print("SEQUENTIAL - one API after another")
print("=" * 50)

async def fetch_sequential():
    results = []
    for name, delay in apis:
        result = await fetch_api(name, delay)
        results.append(result)
    return results

start = time.time()
results = asyncio.run(fetch_sequential())
seq_time = time.time() - start
print(f"\nSequential: {seq_time:.1f}s total")

# --- Concurrent with gather ---
print("\n" + "=" * 50)
print("CONCURRENT - asyncio.gather()")
print("=" * 50)

async def fetch_concurrent():
    tasks = [fetch_api(name, delay) for name, delay in apis]
    results = await asyncio.gather(*tasks)
    return results

start = time.time()
results = asyncio.run(fetch_concurrent())
conc_time = time.time() - start

print(f"\nConcurrent: {conc_time:.1f}s total (= slowest API)")
print(f"\nResults received:")
for r in results:
    print(f"  {r['api']}: {r['data']}")

print(f"\n--- Summary ---")
print(f"Sequential:  {seq_time:.1f}s  (sum of all delays: {sum(d for _, d in apis)}s)")
print(f"Concurrent:  {conc_time:.1f}s  (max delay: {max(d for _, d in apis)}s)")
print(f"Speedup:     {seq_time / conc_time:.1f}x faster")
