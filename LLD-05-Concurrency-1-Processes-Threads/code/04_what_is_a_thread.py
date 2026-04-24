"""
04 - What is a Thread?

A thread is a lightweight unit of execution INSIDE a process.
Multiple threads share the SAME memory and process ID.

Think of threads as multiple waiters in the SAME restaurant.
They share the kitchen, the tables, the menu - everything.

Run: python 04_what_is_a_thread.py
"""

import os
import threading
import time


def waiter_task(table_number):
    """This runs in a separate thread, but same process."""
    current = threading.current_thread()
    print(f"  [Thread '{current.name}']")
    print(f"    Serving table: {table_number}")
    print(f"    Thread ID:     {current.ident}")
    print(f"    Process PID:   {os.getpid()}  <-- SAME for all!")
    print()
    time.sleep(0.5)


def main():
    print("=" * 60)
    print("  WHAT IS A THREAD?")
    print("=" * 60)
    print()

    main_thread = threading.current_thread()
    print(f"  [Main Thread]")
    print(f"    Name:       {main_thread.name}")
    print(f"    Thread ID:  {main_thread.ident}")
    print(f"    Process PID: {os.getpid()}")
    print()

    print("  Creating 3 worker threads...")
    print()

    threads = []
    for i in range(1, 4):
        t = threading.Thread(
            target=waiter_task,
            args=(i,),
            name=f"Waiter-{i}"  # Give threads meaningful names!
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("-" * 60)
    print("  KEY TAKEAWAY:")
    print(f"    All threads share PID: {os.getpid()}")
    print("    But each has a DIFFERENT Thread ID.")
    print()
    print("    Threads = Waiters in the SAME restaurant")
    print("    Processes = SEPARATE restaurant branches")
    print("-" * 60)
    print()


if __name__ == "__main__":
    main()
