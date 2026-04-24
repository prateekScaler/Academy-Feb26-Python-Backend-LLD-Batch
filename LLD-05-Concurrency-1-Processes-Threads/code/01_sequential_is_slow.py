"""
01 - Sequential Execution is SLOW

The Problem: When you do tasks one-after-another (sequentially),
each task must WAIT for the previous one to finish.

This simulates 5 API calls that each take 1 second.
Total time? About 5 seconds. Ouch.

Run: python 01_sequential_is_slow.py
"""

import time


def call_api(user_id):
    """Simulate an API call that takes 1 second."""
    start = time.time()
    print(f"  [User {user_id}] Calling API...          started at {start:.2f}")
    time.sleep(1)  # Simulate network delay
    end = time.time()
    print(f"  [User {user_id}] Got response!           finished at {end:.2f}")
    return f"data_for_user_{user_id}"


def main():
    print("=" * 60)
    print("  SEQUENTIAL EXECUTION — One at a Time")
    print("=" * 60)
    print()
    print("Fetching data for 5 users, one after another...")
    print()

    overall_start = time.time()

    results = []
    for user_id in range(1, 6):
        result = call_api(user_id)
        results.append(result)

    overall_end = time.time()
    total = overall_end - overall_start

    print()
    print("-" * 60)
    print(f"  Total time: {total:.2f} seconds")
    print(f"  Tasks completed: {len(results)}")
    print("-" * 60)
    print()
    print("  Imagine 100 users waiting for this...")
    print(f"  That would take ~{100 * 1} seconds = {100 // 60} min {100 % 60} sec!")
    print()
    print("  There MUST be a better way. See 02_threaded_is_fast.py")
    print()


if __name__ == "__main__":
    main()
