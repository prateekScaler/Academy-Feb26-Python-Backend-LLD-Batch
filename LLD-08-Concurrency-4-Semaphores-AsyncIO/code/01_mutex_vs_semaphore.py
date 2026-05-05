"""
Mutex vs Semaphore
==================
Mutex (Lock): Only 1 thread at a time
Semaphore:    Up to N threads at a time
"""

import threading
import time

def work_with_lock(lock, thread_id):
    """Only 1 thread enters at a time."""
    print(f"  Thread-{thread_id} waiting for lock...")
    with lock:
        print(f"  Thread-{thread_id} ACQUIRED lock  (working...)")
        time.sleep(0.5)
        print(f"  Thread-{thread_id} released lock")

def work_with_semaphore(sem, thread_id):
    """Up to 3 threads enter at a time."""
    print(f"  Thread-{thread_id} waiting for semaphore...")
    with sem:
        print(f"  Thread-{thread_id} ACQUIRED semaphore  (working...)")
        time.sleep(0.5)
        print(f"  Thread-{thread_id} released semaphore")

# --- Mutex: 1 at a time ---
print("=" * 50)
print("MUTEX (Lock) - 1 thread at a time")
print("=" * 50)

lock = threading.Lock()
threads = []

start = time.time()
for i in range(10):
    t = threading.Thread(target=work_with_lock, args=(lock, i))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

mutex_time = time.time() - start
print(f"\nMutex total time: {mutex_time:.1f}s (10 threads x 0.5s = ~5s)")

# --- Semaphore: 3 at a time ---
print("\n" + "=" * 50)
print("SEMAPHORE(3) - 3 threads at a time")
print("=" * 50)

sem = threading.Semaphore(3)
threads = []

start = time.time()
for i in range(10):
    t = threading.Thread(target=work_with_semaphore, args=(sem, i))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

sem_time = time.time() - start
print(f"\nSemaphore total time: {sem_time:.1f}s (10 threads, 3 at a time = ~2s)")

print(f"\n--- Summary ---")
print(f"Mutex:     {mutex_time:.1f}s  (1 at a time)")
print(f"Semaphore: {sem_time:.1f}s  (3 at a time)")
print(f"Speedup:   {mutex_time / sem_time:.1f}x faster with Semaphore(3)")
