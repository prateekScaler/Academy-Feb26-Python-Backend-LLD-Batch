
# LLD-07: Concurrency-2.5 — Executor Syntax, Parallel Merge Sort, and Mutex

> Last class: the IDEA behind executors and futures. Today: **actually use them, parallelize merge sort, and learn why shared data is dangerous.**

---

## 1. Recap — Last Class

No peeking at last class's notes. Answer from memory.

> **Question:** What is a thread pool? Draw it in your head.

```
Tasks:  [t1] [t2] [t3] [t4] [t5] [t6]
           |      |      |
           v      v      v
Pool: [Worker1] [Worker2] [Worker3]
        picks t1  picks t2  picks t3
        finishes
        picks t4 ...
```

<details>
<summary>Answer</summary>

A fixed set of reusable threads that pick tasks from a queue. Workers finish one task, grab the next. No thread creation/destruction per task. 3 workers handle 6 tasks by reusing themselves.

</details>

> **Question:** What is a Future?

<details>
<summary>Answer</summary>

A receipt/placeholder for a result that hasn't arrived yet. You submit a task, get a Future back immediately, check later if it's done. Like a restaurant receipt — food isn't ready, but the receipt promises it will be. Today we learn the actual methods (`.done()`, `.result()`, `as_completed()`).

</details>

---

## 2. Normal Threads Can't Return Values

You want to fetch 3 URLs and collect their responses.

### Step 1: What we want

```python
def fetch(url):
    time.sleep(1)  # Simulate network call
    return f"{url}: 200 OK"

# We want to call fetch() on 50 URLs in parallel
# and collect all 50 results.
```

### Step 2: We try using threads

```python
import threading, time

def fetch(url):
    time.sleep(1)
    return f"{url}: 200 OK"  # This return value goes... where?

t = threading.Thread(target=fetch, args=("a.com",))
t.start()
result = t.join()
print(result)  # None! thread.join() does NOT return the function's result.
```

> **Question:** `fetch()` returns `"a.com: 200 OK"`. But `t.join()` gives us `None`. How do we get the result?

<details>
<summary>Answer</summary>

We'd have to use a shared list and manually append inside `fetch()`. The function has to be rewritten to NOT return, but instead append to a global. Threads have no built-in way to return values.

</details>

### Step 3: The ugly workaround

```python
results = []  # Shared list

def fetch(url):
    time.sleep(1)
    results.append(f"{url}: 200 OK")  # Can't return — must append to shared list

threads = [threading.Thread(target=fetch, args=(url,))
           for url in ["a.com", "b.com", "c.com"]]
[t.start() for t in threads]
[t.join() for t in threads]

print(results)  # Order is random. No error handling. Ugly.
```

**Executors solve this.** They're not just about reusing threads — they give you **results back**:

- `executor.submit(func, args)` --> returns a **Future** (a handle to the result)
- `executor.map(func, iterable)` --> returns results directly, in order

---

## 3. `executor.submit()` — One Task, One Future

Submit a task. Get a Future back. Check it, wait for it, get the result.

### The Syntax

```python
from concurrent.futures import ThreadPoolExecutor
import time

def fetch(url):
    time.sleep(2)
    return f"{url}: 200 OK"

with ThreadPoolExecutor(max_workers=3) as executor:

    # submit() returns a Future IMMEDIATELY
    future = executor.submit(fetch, "https://api.razorpay.com")

    print(future.done())         # False — still running
    result = future.result()     # BLOCKS until done, returns value
    print(future.done())         # True — finished!
    print(result)                # "https://api.razorpay.com: 200 OK"
```

### Future Lifecycle

```
executor.submit(fetch, url)
         |
         v
      PENDING          .done() = False — queued
         |
         v
      RUNNING          .done() = False — worker executing
         |
         v
      FINISHED         .done() = True — .result() returns value
```

### `.done()` — Non-blocking Check

> **Question:** What happens if you call `future.result()` before the task finishes?

