"""
10 - Multiprocessing API Reference

A clean reference for the most common multiprocessing operations.
Very similar to threading, but uses separate processes.

Run: python 10_process_api.py
"""

import multiprocessing
import os
import time


def worker(name, duration):
    """A simple task for our processes."""
    pid = os.getpid()
    print(f"    [{name}] PID={pid} starting, will work for {duration}s")
    time.sleep(duration)
    print(f"    [{name}] PID={pid} done!")


def main():
    print("=" * 60)
    print("  MULTIPROCESSING API REFERENCE")
    print("=" * 60)

    # ---- 1. Basic Process Creation ----
    print()
    print("  1. CREATING AND STARTING PROCESSES")
    print("  " + "-" * 50)

    p = multiprocessing.Process(
        target=worker,          # Function to run
        args=("Chef-1", 0.5),   # Arguments (must be a tuple!)
        name="Chef-1"           # Optional: give it a name
    )
    p.start()                   # Start the process
    p.join()                    # Wait for it to finish
    print(f"    Exit code: {p.exitcode}")  # 0 = success
    print()

    # ---- 2. Multiple Processes ----
    print("  2. RUNNING MULTIPLE PROCESSES")
    print("  " + "-" * 50)

    processes = []
    for i in range(3):
        p = multiprocessing.Process(
            target=worker,
            args=(f"Worker-{i}", 0.3),
            name=f"Worker-{i}"
        )
        processes.append(p)
        p.start()

    for p in processes:
        p.join()
    print("    All processes finished!")
    print()

    # ---- 3. Process Information ----
    print("  3. PROCESS INFORMATION")
    print("  " + "-" * 50)
    print(f"    Current PID:        {os.getpid()}")
    print(f"    Parent PID:         {os.getppid()}")
    print(f"    CPU cores:          {multiprocessing.cpu_count()}")
    print()
    print(f"    You have {multiprocessing.cpu_count()} CPU cores.")
    print(f"    Multiprocessing can use ALL of them!")
    print()

    # ---- 4. Checking Process Status ----
    print("  4. CHECKING PROCESS STATUS")
    print("  " + "-" * 50)

    p = multiprocessing.Process(target=time.sleep, args=(0.5,))
    print(f"    Before start - is_alive: {p.is_alive()}, pid: {p.pid}")
    p.start()
    print(f"    After start  - is_alive: {p.is_alive()}, pid: {p.pid}")
    p.join()
    print(f"    After join   - is_alive: {p.is_alive()}, exitcode: {p.exitcode}")
    print()

    # ---- 5. Process vs Thread at a Glance ----
    print("  5. WHEN TO USE WHAT?")
    print("  " + "-" * 50)
    print("""
    +-------------------+------------------+--------------------+
    |                   |    THREADING     |  MULTIPROCESSING   |
    +-------------------+------------------+--------------------+
    | Memory            | Shared           | Separate (copies)  |
    | Overhead          | Low              | High               |
    | Best for          | I/O-bound tasks  | CPU-bound tasks    |
    | GIL limitation    | YES              | NO (bypasses GIL)  |
    | Communication     | Easy (shared)    | Needs Queue/Pipe   |
    | Race conditions   | YES (danger!)    | Less likely        |
    +-------------------+------------------+--------------------+
    """)

    # ---- Quick Reference ----
    print("=" * 60)
    print("  QUICK REFERENCE")
    print("=" * 60)
    print("""
    # Create
    p = multiprocessing.Process(target=func, args=(arg1,))

    # Start
    p.start()

    # Wait for completion
    p.join()
    p.join(timeout=5)      # Wait max 5 seconds

    # Info
    os.getpid()                  # Current process ID
    os.getppid()                 # Parent process ID
    multiprocessing.cpu_count()  # Number of CPU cores

    # Process object
    p.name                  # Process name
    p.pid                   # Process ID (after start)
    p.is_alive()            # Is it still running?
    p.exitcode              # Exit code (after join)
    p.terminate()           # Kill the process
    """)


if __name__ == "__main__":
    main()
