"""
When NOT to lock — Locking isn't always needed
===============================================
Two common cases where you can safely skip locks:
1. Read-only access (multiple threads reading same data)
2. Independent data (each thread works on its own chunk)
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor


print("=" * 60)
print("CASE 1: Read-only access — NO lock needed")
print("=" * 60)
print("Multiple threads reading the same data is SAFE.\n")

# Shared data that nobody modifies
MENU_PRICES = {
    "Burger": 299,
    "Pizza": 499,
    "Pasta": 399,
    "Salad": 199,
    "Coffee": 149,
}

def calculate_total(items):
    """Read from shared MENU_PRICES — safe without a lock!"""
    total = 0
    for item in items:
        total += MENU_PRICES[item]   # READ only, no modification
        time.sleep(0.01)             # Simulate some processing
    thread = threading.current_thread().name
    print(f"  [{thread}] Order {items} = Rs.{total}")
    return total

orders = [
    ["Burger", "Coffee"],
    ["Pizza", "Salad"],
    ["Pasta", "Coffee", "Salad"],
    ["Burger", "Pizza"],
]

start = time.time()
with ThreadPoolExecutor(max_workers=4) as executor:
    totals = list(executor.map(calculate_total, orders))

print(f"\n  All totals: {totals}")
print(f"  Time: {time.time() - start:.2f}s")
print(f"  No lock needed! Reading is safe when nobody writes.")


print("\n" + "=" * 60)
print("CASE 2: Independent data — NO lock needed")
print("=" * 60)
print("Each thread works on its OWN chunk of data.\n")

# Each thread gets its own slice — no overlap
shared_results = [0] * 4  # Pre-allocated, each thread writes to its OWN index

def process_chunk(args):
    """Each thread writes to its own index — no conflict!"""
    chunk_id, numbers = args
    total = sum(numbers)
    time.sleep(0.1)  # Simulate work
    shared_results[chunk_id] = total  # Each thread writes to DIFFERENT index
    thread = threading.current_thread().name
    print(f"  [{thread}] Chunk {chunk_id}: sum of {len(numbers)} numbers = {total}")
    return total

# Split data into 4 independent chunks
data = list(range(1, 101))  # [1, 2, 3, ..., 100]
chunks = [
    (0, data[0:25]),    # Thread 0 gets indices 0-24
    (1, data[25:50]),   # Thread 1 gets indices 25-49
    (2, data[50:75]),   # Thread 2 gets indices 50-74
    (3, data[75:100]),  # Thread 3 gets indices 75-99
]

start = time.time()
with ThreadPoolExecutor(max_workers=4) as executor:
    list(executor.map(process_chunk, chunks))

print(f"\n  Results by chunk: {shared_results}")
print(f"  Grand total: {sum(shared_results)} (expected {sum(data)})")
print(f"  Time: {time.time() - start:.2f}s")
print(f"  No lock needed! Each thread owns its own chunk.")


print("\n" + "=" * 60)
print("SUMMARY: When do you need a lock?")
print("=" * 60)
print("""
  NEED a lock:
    - Multiple threads WRITING to the SAME variable
    - Read-then-write patterns (check-then-act)
    - Any shared MUTABLE state modified by multiple threads

  DON'T need a lock:
    - Read-only shared data (nobody modifies it)
    - Independent chunks (each thread has its own data)
    - Thread-local variables (each thread has its own copy)

  Unnecessary locks = wasted performance.
  Missing locks = race conditions and bugs.
  Know the difference!
""")
