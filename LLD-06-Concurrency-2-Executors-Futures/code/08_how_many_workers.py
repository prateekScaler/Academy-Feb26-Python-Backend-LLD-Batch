"""
08_how_many_workers.py — Choosing the right pool size
======================================================
Too few workers = slow. Too many = wasted resources (or worse).
Let's find the sweet spot.
"""

import time
import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


CPU_COUNT = os.cpu_count()
print(f"This machine has {CPU_COUNT} CPU cores.\n")


# ---------------------------------------------------------------------------
# I/O-bound task
# ---------------------------------------------------------------------------
def io_task(task_id):
    """Simulate a 1-second network call."""
    time.sleep(1)
    return task_id


# ---------------------------------------------------------------------------
# CPU-bound task
# ---------------------------------------------------------------------------
def cpu_task(n):
    """Sum of squares — pure CPU work."""
    total = 0
    for i in range(n):
        total += i * i
    return total


# ===========================================================================
# TEST 1: I/O-bound — how many threads?
# ===========================================================================
print("=" * 60)
print("TEST 1: I/O-bound (20 tasks, each sleeps 1 second)")
print("=" * 60)
print()

NUM_IO_TASKS = 20
worker_counts = [1, 5, 10, 20, 50]
io_results = {}

for workers in worker_counts:
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        list(executor.map(io_task, range(NUM_IO_TASKS)))
    elapsed = time.perf_counter() - start
    io_results[workers] = elapsed
    print(f"  {workers:2d} workers: {elapsed:.2f}s")

print()
print("  Visualization (shorter = faster):")
print()
max_time = max(io_results.values())
for workers, elapsed in io_results.items():
    bar_len = int((elapsed / max_time) * 40)
    bar = "#" * bar_len + "." * (40 - bar_len)
    print(f"  {workers:2d} workers: [{bar}] {elapsed:.2f}s")

print("""
  INSIGHT for I/O-bound:
    - 1 worker  = sequential (20 seconds for 20 tasks)
    - 20 workers = all run at once (about 1 second!)
    - 50 workers = no extra benefit (only 20 tasks)
    - More threads is fine for I/O since they just sleep/wait
""")


# ===========================================================================
# TEST 2: CPU-bound — how many processes?
# ===========================================================================
print("=" * 60)
print(f"TEST 2: CPU-bound (8 tasks, sum of squares)")
print(f"        This machine has {CPU_COUNT} cores")
print("=" * 60)
print()

NUM_CPU_TASKS = 8
N = 2_000_000
process_counts = [1, 2, 4, 8, 16]
cpu_results = {}


def run_cpu_test():
    for workers in process_counts:
        start = time.perf_counter()
        with ProcessPoolExecutor(max_workers=workers) as executor:
            list(executor.map(cpu_task, [N] * NUM_CPU_TASKS))
        elapsed = time.perf_counter() - start
        cpu_results[workers] = elapsed
        print(f"  {workers:2d} workers: {elapsed:.2f}s")

    print()
    print("  Visualization (shorter = faster):")
    print()
    max_time = max(cpu_results.values())
    for workers, elapsed in cpu_results.items():
        bar_len = int((elapsed / max_time) * 40)
        bar = "#" * bar_len + "." * (40 - bar_len)
        cores_note = " <-- cpu_count" if workers == CPU_COUNT else ""
        print(f"  {workers:2d} workers: [{bar}] {elapsed:.2f}s{cores_note}")

    print(f"""
  INSIGHT for CPU-bound:
    - Speedup improves up to {CPU_COUNT} workers (= number of cores)
    - Beyond {CPU_COUNT}, no improvement — more processes just compete
      for the SAME cores (context switching overhead)
    - Workers > cores is COUNTERPRODUCTIVE for CPU work
""")


# ===========================================================================
# DEFAULTS
# ===========================================================================
print("=" * 60)
print("DEFAULT WORKER COUNTS")
print("=" * 60)
print(f"""
  ThreadPoolExecutor default:
    min(32, os.cpu_count() + 4) = min(32, {CPU_COUNT} + 4) = {min(32, CPU_COUNT + 4)}
    ^ Designed for I/O-bound work, where many threads are fine

  ProcessPoolExecutor default:
    os.cpu_count() = {CPU_COUNT}
    ^ One process per core — the sweet spot for CPU-bound work

  RULES OF THUMB:
    +-------------------+-----------------------------+
    | Work Type         | Recommended Workers         |
    +-------------------+-----------------------------+
    | I/O-bound         | 20-100+ (depends on tasks)  |
    | CPU-bound         | os.cpu_count() (no more!)   |
    | Mixed             | Separate pools for each     |
    +-------------------+-----------------------------+
""")


if __name__ == "__main__":
    run_cpu_test()
