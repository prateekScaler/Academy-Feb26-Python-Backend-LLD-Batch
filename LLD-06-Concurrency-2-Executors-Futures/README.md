
# LLD-06: Concurrency-2 — Executors, Futures, and Thread/Process Pools

> Last class you learned how to create threads and processes by hand. This class, you learn how to **stop doing that** and let Python manage them for you.

---

## 1. Deep Recap: The GIL (What We Didn't Finish Last Class)

We introduced the GIL in Concurrency-1 but didn't go deep enough. This matters. If you don't understand GIL, you'll make wrong decisions about threads vs processes for the rest of your career. So let's do this properly.

### What is the GIL?

**GIL = Global Interpreter Lock.** It's a mutex (a lock) inside CPython — the standard Python interpreter you use every day.

The rule is simple and brutal:

**Only ONE thread can execute Python bytecode at any given instant.**

That's it. Even if your machine has 8 cores, only 1 core is running Python code at a time. The other 7 sit idle (for CPU-bound threaded code).

```
WITHOUT GIL (Java, Go, Rust):
Core 1: [Thread 1 ████████████████]
Core 2: [Thread 2 ████████████████]
Core 3: [Thread 3 ████████████████]
Core 4: [Thread 4 ████████████████]
All 4 threads truly running simultaneously. Full CPU utilization.

WITH GIL (Python):
Core 1: [T1][T2][T3][T4][T1][T2][T3][T4]
Core 2: [idle ...]
Core 3: [idle ...]
Core 4: [idle ...]
Only 1 thread runs at a time. Threads take turns. 3 cores wasted.
```

> **Question:** If Python threads can only run one at a time, why does Python even HAVE threads?

<details>
<summary>Answer</summary>

Because most real-world programs aren't doing heavy math all the time. They're **waiting** — for API responses, database queries, file reads. During that wait, the GIL is **released**, and another thread can run. Threads are useless for CPU-bound work in Python, but they're excellent for I/O-bound work.

</details>

### Are Python Threads Real OS Threads?

**YES.** This is a common misconception.

Python threads are **1:1 mapped** to real operating system threads. The OS sees them. The OS schedules them. The OS puts them on different cores.

But here's the problem:

```
What the OS sees:                    What actually happens:

OS Thread 1 --> Core 1  (running)    Has GIL --> executing Python
OS Thread 2 --> Core 2  (running)    Waiting for GIL --> spinning idle!
OS Thread 3 --> Core 3  (running)    Waiting for GIL --> spinning idle!

The OS thinks all 3 threads are "running" on 3 cores.
In reality, only 1 is doing Python work. The other 2 are
blocked on the GIL mutex, wasting CPU cycles.
```

**The irony:** You pay the full cost of OS threads (heavy, ~1-8MB stack each, expensive context switches) but get **none of the CPU parallelism**. The worst of both worlds for CPU-bound work.

### GIL Timeline Diagrams

How GIL affects CPU-bound vs I/O-bound work is completely different.

**CPU-bound (GIL held, threads take turns every ~5ms):**

```
CPython releases the GIL every ~5ms (sys.getswitchinterval())
to give other threads a chance. But it's just taking turns.

Thread 1: ██████░░░░░░██████░░░░░░██████░░░░░░
Thread 2: ░░░░░░██████░░░░░░██████░░░░░░██████
                ^           ^           ^
                GIL switches every ~5ms
                No speedup! Actually SLOWER than 1 thread
                (context switching overhead for zero benefit)
```

**I/O-bound (GIL released during wait):**

```
Thread 1: ██░░░░░░░░░░░░░░░░░░░░██████
Thread 2: ░░████████████████░░░░░░░░░░
             ^                  ^
             Thread 1 starts an API call, releases GIL.
             Thread 2 grabs GIL immediately, runs freely
             for the ENTIRE duration of the wait.
             REAL speedup!
```

> **Question:** You have 2 threads each doing `for i in range(100_000_000): x += i`. With GIL, will this be faster than running them sequentially?

<details>
<summary>Answer</summary>

**No. It will actually be SLOWER.** Both threads are CPU-bound — neither releases the GIL voluntarily. They take turns every ~5ms, adding context-switching overhead on top of the same total computation. Sequential would be faster because there's no switching cost.

</details>