<details>
<summary>Answer</summary>

It **BLOCKS** — your code pauses right there and waits until the task completes, then returns the result. Use `.result(timeout=5)` to wait max 5 seconds (raises `TimeoutError` if not done).

</details>

### Exception Handling

> **Question:** What if the task raises an exception?

```python
def broken():
    raise ValueError("oops")

future = executor.submit(broken)
future.result()  # ???
```

<details>
<summary>Answer</summary>

The exception is stored inside the Future. `.result()` re-raises it. You get `ValueError: oops` at the point you call `.result()`, not when the task fails. Handle it with try/except:

```python
try:
    result = future.result()
    print(f"Success: {result}")
except ValueError as e:
    print(f"Task failed: {e}")  # "Task failed: oops"
```

</details>

**Summary:**

- `executor.submit(func, *args)` --> returns a **Future** immediately
- `future.done()` --> True/False (non-blocking check)
- `future.result()` --> blocks until done, returns value or re-raises exception
- `future.result(timeout=N)` --> wait max N seconds, raises `TimeoutError`

---

## 4. `executor.map()` — Same Function, Many Inputs

When you have one function and a list of inputs, `map()` is cleaner than multiple `submit()` calls.

```python
from concurrent.futures import ThreadPoolExecutor
import time

def fetch(url):
    time.sleep(1)
    return f"{url}: OK"

urls = [f"api.com/{i}" for i in range(10)]

# map() = submit all + collect results in ORDER
with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(fetch, urls)

for r in results:
    print(r)
# Results in SUBMISSION order (not completion order)
# 10 tasks, 5 workers, 1s each -> ~2 seconds total
```

**Key properties:**

1. Returns results in **submission order** — always
2. Returns an **iterator**, not a list
3. **Same function** for all inputs
4. **Simpler syntax** — no Futures to manage

---

## 5. When to Use `map()` vs `submit()`

| | `executor.map()` | `executor.submit()` |
|---|---|---|
| **Best for** | Same function, list of inputs | Different functions, per-task control |
| **Result order** | Submission order (always) | Completion order (with `as_completed()`) |
| **Error handling** | Exception breaks iteration | Per-task try/except on `.result()` |
| **Syntax** | Simple — one line | More code, more control |

**Mental model:** if `map()` feels limiting, switch to `submit()`.

### Scenario 1: Download 100 product images — same function `download(url)` for each

Use **`map()`** — one line:

```python
# map: one line
results = list(executor.map(download, urls))

# submit: more boilerplate for the same thing
futures = [executor.submit(download, u) for u in urls]
results = [f.result() for f in futures]
```

### Scenario 2: Call 3 different APIs — `fetch_profile()`, `fetch_orders()`, `send_notification()`

Use **`submit()`** — different functions can't use `map()`:

```python
# submit: different functions in one pool
f1 = executor.submit(fetch_profile, user_id)
f2 = executor.submit(fetch_orders, user_id)
f3 = executor.submit(send_notification, user_id)
profile, orders, notif = f1.result(), f2.result(), f3.result()

# map: CAN'T do this — map takes ONE function only
```

### Scenario 3: Calling a flaky API — some calls fail, handle each failure individually

Use **`submit()`** — per-task error isolation:

```python
# submit: handle each failure separately
futures = [executor.submit(fetch, url) for url in urls]
for f in futures:
    try:
        print(f.result())
    except Exception as e:
        print(f"Failed: {e}")  # other tasks keep going

# map: exception breaks the iteration
for result in executor.map(fetch, urls):
    print(result)  # if url[3] fails, you get the exception HERE
                   # and urls 4, 5, 6... are never printed
                   # even though they succeeded!
```

---

## 6. Parallel Merge Sort — A Real Algorithm

First: what is merge sort. Then: can we parallelize it?

### How Merge Sort Works

