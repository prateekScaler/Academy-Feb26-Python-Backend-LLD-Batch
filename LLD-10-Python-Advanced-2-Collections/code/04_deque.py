"""deque — double-ended queue. O(1) append/pop from BOTH ends."""
from collections import deque
import time


# --- Problem: list.insert(0, x) is O(n) ---
def benchmark_prepend(n: int = 100_000):
    # List: insert at front is SLOW (shifts everything)
    lst = []
    start = time.time()
    for i in range(n):
        lst.insert(0, i)
    list_time = time.time() - start

    # Deque: appendleft is O(1)
    dq = deque()
    start = time.time()
    for i in range(n):
        dq.appendleft(i)
    deque_time = time.time() - start

    print(f"Prepend {n:,} items:")
    print(f"  list.insert(0, x):  {list_time:.3f}s")
    print(f"  deque.appendleft(): {deque_time:.3f}s")
    print(f"  deque is {list_time/deque_time:.0f}x faster!")

benchmark_prepend()


# --- Basic operations ---
dq = deque([1, 2, 3])
print(f"\ndeque: {dq}")

dq.append(4)          # right end
dq.appendleft(0)      # left end
print(f"  after append(4), appendleft(0): {dq}")

dq.pop()              # right end
dq.popleft()          # left end
print(f"  after pop(), popleft(): {dq}")


# --- maxlen: fixed-size buffer (sliding window) ---
recent_logs = deque(maxlen=3)
for log in ["login", "view_page", "click_btn", "logout", "login_again"]:
    recent_logs.append(log)
    print(f"  append '{log}': {list(recent_logs)}")

print(f"\n  Only last 3 kept! Old ones auto-removed.")


# --- rotate ---
dq = deque([1, 2, 3, 4, 5])
dq.rotate(2)     # move 2 from right to left
print(f"\nrotate(2):  {dq}")
dq.rotate(-2)    # move 2 from left to right
print(f"rotate(-2): {dq}")


# --- Use cases ---
print("\n--- When to use deque ---")
print("  • Queue (FIFO): append() + popleft()")
print("  • Stack (LIFO): append() + pop()")
print("  • Sliding window: maxlen=N")
print("  • BFS in graphs: popleft() for FIFO processing")
print("  • Recent items: last N logs, last N requests")
print("  • DON'T use for random access: dq[500] is O(n)")
