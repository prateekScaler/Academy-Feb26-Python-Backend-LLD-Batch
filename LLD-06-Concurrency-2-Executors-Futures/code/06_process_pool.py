"""
06_process_pool.py — ProcessPoolExecutor for CPU-bound work
============================================================
Same API as ThreadPoolExecutor. Just change ONE word.
But now it actually uses multiple CPU cores!
"""

import time
import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


# ---------------------------------------------------------------------------
# CPU-bound task: sum of squares
# ---------------------------------------------------------------------------
def sum_of_squares(n):
    """Heavy computation — no I/O, pure CPU."""
    total = 0
    for i in range(n):
        total += i * i
    return total


N = 5_000_000  # 5 million — enough to take noticeable time
NUM_TASKS = 4


def run_test():
    """Run all three approaches and compare."""

    # ===========================================================================
    # 1) SEQUENTIAL
    # ===========================================================================
    print("=" * 60)
    print(f"SEQUENTIAL: {NUM_TASKS} tasks, one at a time")
    print("=" * 60)

    start = time.perf_counter()
    for _ in range(NUM_TASKS):
        sum_of_squares(N)
    sequential_time = time.perf_counter() - start
    print(f"  Time: {sequential_time:.2f}s\n")

    # ===========================================================================
    # 2) THREADPOOLEXECUTOR — won't help (GIL!)
    # ===========================================================================
    print("=" * 60)
    print(f"ThreadPoolExecutor: {NUM_TASKS} threads")
    print("=" * 60)

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=NUM_TASKS) as executor:
        list(executor.map(sum_of_squares, [N] * NUM_TASKS))
    thread_time = time.perf_counter() - start
    print(f"  Time: {thread_time:.2f}s")
    print(f"  vs Sequential: {sequential_time / thread_time:.1f}x")
    print(f"  ^ Basically the SAME — GIL blocks true parallelism!\n")

    # ===========================================================================
    # 3) PROCESSPOOLEXECUTOR — real parallelism!
    # ===========================================================================
    print("=" * 60)
    print(f"ProcessPoolExecutor: {NUM_TASKS} processes")
    print("=" * 60)

    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=NUM_TASKS) as executor:
        list(executor.map(sum_of_squares, [N] * NUM_TASKS))
    process_time = time.perf_counter() - start
    print(f"  Time: {process_time:.2f}s")
    print(f"  vs Sequential: {sequential_time / process_time:.1f}x FASTER!")
    print(f"  ^ Each process has its own Python interpreter + GIL\n")

    # ===========================================================================
    # COMPARISON
    # ===========================================================================
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    bar_width = 40
    max_t = max(sequential_time, thread_time, process_time)

    def bar(t):
        filled = int((t / max_t) * bar_width)
        return "#" * filled + "." * (bar_width - filled)

    print(f"  Sequential:         [{bar(sequential_time)}] {sequential_time:.2f}s")
    print(f"  ThreadPool:         [{bar(thread_time)}] {thread_time:.2f}s")
    print(f"  ProcessPool:        [{bar(process_time)}] {process_time:.2f}s")
    print()

    print(f"  CPU cores available: {os.cpu_count()}")
    print()

    # ===========================================================================
    # THE KEY INSIGHT
    # ===========================================================================
    print("=" * 60)
    print("THE KEY INSIGHT")
    print("=" * 60)
    print("""
  The API is IDENTICAL. Just swap the class name:

    # For I/O-bound (network, file, database):
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(my_function, my_inputs)

    # For CPU-bound (math, image processing, parsing):
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = executor.map(my_function, my_inputs)

  Same .submit(), same .map(), same Future objects.
  One word changes everything.
""")


# IMPORTANT: ProcessPoolExecutor requires this guard on some platforms
if __name__ == "__main__":
    run_test()