```
Original:     [38, 27, 43, 3, 9, 82, 10]

Split:        [38, 27, 43, 3]    [9, 82, 10]

Split again:  [38, 27] [43, 3]   [9, 82] [10]

Split again:  [38][27] [43][3]   [9][82] [10]

Merge:        [27, 38] [3, 43]   [9, 82] [10]

Merge:        [3, 27, 38, 43]    [9, 10, 82]

Merge:        [3, 9, 10, 27, 38, 43, 82]
```

**Key insight:** The two halves are sorted **independently**. That means they can be sorted on **different workers**!

### How We Divide Work Across 4 Workers

```
[38, 27, 43, 3, 9, 82, 10, 15, 44, 6, 71, 2]   (800,000 numbers)
                    |
              Split into 4 chunks
                    |
     +---------+---------+---------+---------+
     | Chunk 1 | Chunk 2 | Chunk 3 | Chunk 4 |
     |Worker 1 |Worker 2 |Worker 3 |Worker 4 |
     | sorts   | sorts   | sorts   | sorts   |
     +---------+---------+---------+---------+
         All 4 sort simultaneously (parallel!)
     +---------+---------+---------+---------+
     |Sorted 1 |Sorted 2 |Sorted 3 |Sorted 4 |
     +---------+---------+---------+---------+
                    |
           Merge (sequential — 1 thread)
                    |
     [2, 3, 6, 9, 10, 15, 27, 38, 43, 44, 71, 82]  (Fully sorted!)
```

### Sequential Merge Sort

```python
def merge_sort(arr):
    if len(arr) <= 1: return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]: result.append(left[i]); i += 1
        else: result.append(right[j]); j += 1
    return result + left[i:] + right[j:]

# Sequential: sort 4 chunks one by one
data = [random.randint(0, 1_000_000) for _ in range(800_000)]
chunks = [data[i::4] for i in range(4)]
sorted_chunks = [merge_sort(c) for c in chunks]
```

### Spot the Bug

> **Question:** Someone writes this. What's wrong?

```python
with ThreadPoolExecutor(4) as ex:
    ex.submit(merge_sort, chunks[0])
    ex.submit(merge_sort, chunks[1])
    ex.submit(merge_sort, chunks[2])
    ex.submit(merge_sort, chunks[3])
# Where are the results?
```

<details>
<summary>Answer</summary>

They forgot to capture the Futures! `submit()` returns a Future but they're not storing it. The sorted results are lost. Need: `futures = [ex.submit(merge_sort, c) for c in chunks]` then `[f.result() for f in futures]`.

Or even simpler — use `map()`: `sorted_chunks = list(ex.map(merge_sort, chunks))`

</details>

### The Correct ThreadPool Version (using `map()`)

> **Question:** We have 4 chunks and 4 workers. Same function (`merge_sort`) on each chunk. Should we use `map()` or `submit()`?

<details>
<summary>Answer</summary>

**`map()`** — same function, list of inputs. This is exactly what map is for.

</details>

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    sorted_chunks = list(executor.map(merge_sort, chunks))

# Merge all sorted chunks back together
result = sorted_chunks[0]
for c in sorted_chunks[1:]:
    result = merge(result, c)
```

### `submit()` vs `map()` Comparison

```python
# Using map() — simpler
with ThreadPoolExecutor(max_workers=4) as executor:
    sorted_chunks = list(executor.map(merge_sort, chunks))

# Using submit() — more explicit
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(merge_sort, c) for c in chunks]
    sorted_chunks = [f.result() for f in futures]
```

Same result. `map()` is cleaner here since it's one function on many inputs.

### GIL Blocks ThreadPool --> ProcessPool Fix

> **Question:** Sorting is pure computation (CPU-bound). Will ThreadPoolExecutor speed this up?

<details>
<summary>Answer</summary>

**No** — GIL! Only 1 thread runs Python at a time. Need ProcessPoolExecutor. Just change one word:

</details>

```python
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor(max_workers=4) as executor:
    sorted_chunks = list(executor.map(merge_sort, chunks))

