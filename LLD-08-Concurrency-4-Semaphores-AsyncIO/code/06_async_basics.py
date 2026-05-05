"""
Async Basics
=============
async def  - defines a coroutine (a function that can pause)
await      - pauses until the result is ready
asyncio.run() - starts the async event loop

Key idea: while one task waits (network, sleep), another runs!
"""

import asyncio
import time

async def greet(name, delay):
    """Greet someone after a delay."""
    print(f"  [{time.strftime('%H:%M:%S')}] Hello {name}! (waiting {delay}s...)")
    await asyncio.sleep(delay)  # Non-blocking! Other tasks can run.
    print(f"  [{time.strftime('%H:%M:%S')}] Done greeting {name}")
    return f"Greeted {name}"

async def sequential():
    """Greet 3 people one after another."""
    await greet("Alice", 1)
    await greet("Bob", 1)
    await greet("Charlie", 1)

async def concurrent():
    """Greet 3 people at the same time!"""
    results = await asyncio.gather(
        greet("Alice", 1),
        greet("Bob", 1),
        greet("Charlie", 1),
    )
    return results

# --- Sequential ---
print("=" * 50)
print("SEQUENTIAL - one after another")
print("=" * 50)

start = time.time()
asyncio.run(sequential())
seq_time = time.time() - start
print(f"Sequential: {seq_time:.1f}s")

# --- Concurrent ---
print("\n" + "=" * 50)
print("CONCURRENT - all at the same time (asyncio.gather)")
print("=" * 50)

start = time.time()
results = asyncio.run(concurrent())
conc_time = time.time() - start
print(f"Concurrent: {conc_time:.1f}s")
print(f"Results: {results}")

print(f"\n--- Summary ---")
print(f"Sequential:  {seq_time:.1f}s  (1s + 1s + 1s)")
print(f"Concurrent:  {conc_time:.1f}s  (all 3 wait at the same time!)")
print(f"Speedup:     {seq_time / conc_time:.1f}x faster")