### What Releases the GIL?

Any operation where Python calls out to the OS or a C library and **waits**:

| Releases GIL (I/O operations) | Does NOT release GIL (CPU work) |
|---|---|
| `time.sleep()` | `for i in range(10_000_000)` |
| `requests.get()` / `urllib.request` | `x = sum(big_list)` |
| `open().read()` / `open().write()` | Image pixel manipulation |
| `socket.recv()` / `socket.send()` | Sorting a large list |
| `subprocess.run()` | Dictionary/set operations |
| Database queries (psycopg2, etc.) | String concatenation in loops |

**The rule of thumb:** If Python is waiting for something external, GIL is released. If Python is crunching numbers, GIL is held.

### Why Does the GIL Exist?

CPython (the standard Python implementation) uses **reference counting** for memory management. Every object in Python has a reference count — how many variables point to it. When the count hits 0, the object is freed.

```python
a = []     # list object refcount = 1
b = a      # refcount = 2
del a      # refcount = 1
del b      # refcount = 0 --> freed!
```

Reference counting is NOT thread-safe. If two threads modify a reference count at the same time, you get corruption — objects freed too early (crash) or never freed (memory leak).

The GIL is the simplest fix: only let one thread touch Python objects at a time. It's crude but effective. No per-object locking, no complex atomic operations — just one big lock.

> **Question:** Java doesn't have a GIL. How does it handle thread-safe memory management?

<details>
<summary>Answer</summary>

Java uses **garbage collection** (GC) instead of reference counting. The GC runs in its own thread, scans all objects periodically, and frees unreachable ones. This approach is thread-safe by design — it doesn't need a global lock. The tradeoff: GC pauses (brief freezes while the collector runs), which Python avoids with reference counting. Every design has tradeoffs.

</details>

### Language Comparison

| Language | GIL? | True parallel threads? | Concurrency model |
|---|---|---|---|
| **Python** (CPython) | Yes | No (use `multiprocessing`) | Threads for I/O, processes for CPU |
| **Java** | No | Yes | Native OS threads, thread pools |
| **Go** | No | Yes | Goroutines (lightweight, M:N scheduling) |
| **Rust** | No | Yes | Ownership system prevents data races at compile time |
| **JavaScript** | Single-threaded | No (Web Workers for parallel) | Event loop (like `asyncio`) |

**Why the difference?** Java, Go, and Rust were designed with concurrency in mind from the start. Python was designed for simplicity and readability; concurrency was bolted on later. The GIL was the simplest solution that kept the interpreter correct.

> **Note:** Python 3.13+ is experimenting with a "no-GIL" build (`--disable-gil`). It's still experimental, but it signals that the GIL may eventually become optional.

### The Workaround: multiprocessing

Each **process** has its own Python interpreter, its own GIL, its own memory space. So:

```
multiprocessing (each process = separate GIL):
Process 1 (GIL-1): [████████████████]  --> Core 1
Process 2 (GIL-2): [████████████████]  --> Core 2
Process 3 (GIL-3): [████████████████]  --> Core 3
Process 4 (GIL-4): [████████████████]  --> Core 4

True parallelism! Each process runs on its own core
with its own GIL. They don't interfere with each other.
```

**The decision tree for Python concurrency:**

```
Is your task CPU-bound or I/O-bound?

I/O-bound (waiting for network, DB, files)
  --> Use threads (GIL is released during wait)

CPU-bound (heavy computation)
  --> Use processes (each has its own GIL)
  --> Never use threads (GIL makes it SLOWER)
```

> **Question:** Your Django app needs to (A) call 3 payment APIs concurrently and (B) resize 100 uploaded images. What do you use for each?

<details>
<summary>Answer</summary>

**(A) Threads** (or ThreadPoolExecutor). API calls are I/O-bound — the CPU waits for network responses. GIL is released during the wait, so threads provide real speedup.

**(B) Processes** (or ProcessPoolExecutor). Image resizing is CPU-bound — heavy pixel math. Threads would be limited by the GIL. Processes bypass it entirely.

</details>

---

## 2. Recap Quiz from Concurrency-1

Quick check before we move forward. No peeking.

**Q1:** Process vs Thread — is memory shared or separate?

<details>
<summary>Answer</summary>