# Same code! Just ThreadPoolExecutor -> ProcessPoolExecutor
# Sequential:  1.20s
# ThreadPool:  1.19s  (GIL blocks)
# ProcessPool: 0.42s  (2.9x faster!)
```

### Amdahl's Law — The Law of Diminishing Returns

**Speedup = 1 / (S + P/N)**

- S = sequential fraction (merge step)
- P = parallel fraction (sort step)
- N = workers

Sort = 90% of time (parallelizable). Merge = 10% (sequential, can't be split).

| Workers (N) | Calculation | Speedup | Efficiency |
|---|---|---|---|
| 1 | 1 / (0.1 + 0.9/1) | **1.0x** | baseline |
| 2 | 1 / (0.1 + 0.9/2) | **1.8x** | good — nearly 2x |
| 4 | 1 / (0.1 + 0.9/4) | **3.1x** | good — but not 4x |
| 8 | 1 / (0.1 + 0.9/8) | **4.7x** | diminishing — 8 workers, only 4.7x |
| 16 | 1 / (0.1 + 0.9/16) | **6.4x** | diminishing — 16 workers, only 6.4x |
| 100 | 1 / (0.1 + 0.9/100) | **9.2x** | almost at ceiling |
| inf | 1 / (0.1 + 0) | **10x** | THE CEILING — can never exceed this |

That 10% sequential part (merge) **caps you at 10x forever**, no matter how many workers you throw at it. Going from 4 to 100 workers only gains you 3x more speedup (3.1x --> 9.2x). The first few workers give the biggest bang.

**The lesson:** Before adding more workers, ask: *"Can I reduce the sequential portion?"* Making more of your code parallelizable gives bigger gains than adding more cores.

> **Question:** Your task is 50% sequential and 50% parallelizable. With infinite workers, what's the max speedup?

<details>
<summary>Answer</summary>

**2x** — `1/0.50 = 2`. Half your code can't be parallelized, so you can never be more than 2x faster. This is why reducing the sequential portion matters more than adding workers.

</details>

---

## 7. Race Condition — The Shared Data Problem

### Step 1: Add & Subtract Without Threads (Sequential)

Start simple. No threads. Just add and subtract the same number of times.

```python
balance = 0

def add(n):
    global balance
    for _ in range(n):
        balance += 1

def subtract(n):
    global balance
    for _ in range(n):
        balance -= 1

add(1_000_000)
subtract(1_000_000)
print(f"Balance: {balance}")  # ???
```

```
Sequential: One after the other

balance = 0 --> add(1M) --> subtract(1M) --> balance = 0
                balance=1,000,000           always correct
```

> **Question:** Add 1 million, subtract 1 million. What is the balance?

<details>
<summary>Answer</summary>

**0** — always, no matter how large the number. Sequential = predictable.

</details>

### Step 2: Same Thing, But With Threads

```
Threaded: Both run simultaneously on shared balance

              balance = 0
              /          \
 Thread 1: add(1M)    Thread 2: subtract(1M)
 balance += 1 x 1M    balance -= 1 x 1M
              \          /
            balance = ???
              not 0!
```

```python
import threading

balance = 0

def add(n):
    global balance
    for _ in range(n):
        balance += 1

def subtract(n):
    global balance
    for _ in range(n):
        balance -= 1

t1 = threading.Thread(target=add, args=(1_000_000,))
t2 = threading.Thread(target=subtract, args=(1_000_000,))
t1.start(); t2.start()
t1.join(); t2.join()

