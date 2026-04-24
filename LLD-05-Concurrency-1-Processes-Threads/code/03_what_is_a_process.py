"""
03 - What is a Process?

A process is a running program. It has its own:
- Memory space
- Process ID (PID)
- Resources

When you create a child process, it gets a COMPLETELY SEPARATE
copy of everything. Think of it as opening a new restaurant branch.

Run: python 03_what_is_a_process.py
"""

import os
import multiprocessing
import time


def child_task(name):
    """This runs in a SEPARATE process."""
    print(f"  [Child '{name}']")
    print(f"    My PID:        {os.getpid()}")
    print(f"    My Parent PID: {os.getppid()}")
    print()


def main():
    print("=" * 60)
    print("  WHAT IS A PROCESS?")
    print("=" * 60)
    print()

    print(f"  [Parent Process]")
    print(f"    My PID: {os.getpid()}")
    print()

    print("  Creating 3 child processes...")
    print()

    children = []
    for name in ["Chef-A", "Chef-B", "Chef-C"]:
        p = multiprocessing.Process(target=child_task, args=(name,))
        children.append(p)
        p.start()

    # Wait for all children to finish
    for p in children:
        p.join()

    print("-" * 60)
    print("  KEY TAKEAWAY:")
    print(f"    Parent PID: {os.getpid()}")
    print("    Each child has a DIFFERENT PID.")
    print("    They are separate programs running independently.")
    print()
    print("    Like opening separate restaurant branches -")
    print("    each has its own kitchen, staff, and inventory.")
    print("-" * 60)
    print()


if __name__ == "__main__":
    main()