**Processes:** separate, isolated memory. Process A cannot see Process B's variables. **Threads (within the same process):** shared memory — same heap, same globals. Fast communication but dangerous (race conditions).

</details>

**Q2:** CPU-bound work — use threads or processes?

<details>
<summary>Answer</summary>

**Processes.** CPU-bound work keeps the GIL held (in Python), so threads take turns and are actually slower than sequential. Processes bypass the GIL entirely — each gets its own interpreter and runs on its own core.

</details>

**Q3:** What does context switching cost?

<details>
<summary>Answer</summary>

Time. The OS saves the current task's state (registers, stack pointer, program counter), loads another task's state, and resumes. For threads within the same process, it's relatively cheap (same memory mappings). For processes, it's expensive (TLB flush, new memory mappings). Either way, it's not free — too much switching wastes time on overhead instead of actual work.

</details>

**Q4:** 1 CPU core, 3 threads — concurrent or parallel?

<details>
<summary>Answer</summary>

**Concurrent but NOT parallel.** 1 core can only execute 1 thread at any instant. The OS rapidly switches between the 3 threads (context switching), creating the illusion of parallelism, but at any given moment only 1 thread is running. You need multiple cores for true parallelism.

</details>

---

## 3. The Problem with Manual Thread Management

Last class you wrote code like this:

```python
import threading
import time

def fetch_url(url):
    print(f"Fetching {url}...")
    time.sleep(1)  # simulate network call
    print(f"Done: {url}")

urls = [
    "https://api.example.com/users",
    "https://api.example.com/orders",
    "https://api.example.com/payments",
    "https://api.example.com/notifications",
    "https://api.example.com/analytics",
]

# Manual thread management
threads = []
for url in urls:
    t = threading.Thread(target=fetch_url, args=(url,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

This works. But think about the problems:

**1. Boilerplate.** Create list, create thread, append, start, join. Every. Single. Time.

**2. No return values.** `fetch_url` can't return data. Thread targets return `None`. You'd need a shared list and manual coordination to collect results.

**3. No error handling.** If one thread raises an exception, it dies silently. The main thread has no idea.

**4. No thread reuse.** Each task creates a new thread, which the OS destroys after it finishes. Creating and destroying threads is expensive.

**5. No limit on concurrency.** What if you have 10,000 URLs?

```python
# This will try to create 10,000 OS threads simultaneously
for url in ten_thousand_urls:
    t = threading.Thread(target=fetch_url, args=(url,))
    t.start()
# Your machine: "I'm going to die now."
```

10,000 OS threads = ~10GB of stack memory. Your machine will slow to a crawl or crash.

> **Question:** Why is creating 10,000 threads bad but creating 10,000 tasks is fine?

<details>
<summary>Answer</summary>

Threads are OS resources. Each one costs ~1-8MB of stack memory, a TCB (thread control block), and context-switching overhead. 10,000 of those crushes your machine. But if you have a **pool** of, say, 20 threads picking tasks from a **queue** of 10,000 tasks, only 20 threads exist at any time. The tasks wait in line, not in memory. This is exactly what thread pools solve.

</details>

---

## 4. Thread Pools — The Concept

The idea is simple:

Instead of creating 10,000 threads, create a **pool** of N worker threads. Put tasks into a **queue**. Workers pick up tasks one by one, finish them, then pick up the next.

```
Task Queue:  [task1] [task2] [task3] [task4] [task5] [task6] [task7] [task8]
                 |        |        |
                 v        v        v
Pool:      [Worker 1] [Worker 2] [Worker 3]
           picks task1  picks task2  picks task3
           finishes --> finishes --> finishes -->
           picks task4  picks task5  picks task6
           finishes --> finishes --> finishes -->
           picks task7  picks task8   (idle, waits)
```

**Key benefits:**
- Workers are **reused** — no creation/destruction overhead per task
- Limited concurrency — only N threads exist, no matter how many tasks
- Built-in queue — tasks wait in line, not in memory
- Clean lifecycle — pool starts up, does work, shuts down

### Restaurant Analogy

Instead of hiring a new waiter for every customer and firing them when they're done (insane), you have **5 permanent waiters** and a queue of orders. Customer #6 waits until a waiter is free. Customer #100 waits in line. Only 5 waiters exist at any time.

```
Order Queue:   [C1] [C2] [C3] [C4] [C5] [C6] [C7]
                 |    |    |    |    |
                 v    v    v    v    v