print(f"Expected: 0")
print(f"Actual:   {balance}")
```

> **Question:** Add 1 million, subtract 1 million. Expected: 0. What do you actually get?

<details>
<summary>Answer</summary>

**NOT 0!** A random wrong number, different each run. Something like 3847 or -12053. This is a **race condition**. Run it yourself. Run it 3 times. You'll get different wrong answers each time.

</details>

### Wait — Doesn't the GIL Prevent This?

**Common confusion:** "But the GIL only lets ONE thread run Python at a time! How can two threads corrupt data?"

**GIL prevents PARALLEL execution. It does NOT prevent CONTEXT SWITCHING.**

The OS can switch from Thread A to Thread B **in the middle** of `balance += 1`. The GIL just ensures only one runs at any instant — but "which one" changes constantly.

### Bytecode Explanation

`balance += 1` looks like 1 operation. But Python compiles it to multiple bytecodes:

```
  LOAD_GLOBAL   balance     <-- READ from memory
  LOAD_CONST    1
  BINARY_ADD                <-- ADD
  STORE_GLOBAL  balance     <-- WRITE back to memory

A context switch can happen BETWEEN any of these steps.
```

The interleaving that breaks things:

```
Step  Thread A (add)           Thread B (subtract)      balance
----- ------------------------ ------------------------ -------
 1    READ balance = 5                                     5
      ==== CONTEXT SWITCH ====
 2                               READ balance = 5          5
 3                               SUBTRACT 1, WRITE         4
      ==== CONTEXT SWITCH ====
 4    ADD 1, WRITE                                         6 !

Thread A still had the old value (5). Writes 6.
Thread B's subtraction (-> 4) was OVERWRITTEN. Lost.
```

> **Question:** True or False: "The GIL makes Python thread-safe."

<details>
<summary>Answer</summary>

**FALSE.** GIL prevents parallel execution but NOT context switching. A thread can be interrupted mid-operation. You still need locks for shared mutable data. This is one of the most common Python misconceptions. GIL != thread safety.

</details>

---

## 8. Critical Section — What to Protect

Before learning the fix, learn to IDENTIFY the problem.

A **critical section** = a piece of code that accesses shared data and MUST NOT be interrupted. If two threads run it simultaneously, data gets corrupted. Your job: identify the critical section, then protect ONLY that part.

### Example 1 (Easy): Where is the critical section?

```python
balance = 0

def deposit(amount):
    global balance
    balance += amount      # Line A
```

> **Question:** Which line is the critical section?

<details>
<summary>Answer</summary>

**Line A:** `balance += amount` — it reads and writes the shared variable `balance`. This is the critical section. Only the line that touches shared data needs protection. The `global` statement itself doesn't modify anything.

</details>

### Example 2 (Medium): Where is the critical section?

```python
inventory = {"biryani": 10}

def place_order(dish):
    if inventory[dish] > 0:    # Line A: check stock
        time.sleep(0.01)       # Line B: simulate processing
        inventory[dish] -= 1    # Line C: reduce stock
        return "Order placed"
    return "Out of stock"
```

> **Question:** Is it just Line C, or Lines A through C?

<details>
<summary>Answer</summary>

**Lines A through C together.** Thread 1 checks stock (10 > 0), Thread 2 checks stock (10 > 0), both proceed, both subtract — stock goes to 8 instead of 9. The CHECK and the UPDATE must be atomic. The "check-then-act" pattern is a classic race condition.

**What if you lock the ENTIRE function (A+B+C)?** It works — but Line B (`time.sleep(0.01)` / processing) runs while holding the lock. Other threads wait during that processing time for nothing. **Over-locking kills concurrency.** Lock only A+C (the shared data access). Let B run freely.

</details>

### Example 3 (Hard): Where is the critical section? What happens if you lock too much?

```python
users = {}

def register(username, email):
    if username not in users:     # Line A: check exists
        log(f"Registering {username}") # Line B: log (slow: writes to file)
        users[username] = email     # Line C: create user
        send_welcome(email)          # Line D: send email (slow: 200ms)
