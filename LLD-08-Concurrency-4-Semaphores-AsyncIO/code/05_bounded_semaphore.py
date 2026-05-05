"""
BoundedSemaphore vs Semaphore
==============================
Regular Semaphore: you can release() more times than you acquire().
                   This is a BUG -- the count goes above the max!

BoundedSemaphore: raises ValueError if you release too many times.
                  Catches the bug immediately.
"""

import threading

print("=" * 50)
print("Regular Semaphore - allows over-release (BUG!)")
print("=" * 50)

sem = threading.Semaphore(2)
print(f"Created Semaphore(2)")
print(f"Internal counter: {sem._value}")

sem.acquire()
print(f"After acquire: counter = {sem._value}")

sem.release()
print(f"After release: counter = {sem._value}")

# BUG: releasing without acquiring first!
sem.release()
print(f"After EXTRA release: counter = {sem._value}")  # Now 3! Was supposed to be max 2!

sem.release()
print(f"After ANOTHER extra release: counter = {sem._value}")  # Now 4!

print(f"\nPROBLEM: Counter is now {sem._value}, but max should be 2!")
print("This means 4 threads could enter at once instead of 2.")

print("\n" + "=" * 50)
print("BoundedSemaphore - catches the bug!")
print("=" * 50)

bsem = threading.BoundedSemaphore(2)
print(f"Created BoundedSemaphore(2)")
print(f"Internal counter: {bsem._value}")

bsem.acquire()
print(f"After acquire: counter = {bsem._value}")

bsem.release()
print(f"After release: counter = {bsem._value}")

# Try to over-release
print(f"\nTrying extra release...")
try:
    bsem.release()
except ValueError as e:
    print(f"ValueError: {e}")
    print("BoundedSemaphore caught the bug!")

print("\n--- Rule of thumb ---")
print("Always use BoundedSemaphore unless you have a reason not to.")
print("It catches accidental over-releases that could cause subtle bugs.")