Waiters:     [W1]  [W2]  [W3] [W4] [W5]
             serves serves serves serves serves
              C1    C2     C3   C4    C5
             done! -----> picks up C6
                   done! -----> picks up C7
```

No matter how many customers, only 5 waiters. Manageable. Efficient.

---

## 5. ThreadPoolExecutor — Python's Thread Pool

Python gives you this in the `concurrent.futures` module. It's the standard way to do managed concurrency.

```python
from concurrent.futures import ThreadPoolExecutor
import time

def fetch_url(url):
    print(f"Fetching {url}...")
    time.sleep(1)  # simulate network I/O
    return f"Data from {url}"

urls = [
    "https://api.example.com/users",
    "https://api.example.com/orders",
    "https://api.example.com/payments",
    "https://api.example.com/notifications",
    "https://api.example.com/analytics",
]

# Create a pool of 3 worker threads
with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(fetch_url, urls)

for result in results:
    print(result)
```

Compare this with the manual version from Section 3. No thread creation. No appending. No joining. No boilerplate. And you get **return values**.

### What's Happening Here

- `ThreadPoolExecutor(max_workers=3)` — create a pool of 3 threads
- `executor.map(func, iterable)` — apply `func` to each item, like `map()` but parallel
- `with` (context manager) — automatically shuts down the pool and joins all threads when done
- Results come back **in the same order** as the input iterable

### The Two Executors

| | `ThreadPoolExecutor` | `ProcessPoolExecutor` |
|---|---|---|
| **Uses** | Threads | Processes |
| **Best for** | I/O-bound (API calls, DB, files) | CPU-bound (image resize, ML, hashing) |
| **GIL** | Limited by GIL for CPU work | Bypasses GIL (separate interpreters) |
| **Memory** | Shared (fast, needs care) | Separate (safe, higher overhead) |
| **Import** | `from concurrent.futures import ThreadPoolExecutor` | `from concurrent.futures import ProcessPoolExecutor` |
| **API** | **Identical** | **Identical** |

The API is exactly the same. Switching between threads and processes is literally changing one word:

```python
# I/O-bound: use threads
with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(fetch_url, urls)

# CPU-bound: use processes (just change the class name!)
with ProcessPoolExecutor(max_workers=4) as executor:
    results = executor.map(resize_image, images)
```

### Two Ways to Submit Work

**`executor.map(func, iterable)`** — batch mode, like built-in `map()`

```python
# Process all URLs, get results in order
results = executor.map(fetch_url, urls)
for result in results:
    print(result)
```

**`executor.submit(func, *args)`** — single task, returns a Future

```python
# Submit one task, get a Future back
future = executor.submit(fetch_url, "https://api.example.com/users")
# ... do other stuff ...
result = future.result()  # blocks until done
```

`map()` is simpler. `submit()` gives you more control. We'll explore `submit()` and Futures next.

---

## 6. Futures — Getting Results Back

This is the **key concept** of this class.

### What is a Future?

A **Future** is a placeholder for a result that hasn't happened yet.

Think of ordering food at a restaurant:

1. You order a burger. The waiter gives you a **receipt** (the Future).
2. The kitchen starts cooking (the task is running).
3. You wait. The receipt doesn't have your burger yet. But it's a **promise** that the burger is coming.
4. Eventually the burger is ready. Your receipt "resolves" — now you can get the food (the result).

```python
from concurrent.futures import ThreadPoolExecutor
import time

def fetch_url(url):
    time.sleep(2)
    return f"Data from {url}"

with ThreadPoolExecutor(max_workers=3) as executor:
    # submit() returns a Future immediately — doesn't block!
    future = executor.submit(fetch_url, "https://api.example.com/users")

    print(type(future))       # <class 'concurrent.futures._base.Future'>
    print(future.done())      # False — still cooking

    result = future.result()  # BLOCKS here until the result is ready
    print(future.done())      # True — done!
    print(result)             # "Data from https://api.example.com/users"