```

> **Question:** What should you lock?

<details>
<summary>Answer</summary>

**Lock only A+C** (check + write). B and D are slow I/O that don't touch shared data. Locking them means other threads wait 200ms+ for no reason.

**Lock the minimum.** If you lock A-D, every registration waits for the previous one's email send (200ms). With 100 users, that's 20 seconds of unnecessary waiting. Lock A+C only = milliseconds.

</details>

### Over-locking Consequences

```
Too few locks:                  Too many locks:
Race conditions, corrupted      Everything runs sequentially,
data, impossible bugs.          no concurrency benefit.

        Find the minimum locking that ensures correctness.
```

---

## 9. Mutex — Mutual Exclusion

Only ONE thread can hold the lock at a time. Others wait.

### The Bathroom Analogy

Bathroom has a lock. One person enters, locks. Others wait. Done? Unlock. Next person. **Mutex = that lock.** Only one thread in the critical section at a time.

### The Basic Way: `acquire()` and `release()`

```python
import threading

balance = 0
lock = threading.Lock()

def add(n):
    global balance
    for _ in range(n):
        lock.acquire()       # Lock — others wait
        balance += 1
        lock.release()       # Unlock — next thread can enter

def subtract(n):
    global balance
    for _ in range(n):
        lock.acquire()
        balance -= 1
        lock.release()
```

> **Question:** What happens if a thread calls `lock.acquire()` but never calls `lock.release()`?

<details>
<summary>Answer</summary>

Every other thread trying to acquire that lock waits FOREVER. The lock is never freed. The program hangs. This is why `release()` is critical.

</details>

### Spot the Exception Problem

> **Question:** What if an exception happens between `acquire()` and `release()`?

<details>
<summary>Answer</summary>

The lock is NEVER released. Every other thread waits forever. Deadlock! We need a way to guarantee release even on errors. The fix: `with lock:` — auto-releases even on exceptions.

</details>

### The Better Way: `with lock:` Context Manager

```python
import threading

balance = 0
lock = threading.Lock()

def add(n):
    global balance
    for _ in range(n):
        with lock:          # acquire + guaranteed release
            balance += 1

def subtract(n):
    global balance
    for _ in range(n):
        with lock:
            balance -= 1

t1 = threading.Thread(target=add, args=(1_000_000,))
t2 = threading.Thread(target=subtract, args=(1_000_000,))
t1.start(); t2.start()
t1.join(); t2.join()

print(f"Expected: 0")
print(f"Actual:   {balance}")  # Exactly 0! Every time!
```

### All `with`-Statement Uses — Same Pattern

> **Question:** `with lock:` — what pattern is this? Where have you seen it?

<details>
<summary>Answer</summary>

**Context manager** — same as `with open("file")` and `with ThreadPoolExecutor()`. Auto-releases the lock even if an exception occurs.

Every `with` you've used is the same pattern:

- `with open("file") as f:` — auto-closes file
- `with ThreadPoolExecutor() as ex:` — auto-shuts down pool
- `with lock:` — auto-releases lock

All guarantee cleanup even on exceptions.

</details>

---

## 10. Mutex Is Not Just a Python Thing

**Mutex is a universal concept** used everywhere concurrent access exists:

- **Databases:** Row-level locks, table locks, `SELECT ... FOR UPDATE` — all mutexes
- **Operating Systems:** File locks, kernel mutexes for device access
- **Java:** `synchronized` keyword is a mutex
- **Go:** `sync.Mutex`
- **Redis:** Distributed locks (`SETNX`) — mutex across multiple servers

The concept is the same everywhere: **only one can enter at a time**. The syntax differs.

**Summary:**

- **Mutex** (Mutual Exclusion) = lock allowing only ONE thread/process in a critical section
- **Critical section** = code that reads+writes shared data, must not be interrupted
- Python: `lock = threading.Lock()` --> `with lock:`
- GIL != thread safety. GIL prevents parallel execution but NOT context switching
- Lock the **minimum** necessary — over-locking kills concurrency
- Mutex is universal: databases, OS, Java, Go, Redis all use the same concept

---

## 11. Deadlock — When Locks Go Wrong

Locks fix race conditions. But what if two threads each wait for the other's lock?

### Deadlock — Circular Wait

```
+--------------------+          +--------------------+
|     Thread A       |          |     Thread B       |
|  holds Lock 1      |   --->   |  holds Lock 2      |
|  needs Lock 2      |   <---   |  needs Lock 1      |
+--------------------+          +--------------------+

