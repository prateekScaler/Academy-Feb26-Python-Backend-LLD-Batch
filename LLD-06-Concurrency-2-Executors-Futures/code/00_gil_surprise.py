"""
00 - GIL Surprise: Why threads don't speed up CPU work
========================================================
Run this FIRST in class. Students predict which is faster.
The result is surprising — that's how we introduce GIL.
"""

import time
import threading


def sum_squares(n):
    """Pure CPU work — no I/O, no sleep."""
    return sum(i * i for i in range(n))


N = 20_000_000

# Sequential: do it 4 times
print("Running sum_squares(20M) four times...\n")

start = time.time()
for _ in range(4):
    sum_squares(N)
seq = time.time() - start
print(f"  Sequential (4 times):  {seq:.2f}s")

# Threaded: 4 threads
start = time.time()
threads = [threading.Thread(target=sum_squares, args=(N,)) for _ in range(4)]
[t.start() for t in threads]
[t.join() for t in threads]
threaded = time.time() - start
print(f"  Threaded (4 threads):  {threaded:.2f}s")

# Result
print()
if threaded >= seq * 0.9:
    print("  SURPRISE: Threads didn't help! Same time (or slower).")
    print("  This is the GIL — Global Interpreter Lock.")
    print("  Only 1 thread runs Python bytecode at a time.")
else:
    print("  Threads helped slightly (your OS might schedule well).")
    print("  But the improvement is NOT 4x as you'd expect.")

print()
print("  For CPU-bound work → use multiprocessing (bypasses GIL)")
print("  For I/O-bound work → threads ARE effective (GIL released during I/O)")
