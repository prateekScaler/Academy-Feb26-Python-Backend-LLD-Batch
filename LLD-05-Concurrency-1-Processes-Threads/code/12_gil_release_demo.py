"""
12 - What Releases the GIL?
=============================
time.sleep() isn't just "pretending" — it's a real OS call
that releases the GIL, just like a real API call would.

This demo shows several operations that release the GIL.
"""

import threading
import time
import urllib.request


# =============================================
# Demo 1: time.sleep() releases the GIL
# =============================================

print("=" * 55)
print("Demo 1: time.sleep() releases the GIL")
print("=" * 55)


def sleep_task(name, seconds):
    print(f"  {name}: sleeping {seconds}s (GIL released)...")
    time.sleep(seconds)  # Releases GIL!
    print(f"  {name}: done!")


# Sequential: 1+1+1+1 = 4s
start = time.time()
for i in range(4):
    sleep_task(f"Task-{i}", 1)
print(f"  Sequential: {time.time()-start:.1f}s\n")

# Threaded: all sleep at same time = ~1s
start = time.time()
threads = [threading.Thread(target=sleep_task, args=(f"Task-{i}", 1)) for i in range(4)]
[t.start() for t in threads]
[t.join() for t in threads]
print(f"  Threaded:   {time.time()-start:.1f}s  ← 4x faster!\n")


# =============================================
# Demo 2: File I/O releases the GIL
# =============================================

print("=" * 55)
print("Demo 2: File I/O releases the GIL")
print("=" * 55)

import tempfile
import os


def write_file(filename, size_mb):
    data = b"x" * (size_mb * 1024 * 1024)
    with open(filename, "wb") as f:
        f.write(data)  # GIL released during disk write!
    os.remove(filename)
    print(f"  Wrote {size_mb}MB to {filename}")


tmpdir = tempfile.gettempdir()

# Sequential
start = time.time()
for i in range(4):
    write_file(os.path.join(tmpdir, f"test_{i}.bin"), 10)
print(f"  Sequential: {time.time()-start:.1f}s\n")

# Threaded
start = time.time()
threads = [
    threading.Thread(target=write_file, args=(os.path.join(tmpdir, f"test_{i}.bin"), 10))
    for i in range(4)
]
[t.start() for t in threads]
[t.join() for t in threads]
print(f"  Threaded:   {time.time()-start:.1f}s\n")


# =============================================
# Summary: What releases vs holds the GIL
# =============================================

print("=" * 55)
print("What RELEASES the GIL (threading helps):")
print("=" * 55)
print("  ✓ time.sleep()")
print("  ✓ requests.get() / urllib.request")
print("  ✓ open().read() / open().write()")
print("  ✓ socket.recv() / socket.send()")
print("  ✓ subprocess.run()")
print("  ✓ Database queries (psycopg2, etc.)")
print()
print("What HOLDS the GIL (threading doesn't help):")
print("  ✗ Pure Python loops: for i in range(10_000_000)")
print("  ✗ Math: sum(i*i for i in range(...))")
print("  ✗ String processing in pure Python")
print("  ✗ Any computation that stays in Python bytecode")
print()
print("For CPU-bound work → use multiprocessing (separate GIL per process)")
