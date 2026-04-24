"""
09 - Threading API Reference

A clean reference for the most common threading operations.
Bookmark this file! You'll use these patterns often.

Run: python 09_thread_api.py
"""

import threading
import time
import os


def greet(name, delay):
    """A simple task for our threads."""
    time.sleep(delay)
    print(f"    Hello from {name}! (thread: {threading.current_thread().name})")


def background_worker():
    """A daemon thread that runs forever (until main thread exits)."""
    while True:
        time.sleep(0.5)
        # This would keep running, but daemon=True kills it when main exits


def main():
    print("=" * 60)
    print("  THREADING API REFERENCE")
    print("=" * 60)

    # ---- 1. Basic Thread Creation ----
    print()
    print("  1. CREATING AND STARTING THREADS")
    print("  " + "-" * 50)

    t = threading.Thread(
        target=greet,           # Function to run
        args=("Alice", 0.5),    # Arguments (must be a tuple!)
        name="Greeter-1"        # Optional: give it a name
    )
    t.start()                   # Start the thread
    t.join()                    # Wait for it to finish
    print("    Thread finished!")
    print()

    # ---- 2. Multiple Threads ----
    print("  2. RUNNING MULTIPLE THREADS")
    print("  " + "-" * 50)

    threads = []
    for i in range(3):
        t = threading.Thread(
            target=greet,
            args=(f"Worker-{i}", 0.3),
            name=f"Worker-{i}"
        )
        threads.append(t)
        t.start()

    # Always join ALL threads
    for t in threads:
        t.join()
    print("    All threads finished!")
    print()

    # ---- 3. Thread Information ----
    print("  3. THREAD INFORMATION")
    print("  " + "-" * 50)
    current = threading.current_thread()
    print(f"    Current thread: {current.name}")
    print(f"    Thread ID:      {current.ident}")
    print(f"    Active threads: {threading.active_count()}")
    print(f"    All threads:    {[t.name for t in threading.enumerate()]}")
    print()

    # ---- 4. Daemon Threads ----
    print("  4. DAEMON THREADS")
    print("  " + "-" * 50)
    print("    Daemon threads are 'background' threads.")
    print("    They are killed automatically when the main thread exits.")
    print()

    daemon = threading.Thread(
        target=background_worker,
        daemon=True,            # Dies when main thread exits
        name="BackgroundWorker"
    )
    daemon.start()
    print(f"    Daemon started: {daemon.name}")
    print(f"    Is daemon?      {daemon.daemon}")
    print(f"    Is alive?       {daemon.is_alive()}")
    print()
    # We don't join daemon threads - they'll be killed when main exits

    # ---- 5. Checking Thread Status ----
    print("  5. CHECKING THREAD STATUS")
    print("  " + "-" * 50)

    t = threading.Thread(target=time.sleep, args=(0.5,), name="Sleeper")
    print(f"    Before start - is_alive: {t.is_alive()}")
    t.start()
    print(f"    After start  - is_alive: {t.is_alive()}")
    t.join()
    print(f"    After join   - is_alive: {t.is_alive()}")
    print()

    # ---- Quick Reference ----
    print("=" * 60)
    print("  QUICK REFERENCE")
    print("=" * 60)
    print("""
    # Create
    t = threading.Thread(target=func, args=(arg1, arg2))

    # Start
    t.start()

    # Wait for completion
    t.join()
    t.join(timeout=5)      # Wait max 5 seconds

    # Info
    threading.current_thread()   # Current thread object
    threading.active_count()     # Number of active threads
    threading.enumerate()        # List of active threads

    # Thread object
    t.name                  # Thread name
    t.ident                 # Thread ID
    t.is_alive()            # Is it still running?
    t.daemon                # Is it a daemon thread?
    """)


if __name__ == "__main__":
    main()
