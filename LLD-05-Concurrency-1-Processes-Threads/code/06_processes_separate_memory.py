"""
06 - Processes Have SEPARATE Memory

Unlike threads, each process gets its OWN copy of all variables.
Modifying a variable in one process does NOT affect the other.

This is safer (no race conditions!) but means you need special
tools to share data between processes.

Run: python 06_processes_separate_memory.py
"""

import multiprocessing
import os


# This global variable exists in the PARENT process
counter = 0


def increment_global(n, worker_name):
    """Try to increment the global counter — but it's a COPY!"""
    global counter
    print(f"  [{worker_name}] PID={os.getpid()} Starting with counter={counter}")
    for _ in range(n):
        counter += 1
    print(f"  [{worker_name}] PID={os.getpid()} Finished with counter={counter}")


def increment_shared(n, worker_name, shared_counter):
    """Increment a shared counter using multiprocessing.Value."""
    print(f"  [{worker_name}] PID={os.getpid()} Starting...")
    for _ in range(n):
        shared_counter.value += 1
    print(f"  [{worker_name}] PID={os.getpid()} Finished. Shared={shared_counter.value}")


def main():
    global counter
    increments = 100_000

    print("=" * 60)
    print("  PROCESSES HAVE SEPARATE MEMORY")
    print("=" * 60)

    # ---- Part 1: Global variable is NOT shared ----
    print()
    print("  PART 1: Using a regular global variable")
    print("  " + "-" * 50)
    print()

    counter = 0
    p1 = multiprocessing.Process(target=increment_global, args=(increments, "Process-1"))
    p2 = multiprocessing.Process(target=increment_global, args=(increments, "Process-2"))

    p1.start()
    p2.start()
    p1.join()
    p2.join()

    print()
    print(f"  Parent's counter after both processes: {counter}")
    print(f"  Expected: {2 * increments:,}")
    print(f"  Got: {counter} ... it's still 0!")
    print()
    print("  Each process got its OWN COPY of 'counter'.")
    print("  The parent's counter was never touched.")

    # ---- Part 2: Using multiprocessing.Value to share ----
    print()
    print("  PART 2: Using multiprocessing.Value (shared memory)")
    print("  " + "-" * 50)
    print()

    shared_counter = multiprocessing.Value('i', 0)  # 'i' = integer, initial value 0

    p3 = multiprocessing.Process(target=increment_shared, args=(increments, "Process-3", shared_counter))
    p4 = multiprocessing.Process(target=increment_shared, args=(increments, "Process-4", shared_counter))

    p3.start()
    p4.start()
    p3.join()
    p4.join()

    print()
    print(f"  Shared counter: {shared_counter.value:,}")
    print(f"  Expected: {2 * increments:,}")
    print()
    print("  Note: multiprocessing.Value CAN also have race conditions.")
    print("  You'd use a Lock to make it safe (Concurrency-3).")

    print()
    print("-" * 60)
    print("  KEY TAKEAWAY:")
    print("    Processes = separate memory (safe but isolated)")
    print("    Threads = shared memory (fast but dangerous)")
    print("-" * 60)
    print()


if __name__ == "__main__":
    main()
