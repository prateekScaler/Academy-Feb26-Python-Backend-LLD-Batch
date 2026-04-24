"""
07 - CPU-bound vs I/O-bound: THE Key Distinction

This is the MOST IMPORTANT concept in concurrency:

  I/O-bound = waiting for something external (network, disk, API)
    -> Threads help A LOT (they can wait in parallel)

  CPU-bound = doing heavy computation (math, parsing, hashing)
    -> Threads DON'T help in Python (because of the GIL)

Run: python 07_cpu_vs_io_bound.py
"""

import time
import threading


# ---- Task Definitions ----

def io_task(task_id):
    """Simulate an API call (I/O-bound)."""
    time.sleep(1)
    return task_id


def cpu_task(task_id):
    """Heavy computation (CPU-bound)."""
    total = sum(i * i for i in range(5_000_000))
    return total


def run_sequential(task_func, count, label):
    """Run tasks one after another."""
    start = time.time()
    for i in range(count):
        task_func(i)
    elapsed = time.time() - start
    return elapsed


def run_threaded(task_func, count, label):
    """Run tasks with threads."""
    start = time.time()
    threads = []
    for i in range(count):
        t = threading.Thread(target=task_func, args=(i,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    elapsed = time.time() - start
    return elapsed


def main():
    num_tasks = 4

    print("=" * 60)
    print("  CPU-BOUND vs I/O-BOUND")
    print("=" * 60)
    print()
    print(f"  Running {num_tasks} tasks each, Sequential vs Threaded")
    print()

    # ---- I/O-bound test ----
    print("  I/O-BOUND (simulated API calls, 1 sec each)")
    print("  " + "-" * 50)

    io_seq = run_sequential(io_task, num_tasks, "I/O Sequential")
    print(f"    Sequential:  {io_seq:.2f} sec")

    io_thr = run_threaded(io_task, num_tasks, "I/O Threaded")
    print(f"    Threaded:    {io_thr:.2f} sec")

    if io_thr > 0:
        io_speedup = io_seq / io_thr
    else:
        io_speedup = float('inf')
    print(f"    Speedup:     {io_speedup:.1f}x")
    print()

    # ---- CPU-bound test ----
    print("  CPU-BOUND (sum of squares, heavy math)")
    print("  " + "-" * 50)

    cpu_seq = run_sequential(cpu_task, num_tasks, "CPU Sequential")
    print(f"    Sequential:  {cpu_seq:.2f} sec")

    cpu_thr = run_threaded(cpu_task, num_tasks, "CPU Threaded")
    print(f"    Threaded:    {cpu_thr:.2f} sec")

    if cpu_thr > 0:
        cpu_speedup = cpu_seq / cpu_thr
    else:
        cpu_speedup = float('inf')
    print(f"    Speedup:     {cpu_speedup:.1f}x")
    print()

    # ---- Summary ----
    print("=" * 60)
    print("  RESULTS SUMMARY")
    print("=" * 60)
    print()
    print(f"    I/O-bound speedup with threads: {io_speedup:.1f}x  <-- GREAT!")
    print(f"    CPU-bound speedup with threads: {cpu_speedup:.1f}x  <-- NO HELP!")
    print()
    print("  WHY? Python's GIL (Global Interpreter Lock) allows only")
    print("  ONE thread to execute Python code at a time.")
    print()
    print("  For I/O: threads release the GIL while waiting, so")
    print("           other threads can run. Big win!")
    print()
    print("  For CPU: threads compete for the GIL, so they take")
    print("           turns instead of running in parallel. No win!")
    print()
    print("  Solution for CPU-bound? Use multiprocessing (see 08)")
    print()


if __name__ == "__main__":
    main()
