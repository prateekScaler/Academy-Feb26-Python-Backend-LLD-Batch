"""
02 - Threaded Execution is FAST

The Solution: Run all 5 API calls at the SAME TIME using threads.
While one thread waits for a response, the others keep working.

Same 5 API calls as before, but now they overlap!
Total time? About 1 second. 5x faster!

Run: python 02_threaded_is_fast.py
"""

import time
import threading


def call_api(user_id, results):
    """Simulate an API call that takes 1 second."""
    start = time.time()
    print(f"  [User {user_id}] Calling API...          started at {start:.2f}")
    time.sleep(1)  # Simulate network delay
    end = time.time()
    print(f"  [User {user_id}] Got response!           finished at {end:.2f}")
    results[user_id] = f"data_for_user_{user_id}"


def main():
    print("=" * 60)
    print("  THREADED EXECUTION — All at Once!")
    print("=" * 60)
    print()
    print("Fetching data for 5 users, ALL AT THE SAME TIME...")
    print()

    overall_start = time.time()

    results = {}
    threads = []

    # Create and start 5 threads
    for user_id in range(1, 6):
        t = threading.Thread(target=call_api, args=(user_id, results))
        threads.append(t)
        t.start()  # Start the thread (non-blocking!)

    # Wait for ALL threads to finish
    for t in threads:
        t.join()

    overall_end = time.time()
    total = overall_end - overall_start

    print()
    print("-" * 60)
    print(f"  Total time: {total:.2f} seconds")
    print(f"  Tasks completed: {len(results)}")
    print("-" * 60)
    print()

    # Compare with sequential
    sequential_time = 5.0
    speedup = sequential_time / total
    print(f"  Sequential would take: ~5.00 seconds")
    print(f"  Threaded took:         ~{total:.2f} seconds")
    print(f"  Speedup:               ~{speedup:.1f}x faster!")
    print()
    print("  Notice how ALL 5 tasks started at nearly the same time?")
    print("  That's the power of threads for I/O-bound work.")
    print()


if __name__ == "__main__":
    main()
