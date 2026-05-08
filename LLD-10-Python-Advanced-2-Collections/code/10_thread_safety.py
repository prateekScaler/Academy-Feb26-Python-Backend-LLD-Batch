"""Thread safety in Python collections — what's safe, what's not."""
import threading
import time
from collections import deque
import queue


# --- GIL reminder: atomic operations are "safe", compound ones aren't ---
# SAFE (single bytecode): list.append(), dict[k]=v, deque.append()
# UNSAFE (multiple ops):  counter += 1, check-then-act, read-modify-write

# --- Demo: list.append IS atomic (GIL protects single bytecodes) ---
shared_list = []

def append_items(start: int) -> None:
    for i in range(1000):
        shared_list.append(start + i)  # single bytecode = atomic under GIL

threads = [threading.Thread(target=append_items, args=(i * 1000,)) for i in range(5)]
[t.start() for t in threads]
[t.join() for t in threads]

print(f"list.append() from 5 threads: {len(shared_list)} items (expected 5000)")
print(f"  Safe? YES — append is a single bytecode operation")


# --- Demo: counter += 1 is NOT safe ---
counter = 0

def increment() -> None:
    global counter
    for _ in range(100_000):
        counter += 1   # LOAD + ADD + STORE = 3 operations!

threads = [threading.Thread(target=increment) for _ in range(5)]
[t.start() for t in threads]
[t.join() for t in threads]

print(f"\ncounter += 1 from 5 threads: {counter} (expected 500,000)")
print(f"  Safe? NO — LOAD + ADD + STORE can be interrupted")


# --- queue.Queue: thread-safe by design ---
q: queue.Queue[str] = queue.Queue()

def producer() -> None:
    for i in range(5):
        q.put(f"item-{i}")
        time.sleep(0.01)

def consumer() -> None:
    while True:
        try:
            item = q.get(timeout=0.5)
            print(f"  consumed: {item}")
            q.task_done()
        except queue.Empty:
            break

print(f"\nqueue.Queue — thread-safe producer/consumer:")
t1 = threading.Thread(target=producer)
t2 = threading.Thread(target=consumer)
t1.start(); t2.start()
t1.join(); t2.join()


# --- Summary ---
print("\n" + "=" * 55)
print("Thread Safety Summary:")
print("=" * 55)
print()
print("  SAFE (atomic single bytecode under GIL):")
print("    list.append(x), list.pop()")
print("    dict[k] = v, dict.pop(k)")
print("    deque.append(x), deque.appendleft(x)")
print("    deque.pop(), deque.popleft()")
print("    set.add(x)")
print()
print("  NOT SAFE (compound operations):")
print("    counter += 1  (read + modify + write)")
print("    if key not in d: d[key] = val  (check-then-act)")
print("    list[i] = list[i] + 1")
print("    any read-modify-write pattern")
print()
print("  USE queue.Queue FOR:")
print("    Producer-consumer (thread-safe put/get with blocking)")
print("    Task queues between threads")
print("    Any shared buffer between threads")
print()
print("  DON'T RELY ON GIL:")
print("    It's an implementation detail of CPython")
print("    It may be removed in future Python (PEP 703)")
print("    Use locks/queues for correctness")
