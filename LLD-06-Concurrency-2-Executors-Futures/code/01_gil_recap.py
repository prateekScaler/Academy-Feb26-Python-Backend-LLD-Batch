"""
01_gil_recap.py — Deep GIL (Global Interpreter Lock) Recap
===========================================================
The GIL is a mutex that allows only ONE thread to execute Python bytecode
at a time. This means threads can NOT speed up CPU-bound work.

We prove it here with numbers.
"""

import time
import threading
import multiprocessing


# ---------------------------------------------------------------------------
# CPU-bound task: count to N (pure Python computation)
# ---------------------------------------------------------------------------
def cpu_task(n=20_000_000):
    """Burn CPU by counting. No I/O, no sleeping — pure computation."""
    total = 0
    for i in range(n):
        total += 1
    return total


NUM_TASKS = 4


# ---------------------------------------------------------------------------
# 1) SEQUENTIAL — one after another
# ---------------------------------------------------------------------------
print("=" * 60)
print("APPROACH 1: Sequential (one at a time)")
print("=" * 60)

start = time.perf_counter()
for i in range(NUM_TASKS):
    cpu_task()
sequential_time = time.perf_counter() - start
print(f"  Time: {sequential_time:.2f}s\n")


# ---------------------------------------------------------------------------
# 2) THREADS — should be faster... right? NOPE.
# ---------------------------------------------------------------------------
print("=" * 60)
print("APPROACH 2: Threads (4 threads)")
print("=" * 60)

start = time.perf_counter()
threads = []
for i in range(NUM_TASKS):
    t = threading.Thread(target=cpu_task)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

threaded_time = time.perf_counter() - start
print(f"  Time: {threaded_time:.2f}s")
print(f"  vs Sequential: {'SLOWER' if threaded_time >= sequential_time else 'Faster'}")
print(f"  WHY? The GIL forces threads to take turns!\n")


# ---------------------------------------------------------------------------
# 3) MULTIPROCESSING — separate processes, each with its own GIL
# ---------------------------------------------------------------------------
print("=" * 60)
print("APPROACH 3: Multiprocessing (4 processes)")
print("=" * 60)

start = time.perf_counter()
processes = []
for i in range(NUM_TASKS):
    p = multiprocessing.Process(target=cpu_task)
    processes.append(p)
    p.start()

for p in processes:
    p.join()

multiprocess_time = time.perf_counter() - start
print(f"  Time: {multiprocess_time:.2f}s")
speedup = sequential_time / multiprocess_time
print(f"  vs Sequential: {speedup:.1f}x faster!\n")


# ---------------------------------------------------------------------------
# RESULTS COMPARISON
# ---------------------------------------------------------------------------
print("=" * 60)
print("RESULTS COMPARISON")
print("=" * 60)
bar_width = 40

def bar(t, max_t):
    filled = int((t / max_t) * bar_width)
    return "#" * filled + "." * (bar_width - filled)

max_t = max(sequential_time, threaded_time, multiprocess_time)
print(f"  Sequential:     [{bar(sequential_time, max_t)}] {sequential_time:.2f}s")
print(f"  Threaded:       [{bar(threaded_time, max_t)}] {threaded_time:.2f}s")
print(f"  Multiprocess:   [{bar(multiprocess_time, max_t)}] {multiprocess_time:.2f}s")
print()


# ---------------------------------------------------------------------------
# ASCII TIMELINE — How the GIL works
# ---------------------------------------------------------------------------
print("=" * 60)
print("HOW THE GIL WORKS (ASCII Timeline)")
print("=" * 60)
print("""
With 2 threads doing CPU work:

Time -->  |  0s    1s    2s    3s    4s    5s    6s
----------+------------------------------------------
Thread A: |  [RUN].......[RUN].......[RUN].......
Thread B: |  ......[RUN].......[RUN].......[RUN]..
GIL held: |  [A]   [B]   [A]   [B]   [A]   [B]

  ^ Only ONE thread runs at a time! They just take turns.
  ^ Total time = same as sequential (or worse due to switching)

With 2 PROCESSES doing CPU work:

Time -->  |  0s    1s    2s    3s
----------+------------------------------------------
Process A:|  [====RUN====]
Process B:|  [====RUN====]
                                    ^ True parallelism!
                                    ^ Each process has its OWN GIL
""")


# ---------------------------------------------------------------------------
# GIL RELEASE TABLE
# ---------------------------------------------------------------------------
print("=" * 60)
print("WHAT RELEASES / HOLDS THE GIL")
print("=" * 60)
print("""
  HOLDS the GIL (threads DON'T help):    RELEASES the GIL (threads DO help):
  ------------------------------------    ------------------------------------
  - Math calculations                     - time.sleep()
  - String processing                     - File read/write (I/O)
  - List/dict operations                  - Network requests (HTTP, DB)
  - Loops in pure Python                  - socket.recv() / socket.send()
  - Sorting, searching                    - subprocess calls
  - JSON parsing                          - C extensions (numpy, PIL)

  RULE OF THUMB:
    CPU-bound work  -->  use multiprocessing (or ProcessPoolExecutor)
    I/O-bound work  -->  use threading (or ThreadPoolExecutor)
""")
