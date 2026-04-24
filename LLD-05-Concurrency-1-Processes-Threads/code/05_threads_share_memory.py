"""
05 - Threads Share Memory (and why that's DANGEROUS)

Since threads share the same memory, two threads can read and
write the SAME variable at the same time. This causes a
"race condition" - the result depends on timing/luck.

Run this multiple times - you'll get DIFFERENT results each time!

Run: python 05_threads_share_memory.py
"""

import threading
import time


# Shared variable - both threads will modify this
counter = 0


def increment(n, worker_name):
    """Increment the global counter n times."""
    global counter
    print(f"  [{worker_name}] Starting to increment {n:,} times...")
    for _ in range(n):
        counter += 1  # This is NOT atomic! (read -> add 1 -> write)
    print(f"  [{worker_name}] Done!")


def main():
    global counter

    print("=" * 60)
    print("  THREADS SHARE MEMORY — Race Condition Demo")
    print("=" * 60)
    print()

    num_trials = 5
    increments_per_thread = 100_000

    print(f"  2 threads, each incrementing a counter {increments_per_thread:,} times")
    print(f"  Expected result: {2 * increments_per_thread:,}")
    print()

    for trial in range(1, num_trials + 1):
        counter = 0  # Reset

        t1 = threading.Thread(target=increment, args=(increments_per_thread, "Thread-1"))
        t2 = threading.Thread(target=increment, args=(increments_per_thread, "Thread-2"))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        expected = 2 * increments_per_thread
        diff = expected - counter
        status = "OK" if diff == 0 else f"LOST {diff:,} increments!"

        print(f"    Trial {trial}: counter = {counter:>10,}   ({status})")
        print()

    print("-" * 60)
    print(f"  Expected: {2 * increments_per_thread:,}")
    print(f"  But often you get LESS. Why?")
    print()
    print("  Both threads do: read counter -> add 1 -> write counter")
    print("  If they read at the same time, one write OVERWRITES the other!")
    print()
    print("  This is a RACE CONDITION.")
    print("  We'll learn to fix it with Locks in Concurrency-3.")
    print("-" * 60)
    print()


if __name__ == "__main__":
    main()
