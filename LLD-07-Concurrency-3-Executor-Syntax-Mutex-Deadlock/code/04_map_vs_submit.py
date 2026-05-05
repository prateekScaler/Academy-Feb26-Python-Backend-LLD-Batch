"""
map() vs submit() — Same problem, two approaches
==================================================
map()   = simple, results in submission order
submit() + as_completed() = flexible, results in completion order
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Five API calls with different durations
api_calls = [
    ("User Profile",   1.5),
    ("Order History",  0.5),
    ("Recommendations", 3.0),
    ("Cart",           1.0),
    ("Notifications",  2.0),
]

def call_api(args):
    """For map() — takes a tuple since map() passes one arg at a time."""
    name, duration = args
    time.sleep(duration)
    return f"{name} ({duration}s)"

def call_api_named(name, duration):
    """For submit() — takes separate args."""
    time.sleep(duration)
    return f"{name} ({duration}s)"


print("=" * 60)
print("APPROACH 1: executor.map()  —  Results in SUBMISSION order")
print("=" * 60)

start = time.time()
with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(call_api, api_calls))

print(f"\nResults (submission order):")
for i, result in enumerate(results, 1):
    print(f"  {i}. {result}")
print(f"Total: {time.time() - start:.1f}s")


print("\n" + "=" * 60)
print("APPROACH 2: submit() + as_completed()  —  Results in COMPLETION order")
print("=" * 60)

start = time.time()
with ThreadPoolExecutor(max_workers=5) as executor:
    future_to_name = {}
    for name, duration in api_calls:
        future = executor.submit(call_api_named, name, duration)
        future_to_name[future] = name

    results = []
    for future in as_completed(future_to_name):
        result = future.result()
        elapsed = time.time() - start
        results.append(f"{result} — arrived at {elapsed:.1f}s")

print(f"\nResults (completion order):")
for i, result in enumerate(results, 1):
    print(f"  {i}. {result}")
print(f"Total: {time.time() - start:.1f}s")


print("\n" + "=" * 60)
print("WHEN TO USE WHICH?")
print("=" * 60)
print("""
  map():
    - Simple, clean syntax
    - Results in original order (good for: fetching pages 1,2,3...)
    - Cannot handle per-task exceptions easily

  submit() + as_completed():
    - More flexible
    - Results in completion order (good for: show fastest result first)
    - Can handle exceptions per task
    - Can add tasks dynamically

  Rule of thumb:
    Same function, same args pattern  -->  map()
    Different behavior per task       -->  submit()
    Need fastest-first processing     -->  submit() + as_completed()
""")
