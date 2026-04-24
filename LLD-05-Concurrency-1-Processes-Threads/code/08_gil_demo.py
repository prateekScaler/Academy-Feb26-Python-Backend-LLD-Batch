"""
08 - The GIL (Global Interpreter Lock) in Action

The GIL is a mutex that allows only ONE thread to execute
Python bytecode at a time. This means:

  Threads    + CPU work = NO speedup (GIL blocks parallelism)
  Processes  + CPU work = REAL speedup (each has its own GIL)

Run: python 08_gil_demo.py
"""

import time
import threading
import multiprocessing


def cpu_work(n):
    """CPU-bound: count to n."""
    total = 0
    for i in range(n):
        total += i
    return total


def cpu_work_for_process(n):
    """Same work, but for multiprocessing (needs to be top-level)."""
    total = 0
    for i in range(n):
        total += i


def main():
    N = 10_000_000  # 10 million iterations per task
    num_workers = 4

    print("=" * 60)
    print("  THE GIL (Global Interpreter Lock) DEMO")
    print("=" * 60)
    print()
    print(f"  Task: count to {N:,} (pure CPU work)")
    print(f"  Workers: {num_workers}")
    print()

    # ---- 1. Sequential ----
    print("  1. SEQUENTIAL (baseline)")
    print("  " + "-" * 50)
    start = time.time()
    for _ in range(num_workers):
        cpu_work(N)
    seq_time = time.time() - start
    print(f"     Time: {seq_time:.2f} sec")
    print()

    # ---- 2. Threaded ----
    print("  2. THREADED (limited by GIL)")
    print("  " + "-" * 50)
    start = time.time()
    threads = []
    for _ in range(num_workers):
        t = threading.Thread(target=cpu_work, args=(N,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    thread_time = time.time() - start
    print(f"     Time: {thread_time:.2f} sec")
    print()

    # ---- 3. Multiprocessing ----
    print("  3. MULTIPROCESSING (bypasses GIL)")
    print("  " + "-" * 50)
    start = time.time()
    processes = []
    for _ in range(num_workers):
        p = multiprocessing.Process(target=cpu_work_for_process, args=(N,))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()
    proc_time = time.time() - start
    print(f"     Time: {proc_time:.2f} sec")
    print()

    # ---- Comparison ----
    print("=" * 60)
    print("  COMPARISON")
    print("=" * 60)
    print()
    print(f"    Sequential:      {seq_time:>6.2f} sec  (baseline)")
    print(f"    Threaded:        {thread_time:>6.2f} sec  ({seq_time/thread_time:.1f}x vs baseline)")
    print(f"    Multiprocessing: {proc_time:>6.2f} sec  ({seq_time/proc_time:.1f}x vs baseline)")
    print()
    print("  OBSERVATIONS:")
    print(f"    - Threads are ~{seq_time/thread_time:.1f}x vs sequential (should be {num_workers}x!)")
    print(f"    - Processes are ~{seq_time/proc_time:.1f}x vs sequential (close to {num_workers}x!)")
    print()
    print("  The GIL allows only 1 thread to run Python at a time.")
    print("  Processes each have their OWN Python interpreter + GIL,")
    print("  so they truly run in parallel on multiple CPU cores.")
    print()


if __name__ == "__main__":
    main()