```

### Future Methods

| Method | What it does |
|---|---|
| `future.result()` | Block until the result is ready, then return it |
| `future.result(timeout=5)` | Block for at most 5 seconds, then raise `TimeoutError` |
| `future.done()` | Returns `True` if the task finished (doesn't block) |
| `future.cancelled()` | Returns `True` if the task was cancelled |
| `future.cancel()` | Attempts to cancel (only works if not yet started) |
| `future.exception()` | Returns the exception if the task failed, or `None` |

### Submitting Multiple Tasks

```python
from concurrent.futures import ThreadPoolExecutor
import time

def fetch_url(url):
    time.sleep(1)
    return f"Data from {url}"

urls = [
    "https://api.example.com/users",
    "https://api.example.com/orders",
    "https://api.example.com/payments",
]

with ThreadPoolExecutor(max_workers=3) as executor:
    # Submit all tasks, collect Futures
    futures = [executor.submit(fetch_url, url) for url in urls]

    # Get results (in submission order)
    for future in futures:
        print(future.result())
```

### `as_completed()` — Process Results As They Finish

What if some tasks finish faster than others? `as_completed()` yields Futures in the order they **finish**, not the order they were submitted.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time, random

def fetch_url(url):
    delay = random.uniform(0.5, 3.0)
    time.sleep(delay)
    return f"{url} (took {delay:.1f}s)"

urls = [
    "https://api.example.com/users",
    "https://api.example.com/orders",
    "https://api.example.com/payments",
    "https://api.example.com/notifications",
]

with ThreadPoolExecutor(max_workers=4) as executor:
    # Submit all tasks
    future_to_url = {executor.submit(fetch_url, url): url for url in urls}

    # Process results as they arrive — fastest first!
    for future in as_completed(future_to_url):
        url = future_to_url[future]
        try:
            result = future.result()
            print(f"Completed: {result}")
        except Exception as e:
            print(f"Failed: {url} — {e}")
```

**Why use `as_completed()`?** If task A takes 10 seconds and task B takes 1 second, iterating in submission order would wait 10 seconds before seeing B's result. `as_completed()` gives you B's result after 1 second.

> **Question:** `executor.map()` vs `executor.submit()` + `as_completed()` — when would you use each?

<details>
<summary>Answer</summary>

Use `executor.map()` when you want results **in the same order** as the input and all tasks are similar. Use `executor.submit()` + `as_completed()` when you want results **as fast as possible** (fastest first), need per-task error handling, or tasks have different functions/arguments.

</details>

### `wait()` — Wait for Specific Conditions

```python
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED, ALL_COMPLETED
import time

def fetch_url(url):
    time.sleep(1)
    return f"Data from {url}"

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(fetch_url, url) for url in urls]

    # Wait until the FIRST one finishes
    done, pending = wait(futures, return_when=FIRST_COMPLETED)
    print(f"First done: {done.pop().result()}")
    print(f"Still pending: {len(pending)}")

    # Wait for ALL to finish
    done, pending = wait(futures, return_when=ALL_COMPLETED)
    print(f"All done: {len(done)} completed")
```

**`return_when` options:**
- `FIRST_COMPLETED` — return as soon as ANY future finishes
- `FIRST_EXCEPTION` — return as soon as ANY future raises an exception
- `ALL_COMPLETED` — wait for everything (default)

---

## 7. ProcessPoolExecutor — Same API for CPU-bound

Remember: `ThreadPoolExecutor` for I/O-bound, `ProcessPoolExecutor` for CPU-bound. The API is **identical**.

```python
from concurrent.futures import ProcessPoolExecutor
import math

def is_prime(n):
    """CPU-bound: checks if n is prime (heavy computation for large n)."""
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

numbers = [112272535095293, 112582705942171, 112272535095293,
           115280095190773, 115797848077099, 1099726899285419]

if __name__ == "__main__":
    # Use ProcessPoolExecutor — each process has its own GIL
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = executor.map(is_prime, numbers)

    for number, prime in zip(numbers, results):
        print(f"{number} is prime: {prime}")
```

**Important:** `ProcessPoolExecutor` requires `if __name__ == "__main__":` on Windows and macOS (to prevent infinite process spawning).

> **Question:** Why can't you just use `ThreadPoolExecutor` for the prime-checking code above?

<details>
<summary>Answer</summary>