A waits for B. B waits for A. Neither moves. Forever.
```

### The Narrow Hallway Analogy

Two people meet in a narrow hallway. Each steps to the same side to let the other pass. They step again — same side. Again. Again. Both stuck, endlessly mirroring each other.

### BookMyShow Example — Two Users, Same Seats

```
Cinema — Row A

 [1] [2] [3*] [4] [5] [6*] [7] [8]

 User 1 wants: 3 then 6
 User 2 wants: 6 then 3
```

```
User 1: locks Seat 3    wants Seat 6 -> WAITS (User 2 has it)
User 2: locks Seat 6    wants Seat 3 -> WAITS (User 1 has it)

DEADLOCK! Different locking order = circular wait.
```

```python
import threading, time

lock_A = threading.Lock()
lock_B = threading.Lock()

def user1_books():
    with lock_A:                # Gets lock A
        print("User 1: got seat A")
        time.sleep(0.1)          # Tiny delay
        with lock_B:            # Wants lock B -> WAITS (User 2 has it)
            print("User 1: got seat B")

def user2_books():
    with lock_B:                # Gets lock B
        print("User 2: got seat B")
        time.sleep(0.1)          # Tiny delay
        with lock_A:            # Wants lock A -> WAITS (User 1 has it)
            print("User 2: got seat A")

t1 = threading.Thread(target=user1_books)
t2 = threading.Thread(target=user2_books)
t1.start(); t2.start()
# HANGS FOREVER. Both threads waiting for each other.
```

> **Question:** Why does this deadlock?

<details>
<summary>Answer</summary>

User 1 locks A first, then wants B. User 2 locks B first, then wants A. Each holds what the other needs. Neither can proceed. The root cause: **different lock ordering**. If both always locked in the SAME order, no deadlock.

</details>

### Solution 1: Deadlock Prevention — Consistent Lock Ordering

```python
import threading, time

locks = {"A": threading.Lock(), "B": threading.Lock()}

def book_seats(user, seat1, seat2):
    # ALWAYS lock in sorted order — prevents deadlock!
    first, second = sorted([seat1, seat2])

    with locks[first]:
        print(f"{user}: got seat {first}")
        time.sleep(0.1)
        with locks[second]:
            print(f"{user}: got seat {second}")
    print(f"{user}: booking complete!")

# Both users lock A first, then B — no deadlock!
t1 = threading.Thread(target=book_seats, args=("User 1", "A", "B"))
t2 = threading.Thread(target=book_seats, args=("User 2", "B", "A"))
t1.start(); t2.start()
t1.join(); t2.join()
print("Done! No deadlock.")
```

**The fix: sort before locking.**

- User 1 wants A, B --> sorted: A, B --> locks A first, then B.
- User 2 wants B, A --> sorted: A, B --> locks A first, then B.

**Same order = no circular wait = no deadlock.** This works for any number of resources.

### Solution 2: Deadlock Recovery — Timeouts

Can't always prevent deadlocks? **Detect and recover.**

`lock.acquire(timeout=5)` — try for 5 seconds. If can't get the lock, give up and retry. The thread releases what it holds, waits a random time, tries again.

```python
import threading, time, random

lock_A = threading.Lock()
lock_B = threading.Lock()

def book_with_retry(user, first_lock, second_lock):
    while True:
        first_lock.acquire()
        if second_lock.acquire(timeout=0.1):  # Try for 0.1s
            print(f"{user}: got both locks!")
            second_lock.release()
            first_lock.release()
            return
        else:
            first_lock.release()              # Give up, release, retry
            time.sleep(random.uniform(0, 0.1))  # Random backoff
            print(f"{user}: couldn't get both, retrying...")
