"""
Common Async Mistakes
======================
Two mistakes beginners make ALL the time.
"""

import asyncio
import time

# ============================================================
# MISTAKE 1: Forgetting 'await'
# ============================================================
print("=" * 50)
print("MISTAKE 1: Forgetting 'await'")
print("=" * 50)

async def fetch_data():
    await asyncio.sleep(0.1)
    return "some data"

async def wrong_way():
    result = fetch_data()  # Oops! No await!
    print(f"  Wrong: result = {result}")
    print(f"  Type:  {type(result)}")
    # Clean up the unawaited coroutine
    await result

async def right_way():
    result = await fetch_data()  # Correct!
    print(f"  Right: result = {result}")
    print(f"  Type:  {type(result)}")

print("\nWithout await:")
asyncio.run(wrong_way())

print("\nWith await:")
asyncio.run(right_way())

# ============================================================
# MISTAKE 2: Using time.sleep() instead of asyncio.sleep()
# ============================================================
print("\n" + "=" * 50)
print("MISTAKE 2: time.sleep() vs asyncio.sleep()")
print("=" * 50)

async def blocking_task(name):
    """BAD: time.sleep blocks the entire event loop!"""
    print(f"  [{time.strftime('%H:%M:%S')}] {name} starting")
    time.sleep(1)  # BLOCKS everything!
    print(f"  [{time.strftime('%H:%M:%S')}] {name} done")

async def nonblocking_task(name):
    """GOOD: asyncio.sleep lets other tasks run."""
    print(f"  [{time.strftime('%H:%M:%S')}] {name} starting")
    await asyncio.sleep(1)  # Other tasks can run!
    print(f"  [{time.strftime('%H:%M:%S')}] {name} done")

async def run_blocking():
    await asyncio.gather(
        blocking_task("Task-A"),
        blocking_task("Task-B"),
        blocking_task("Task-C"),
    )

async def run_nonblocking():
    await asyncio.gather(
        nonblocking_task("Task-A"),
        nonblocking_task("Task-B"),
        nonblocking_task("Task-C"),
    )

print("\nWRONG - time.sleep() blocks everything:")
start = time.time()
asyncio.run(run_blocking())
bad_time = time.time() - start
print(f"  Took {bad_time:.1f}s (tasks ran one-by-one, NOT concurrently!)")

print("\nRIGHT - asyncio.sleep() allows concurrency:")
start = time.time()
asyncio.run(run_nonblocking())
good_time = time.time() - start
print(f"  Took {good_time:.1f}s (all 3 ran at the same time!)")

print(f"\n--- Summary ---")
print(f"time.sleep(1) x 3 tasks:    {bad_time:.1f}s  (BLOCKED - no concurrency!)")
print(f"asyncio.sleep(1) x 3 tasks: {good_time:.1f}s  (concurrent - correct!)")
print(f"\nRule: Inside async code, ALWAYS use 'await asyncio.sleep()'")
print(f"      Never use 'time.sleep()' -- it freezes the entire event loop.")