`is_prime()` is pure CPU computation — no I/O, no waiting, no GIL release. With `ThreadPoolExecutor`, all threads would fight over the GIL, taking turns every ~5ms. It would be **slower** than sequential (overhead of switching, zero parallelism). `ProcessPoolExecutor` creates separate processes, each with its own GIL and its own core, achieving true parallelism.

</details>

---

## 8. Error Handling in Futures

What happens when a task raises an exception?

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def risky_fetch(url):
    if "bad" in url:
        raise ConnectionError(f"Cannot connect to {url}")
    return f"Data from {url}"

urls = [
    "https://api.example.com/users",
    "https://bad-server.example.com/data",
    "https://api.example.com/orders",
]

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {executor.submit(risky_fetch, url): url for url in urls}

    for future in as_completed(futures):
        url = futures[future]
        try:
            result = future.result()  # Re-raises the exception here!
            print(f"Success: {result}")
        except ConnectionError as e:
            print(f"Error for {url}: {e}")
```

**Key behavior:**
- The exception does NOT crash the pool or other tasks
- The exception is **stored** inside the Future
- It's **re-raised** when you call `future.result()`
- If you never call `.result()`, you'll never see the error (silent failure!)
- Always wrap `future.result()` in try/except

> **Question:** What happens if you use `executor.map()` and one of the tasks raises an exception?

<details>
<summary>Answer</summary>

The exception is raised when you **iterate** over the results. `executor.map()` returns a generator-like object. When you reach the failed task's result during iteration, the exception is raised at that point. Unlike `submit()`, you can't catch errors per-task easily with `map()` — the iteration stops at the first error unless you wrap the target function itself in try/except.

</details>

---

## 9. Real-World Examples

### Example 1: Download 100 URLs with ThreadPoolExecutor

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request
import time

def fetch_url(url):
    """I/O-bound: network wait."""
    resp = urllib.request.urlopen(url, timeout=10)
    data = resp.read()
    return url, len(data)

urls = [f"https://httpbin.org/delay/1" for _ in range(10)]

# Sequential: ~10 seconds
start = time.time()
for url in urls:
    fetch_url(url)
print(f"Sequential: {time.time() - start:.1f}s")

# ThreadPoolExecutor: ~1-2 seconds
start = time.time()
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(fetch_url, url): url for url in urls}
    for future in as_completed(futures):
        url, size = future.result()
        print(f"  {url[:30]}... — {size} bytes")
print(f"Threaded: {time.time() - start:.1f}s")
```

### Example 2: Resize Images with ProcessPoolExecutor

```python
from concurrent.futures import ProcessPoolExecutor
import time

def resize_image(image_path):
    """CPU-bound: pixel manipulation (simulated)."""
    # In reality: PIL/Pillow resize
    total = 0
    for i in range(5_000_000):  # simulate heavy computation
        total += i
    return f"Resized: {image_path}"

images = [f"photo_{i}.jpg" for i in range(8)]

if __name__ == "__main__":
    # Sequential
    start = time.time()
    for img in images:
        resize_image(img)
    print(f"Sequential: {time.time() - start:.1f}s")

    # ProcessPoolExecutor
    start = time.time()
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(resize_image, images))
    print(f"Parallel:   {time.time() - start:.1f}s")
```

### Example 3: Django — Batch API Calls

```python
# In a Django view: verify payment AND send notifications concurrently

from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

def verify_payment(order_id):
    """Call Razorpay API to verify payment."""
    resp = requests.get(f"https://api.razorpay.com/v1/orders/{order_id}")
    return resp.json()

def send_email(user_email, message):
    """Call email service API."""
    requests.post("https://api.sendgrid.com/v3/mail/send", json={
        "to": user_email, "body": message
    })
    return "email sent"

def send_sms(phone, message):
    """Call SMS service API."""
    requests.post("https://api.twilio.com/messages", json={
        "to": phone, "body": message
    })
    return "sms sent"

# In your Django view:
def process_order(request, order_id):
    with ThreadPoolExecutor(max_workers=3) as executor:
        payment_future = executor.submit(verify_payment, order_id)
        email_future = executor.submit(send_email, "user@example.com", "Order confirmed!")
        sms_future = executor.submit(send_sms, "+91999999999", "Order confirmed!")

        payment_status = payment_future.result()  # wait for payment verification
        email_status = email_future.result()       # wait for email
        sms_status = sms_future.result()           # wait for SMS

    # All 3 API calls ran concurrently instead of sequentially
    # Sequential: 500ms + 300ms + 200ms = 1000ms
    # Concurrent: max(500ms, 300ms, 200ms) = 500ms
```