```

### Solution 3: Deadlock Ignorance — The Ostrich Algorithm

**Most operating systems (Linux, Windows, macOS) simply IGNORE deadlocks.**

Why? Deadlock detection and prevention have overhead. If deadlocks are rare (which they are in practice), the cost of preventing them exceeds the cost of occasionally rebooting. This is called the **"Ostrich Algorithm"** — stick your head in the sand and pretend it doesn't exist.

### Repercussions — Have You Seen This?

**Yes, you've experienced this.** Ever had your computer freeze and nothing responds? That could be a deadlock. The "fix" = force-restart.

- **Your phone app hanging** — you kill it from task manager. OS doesn't fix it, YOU do.
- **Database locks timing out** — PostgreSQL uses timeouts (recovery), not prevention. You see `ERROR: deadlock detected` in logs.
- **Print spooler stuck** — Windows print service deadlocks are so common that "restart print spooler" is a meme.

The OS could detect and break deadlocks automatically, but the overhead of constantly checking EVERY lock in EVERY process would slow down the entire system. Deadlocks are rare enough that rebooting is cheaper.

### Three Strategies — Summary

| Strategy | How | Used by |
|---|---|---|
| **Prevention** | Consistent lock ordering (sorted). Eliminate circular wait. | Application code, databases |
| **Recovery** | Timeouts + retry with backoff. Detect and break the cycle. | Databases (lock timeout), distributed systems |
| **Ignorance** | Do nothing. Reboot if stuck. Rare enough to not be worth the overhead. | Linux, Windows, macOS |

### Homework Challenge

> **Question:** You're building a money transfer system. `transfer(from_account, to_account, amount)` needs to lock both accounts.
>
> Thread 1: `transfer(Alice, Bob, 100)` — locks Alice, then Bob
> Thread 2: `transfer(Bob, Alice, 50)` — locks Bob, then Alice
>
> **How would you prevent deadlock here?** Come with your answer next class.

**Interview ready:**

- **Deadlock** = two+ threads each waiting for a lock the other holds. Both wait forever.
- **Prevention:** always acquire locks in a consistent order (sort by ID/name)
- **Recovery:** use `lock.acquire(timeout=N)`, release and retry with random backoff
- **Ignorance:** most OSes use the "ostrich algorithm" — deadlocks are rare, rebooting is cheaper than prevention overhead
- **4 conditions for deadlock:** mutual exclusion, hold-and-wait, no preemption, circular wait. Break ANY one to prevent deadlock.

---

## 12. What's Next

| Today | Next Class | After That |
|---|---|---|
| Executors, Mutex, Deadlock | Semaphores & more patterns | Async I/O (asyncio) |
| Mutex = 1 thread at a time | Semaphore = N threads at a time | Single-threaded concurrency |

**Next: Semaphores.** Mutex allows 1 thread. What if you want exactly 3 (like 3 database connections)? That's a **semaphore**. Also: the homework answer for the transfer deadlock.

---

## 13. Resources

- [Real Python — concurrent.futures](https://realpython.com/python-concurrency/) — submit(), map(), as_completed() explained
- [Real Python — Threading](https://realpython.com/intro-to-python-threading/) — Locks, race conditions, thread safety
- [Python docs — threading.Lock](https://docs.python.org/3/library/threading.html#lock-objects) — Official Lock/Mutex documentation
- [W3Schools — Merge Sort Visualization](https://www.w3schools.com/dsa/dsa_algo_mergesort.php) — Interactive sorting algorithm visualizer
- [Concurrency Visualized (YouTube Playlist)](https://www.youtube.com/watch?v=2PjlaUnrAMQ&list=PLsdq-3Z1EPT3VjDhjMb5yBsgn0wn2-fjp) — Animated deadlock and concurrency explanations
- [Compiler Explorer (godbolt.org)](https://godbolt.org/) — See how any language compiles to instructions
