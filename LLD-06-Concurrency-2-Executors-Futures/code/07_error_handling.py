"""
07_error_handling.py — What happens when tasks fail
=====================================================
With manual threads, exceptions vanish silently.
With Futures, exceptions are CAPTURED and re-raised on .result().
"""

import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


def timestamp():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


# ---------------------------------------------------------------------------
# A function that sometimes fails
# ---------------------------------------------------------------------------
def process_payment(payment_id):
    """Simulate processing a payment. Some will fail."""
    time.sleep(0.5)

    if payment_id == 3:
        raise ValueError(f"Payment {payment_id}: Invalid card number!")
    if payment_id == 7:
        raise ConnectionError(f"Payment {payment_id}: Gateway timeout!")
    if payment_id == 9:
        raise PermissionError(f"Payment {payment_id}: Insufficient funds!")

    return f"Payment {payment_id}: Success (${ payment_id * 100 })"


# ===========================================================================
# STEP 1: Exceptions are stored in the Future
# ===========================================================================
print("=" * 60)
print("STEP 1: Exceptions are stored, not lost")
print("=" * 60)
print()

with ThreadPoolExecutor(max_workers=5) as executor:
    future_ok = executor.submit(process_payment, 1)    # Will succeed
    future_bad = executor.submit(process_payment, 3)   # Will fail

    time.sleep(1)  # Wait for both to finish

    print(f"  Good future: done={future_ok.done()}")
    print(f"  Bad future:  done={future_bad.done()}")
    print()

    # The exception is stored inside the Future
    print(f"  Good future exception: {future_ok.exception()}")
    print(f"  Bad future exception:  {future_bad.exception()}")
    print()

    # .result() on the good future returns the value
    print(f"  Good result: {future_ok.result()}")

    # .result() on the bad future RE-RAISES the exception
    try:
        result = future_bad.result()
    except ValueError as e:
        print(f"  Bad result raised: {type(e).__name__}: {e}")

print()


# ===========================================================================
# STEP 2: Process all tasks, handling errors gracefully
# ===========================================================================
print("=" * 60)
print("STEP 2: Handle errors for a batch of tasks")
print("=" * 60)
print()

successes = 0
failures = 0

with ThreadPoolExecutor(max_workers=5) as executor:
    # Submit all 10 payments
    futures = {}
    for payment_id in range(1, 11):
        future = executor.submit(process_payment, payment_id)
        futures[future] = payment_id

    # Process as they complete
    for future in as_completed(futures):
        payment_id = futures[future]

        try:
            result = future.result()
            print(f"  [OK]    {result}")
            successes += 1
        except Exception as e:
            print(f"  [ERROR] Payment {payment_id}: {type(e).__name__}: {e}")
            failures += 1

print(f"\n  Summary: {successes} succeeded, {failures} failed")
print()


# ===========================================================================
# STEP 3: map() vs submit() error behavior
# ===========================================================================
print("=" * 60)
print("STEP 3: Error behavior with map() vs submit()")
print("=" * 60)
print()

print("  With map(): exception is raised when you ITERATE to that result")
print()

with ThreadPoolExecutor(max_workers=5) as executor:
    # map() runs all 5 tasks. Payment 3 will fail.
    results_iter = executor.map(process_payment, range(1, 6))

    # The exception is raised when we reach that position in the iterator
    for payment_id in range(1, 6):
        try:
            result = next(results_iter)
            print(f"  Payment {payment_id}: {result}")
        except Exception as e:
            print(f"  Payment {payment_id}: EXCEPTION -> {type(e).__name__}: {e}")
            break  # map() iterator stops after first exception!

print()
print("  NOTE: With map(), iteration STOPS at the first exception.")
print("  With submit() + as_completed(), you can handle each error individually.")
print()


# ===========================================================================
# BEST PRACTICE PATTERN
# ===========================================================================
print("=" * 60)
print("BEST PRACTICE: The try/except pattern")
print("=" * 60)
print("""
  with ThreadPoolExecutor(max_workers=5) as executor:
      futures = {
          executor.submit(task, arg): arg
          for arg in work_items
      }

      for future in as_completed(futures):
          arg = futures[future]
          try:
              result = future.result()
              # Handle success
          except SpecificError as e:
              # Handle known errors
          except Exception as e:
              # Handle unexpected errors
              logging.error(f"Task {arg} failed: {e}")

  KEY POINTS:
    - .exception() returns the exception (or None if success)
    - .result() re-raises the stored exception
    - Use try/except around .result() for safe error handling
    - Errors are NEVER silently lost (unlike raw threads!)
""")