---

## 10. How Many Workers?

Choosing `max_workers` matters. Too few = underutilized. Too many = thrashing.

### I/O-bound (ThreadPoolExecutor)

Workers spend most of their time **waiting**. You can have many more workers than CPU cores.

```python
# I/O-bound: many workers are fine (they're mostly sleeping)
with ThreadPoolExecutor(max_workers=20) as executor:
    results = executor.map(fetch_url, urls)

# Rule of thumb: 20-100 workers for I/O-bound tasks
# More workers = more concurrent I/O operations
# Limited by: network bandwidth, server rate limits, file descriptor limits
```

### CPU-bound (ProcessPoolExecutor)

Workers need actual CPU cores. More workers than cores = context switching waste.

```python
import os

# CPU-bound: workers = number of CPU cores
with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
    results = executor.map(resize_image, images)

# More workers than cores = SLOWER (context switching overhead)
```

### Defaults

```python
import os

# ThreadPoolExecutor default:
# min(32, os.cpu_count() + 4)
# On a 4-core machine: min(32, 8) = 8 workers

# ProcessPoolExecutor default:
# os.cpu_count()
# On a 4-core machine: 4 workers
```

### Quick Reference

| Scenario | Executor | Workers |
|---|---|---|
| Fetch 100 URLs | `ThreadPoolExecutor` | 20-50 |
| Query 10 databases | `ThreadPoolExecutor` | 10 |
| Resize 1000 images | `ProcessPoolExecutor` | `os.cpu_count()` |
| Hash 10,000 passwords | `ProcessPoolExecutor` | `os.cpu_count()` |
| Call 3 payment APIs | `ThreadPoolExecutor` | 3 |

> **Question:** You have an 8-core machine and need to resize 100 images. You set `max_workers=100` on a ProcessPoolExecutor. Faster?

<details>
<summary>Answer</summary>

**No, significantly slower.** You'd create 100 OS processes (huge memory overhead) but only 8 can run at once. The other 92 sit idle and context-switch. Optimal is `max_workers=8` (one per core). For CPU-bound, more processes than cores is always counterproductive.

</details>

---

## 11. Connecting to What's Next

| Today (Concurrency-2) | Concurrency-3 | Concurrency-4 |
|---|---|---|
| Thread/Process Pools | Locks, Semaphores, Deadlocks | Async I/O (`asyncio`) |
| Executors & Futures | Safe shared state | Event-loop based concurrency |
| Managed concurrency | What happens when threads share data? | Single-thread, thousands of tasks |

**Today** you learned to let Python manage threads/processes for you. **Next class** we tackle the danger of shared memory — what happens when two threads modify the same variable? Spoiler: bad things. Locks fix it.

---

## 12. Key Takeaways

1. **GIL** = only 1 thread runs Python bytecode at a time. Threads help for I/O (GIL released during wait), not for CPU work.
2. **Thread pools** reuse a fixed set of workers instead of creating/destroying threads per task.
3. **`ThreadPoolExecutor`** = managed thread pool for I/O-bound work.
4. **`ProcessPoolExecutor`** = managed process pool for CPU-bound work. Same API.
5. **Futures** = placeholders for results that haven't happened yet. `.result()` blocks until ready.
6. **`as_completed()`** = process results in the order they finish (fastest first).
7. **Workers:** I/O-bound = many (20-100). CPU-bound = number of cores.

---

## 13. Resources

- [Real Python — concurrent.futures](https://realpython.com/python-concurrent-futures/) — Practical guide with examples
- [Python docs — concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html) — Official documentation
- [Real Python — Threading](https://realpython.com/intro-to-python-threading/) — Review from last class
- [PlanetScale — Processes & Threads](https://planetscale.com/blog/processes-and-threads) — Visual explainer from last class
- [PlanetScale — I/O & Latency](https://planetscale.com/blog/io-devices-and-latency) — Why I/O is slow at the hardware level
- [David Beazley — Understanding the Python GIL (YouTube)](https://www.youtube.com/watch?v=Obt-vMVdM8s) — Deep-dive GIL talk
