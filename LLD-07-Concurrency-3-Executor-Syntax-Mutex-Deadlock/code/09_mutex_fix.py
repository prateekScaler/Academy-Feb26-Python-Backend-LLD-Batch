"""
Mutex (Lock) — Fixing the race condition
=========================================
A Lock (mutual exclusion / mutex) ensures only ONE thread
can access the critical section at a time.
"""

import threading
import time

INCREMENTS = 100_000


# ---- WITHOUT LOCK (broken) ----

counter_no_lock = 0

def increment_no_lock(n):
    global counter_no_lock
    for _ in range(n):
        counter_no_lock += 1


# ---- WITH LOCK (correct) ----

counter_with_lock = 0
lock = threading.Lock()

def increment_with_lock(n):
    global counter_with_lock
    for _ in range(n):
        with lock:  # Only one thread can be inside this block at a time
            counter_with_lock += 1


print("=" * 60)
print("WITHOUT LOCK — Race condition")
print("=" * 60)

results_no_lock = []
for run in range(3):
    counter_no_lock = 0
    t1 = threading.Thread(target=increment_no_lock, args=(INCREMENTS,))
    t2 = threading.Thread(target=increment_no_lock, args=(INCREMENTS,))

    start = time.time()
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    elapsed = time.time() - start

    results_no_lock.append(elapsed)
    print(f"  Run {run+1}: counter = {counter_no_lock:>10,}  (expected {INCREMENTS*2:,})  [{elapsed:.3f}s]")


print("\n" + "=" * 60)
print("WITH LOCK — Always correct!")
print("=" * 60)

results_with_lock = []
for run in range(3):
    counter_with_lock = 0
    t1 = threading.Thread(target=increment_with_lock, args=(INCREMENTS,))
    t2 = threading.Thread(target=increment_with_lock, args=(INCREMENTS,))

    start = time.time()
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    elapsed = time.time() - start

    results_with_lock.append(elapsed)
    status = "CORRECT" if counter_with_lock == INCREMENTS * 2 else "WRONG"
    print(f"  Run {run+1}: counter = {counter_with_lock:>10,}  ({status})  [{elapsed:.3f}s]")


print("\n" + "=" * 60)
print("PERFORMANCE COST OF LOCKING")
print("=" * 60)
avg_no_lock = sum(results_no_lock) / len(results_no_lock)
avg_with_lock = sum(results_with_lock) / len(results_with_lock)
print(f"  Without lock (wrong but fast): {avg_no_lock:.3f}s average")
print(f"  With lock (correct but slow):  {avg_with_lock:.3f}s average")
print(f"  Slowdown: {avg_with_lock/avg_no_lock:.1f}x")

print("""
  The lock is SLOWER because:
  - Threads must wait their turn (no parallel increments)
  - Lock acquire/release has overhead

  But correctness > speed. A wrong answer fast is still wrong!

  "with lock:" is a context manager:
    lock.acquire()      # Wait until lock is free, then grab it
    try:
        counter += 1    # Only ONE thread runs this at a time
    finally:
        lock.release()  # Release so other thread can proceed
""")
