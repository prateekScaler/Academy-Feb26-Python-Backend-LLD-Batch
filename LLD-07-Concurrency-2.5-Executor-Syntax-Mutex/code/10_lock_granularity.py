"""
Lock Granularity — Lock the MINIMUM necessary
==============================================
Fine-grained lock:   Lock only the shared data update   --> fast
Coarse-grained lock: Lock the entire function           --> kills concurrency
"""

import threading
import time

INCREMENTS = 50_000
counter = 0
lock = threading.Lock()


def simulate_work():
    """Simulate some I/O or computation (0.0001s)."""
    time.sleep(0.0001)


# ---- FINE-GRAINED: Lock only the counter update ----

def increment_fine(n):
    """Lock only the shared counter update. Let work run in parallel."""
    global counter
    for _ in range(n):
        simulate_work()       # This runs WITHOUT the lock (parallel OK!)
        with lock:            # Lock ONLY the critical section
            counter += 1


# ---- COARSE-GRAINED: Lock the entire function body ----

def increment_coarse(n):
    """Lock everything including the sleep. Kills concurrency!"""
    global counter
    for _ in range(n):
        with lock:            # Lock covers EVERYTHING
            simulate_work()   # Other thread waits even for this!
            counter += 1


# Use fewer increments since each has a sleep
TEST_N = 500

print("=" * 60)
print("FINE-GRAINED LOCK: Lock only the counter update")
print("=" * 60)

counter = 0
t1 = threading.Thread(target=increment_fine, args=(TEST_N,))
t2 = threading.Thread(target=increment_fine, args=(TEST_N,))

start = time.time()
t1.start()
t2.start()
t1.join()
t2.join()
fine_time = time.time() - start

print(f"  Counter: {counter:,} (expected {TEST_N * 2:,})")
print(f"  Time:    {fine_time:.2f}s")


print("\n" + "=" * 60)
print("COARSE-GRAINED LOCK: Lock the entire function body")
print("=" * 60)

counter = 0
t1 = threading.Thread(target=increment_coarse, args=(TEST_N,))
t2 = threading.Thread(target=increment_coarse, args=(TEST_N,))

start = time.time()
t1.start()
t2.start()
t1.join()
t2.join()
coarse_time = time.time() - start

print(f"  Counter: {counter:,} (expected {TEST_N * 2:,})")
print(f"  Time:    {coarse_time:.2f}s")


print("\n" + "=" * 60)
print("COMPARISON")
print("=" * 60)
print(f"  Fine-grained:   {fine_time:.2f}s")
print(f"  Coarse-grained: {coarse_time:.2f}s")
print(f"  Coarse is {coarse_time/fine_time:.1f}x slower!")

print("""
  Fine-grained (GOOD):
    Thread A: [work] [work] [LOCK counter++ UNLOCK] [work] ...
    Thread B: [work] [work] ......wait...... [LOCK counter++ UNLOCK] ...
    Both threads do "work" in PARALLEL. Only the counter update is serialized.

  Coarse-grained (BAD):
    Thread A: [LOCK work counter++ UNLOCK] ...............wait..............
    Thread B: ...............wait.............. [LOCK work counter++ UNLOCK]
    Threads take TURNS for everything. Basically sequential!

  RULE: Lock the MINIMUM necessary. Keep the critical section SMALL.
""")
