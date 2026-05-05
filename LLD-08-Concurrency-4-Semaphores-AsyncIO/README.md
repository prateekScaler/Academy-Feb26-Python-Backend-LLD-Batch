
# LLD-08: Concurrency-4 — Semaphores & Async I/O

> Last class: mutex (1 at a time) and deadlocks. Today: **semaphores (N at a time), producer-consumer signalling, and async/await (no threads at all).**

---

## Recap — Last Class

> **Question:** What is a mutex?

<details>
<summary>Answer</summary>

A lock (`threading.Lock()`) that allows only **ONE** thread in the critical section at a time. Use `with lock:` to acquire/release safely. Mutex = mutual exclusion. Today we learn semaphore = "allow N at a time."

</details>

> **Question:** Homework — `transfer(Alice, Bob, 100)` and `transfer(Bob, Alice, 50)` run concurrently. How do you prevent deadlock?

<details>
<summary>Answer</summary>

Sort accounts by ID before locking. Both transfers lock the **lower ID first** — same order, no circular wait. Same pattern as the BookMyShow seat booking fix.

</details>

> **Question:** True or False — "The GIL makes Python thread-safe."

<details>
<summary>Answer</summary>

**FALSE.** The GIL prevents parallel execution but NOT context switching. A thread can be interrupted mid-operation. You still need locks. GIL ≠ thread safety.

</details>

---

## Semaphore — The Problem

### Toll Booth Analogy

A highway has **3 toll booths**. 6 cars arrive at once.

**Without any lock:** all 6 cars rush in. More cars than booths — violations!

```python
# 00d_toll_no_lock.py — Step 1: No protection
booths_in_use = 0
MAX_BOOTHS = 3

def pay_toll(car):
    global booths_in_use, violations
    booths_in_use += 1
    if booths_in_use > MAX_BOOTHS:
        print(f"  Car {car}: VIOLATION! {booths_in_use} cars in {MAX_BOOTHS} booths!")
    time.sleep(1)
    booths_in_use -= 1
```

Output: multiple violations! We need to control access.

### Attempt 1: Mutex

Lock the whole toll plaza — only 1 car at a time.

```python
# 00e_toll_with_mutex.py — Step 2: Mutex (too strict)
lock = threading.Lock()

def pay_toll(car):
    global booths_in_use
    with lock:                          # Only 1 car at a time
        booths_in_use += 1
        print(f"  Car {car}: booth {booths_in_use} of {MAX_BOOTHS}")
        time.sleep(1)
        booths_in_use -= 1
```

Output: always "booth 1 of 3". **2 booths sit empty!** Mutex is too strict — we have 3 booths but only allow 1 car.

> **Question:** Mutex allows 1 at a time. We have 3 booths. What do we need?

<details>
<summary>Answer</summary>

Something that allows **N at a time** — a **Semaphore(3)**.

</details>

### Solution: Semaphore

```python
# 00f_toll_with_semaphore.py — Step 3: Semaphore (just right)
sem = threading.Semaphore(MAX_BOOTHS)   # Allow 3 at a time
lock = threading.Lock()                  # Just for the counter

def pay_toll(car):
    global booths_in_use
    with sem:                           # Up to 3 at a time
        with lock: booths_in_use += 1
        print(f"  Car {car}: booth {booths_in_use} of {MAX_BOOTHS}")
        time.sleep(1)
        with lock: booths_in_use -= 1
```

Output: 3 cars at once, 2 batches, all booths used. **6 seconds → 2 seconds!**

### How Semaphore Works

| | Mutex (Lock) | Semaphore |
|---|---|---|
| **How many?** | 1 at a time | **N at a time** |
| **Analogy** | Bathroom with 1 stall | Parking lot with N spots |
| **Internal** | locked / unlocked | Counter (0 to N) |

- `Semaphore(N)` — creates a counter starting at N
- `acquire()` — decrements counter. If counter = 0, **blocks** (waits)
- `release()` — increments counter. Wakes up one waiting thread

> **Question:** 10 threads, `Semaphore(3)`, each takes 1 second. Total time?

<details>
<summary>Answer</summary>

**~4 seconds.** 3 run at a time: `ceil(10/3) = 4` batches × 1s each.

</details>

### Use Cases

- **Rate Limiting** — Max 5 API calls at once. `Semaphore(5)`
- **Connection Pooling** — Max 10 DB connections. `Semaphore(10)`
- **Resource Throttling** — Max 3 file downloads. `Semaphore(3)`

### BoundedSemaphore

Use `BoundedSemaphore(N)` instead of `Semaphore(N)` to catch bugs: raises an error if you `release()` more than you `acquire()`. Regular `Semaphore` silently lets the counter exceed N.

---

## Producer-Consumer — Semaphore as a Signalling Tool

A semaphore isn't just "N at a time." It's a **signalling mechanism**.

### The Problem

Producer creates items, puts in buffer. Consumer takes items from buffer. Buffer has a max size.

**Rules:**
- Producer must **WAIT** when buffer is full
- Consumer must **WAIT** when buffer is empty
- One thread must **SIGNAL** the other when state changes

### Attempt 1: No Protection

```python
# 00g_producer_no_protection.py
buffer = []
MAX_SIZE = 3

def producer():
    for i in range(6):
        buffer.append(f"item-{i}")       # No check!
        time.sleep(0.2)

def consumer():
    for _ in range(6):
        time.sleep(0.5)                   # Slower than producer
        item = buffer.pop(0)              # Crashes if empty!
```

Buffer overflows past MAX_SIZE. Consumer may crash on empty buffer.

### Attempt 2: Mutex

```python
# 00h_producer_with_mutex.py
lock = threading.Lock()

def producer():
    for i in range(6):
        with lock:
            if len(buffer) >= MAX_SIZE:
                print("SKIPPED — buffer full! Can't wait with mutex.")
            else:
                buffer.append(f"item-{i}")
```

> **Question:** Can a mutex make the producer WAIT until space is free?

<details>
<summary>Answer</summary>

**No!** A mutex is binary (locked/unlocked). It can't express "wait until a condition changes." If you hold the lock and busy-wait, the consumer can never acquire it → **deadlock**. If you skip, you lose items. Mutex protects data but **can't signal** between threads.

</details>

### Solution: Semaphore Signalling

Two semaphores signal between producer and consumer:

```python
# 00i_producer_with_semaphore.py
space_sem = threading.Semaphore(MAX_SIZE)  # 3 spaces free
items_sem = threading.Semaphore(0)         # 0 items ready

def producer():
    for i in range(6):
        space_sem.acquire()     # WAIT if buffer full
        buffer.append(f"item-{i}")
        items_sem.release()     # SIGNAL: "item ready!"

def consumer():
    for _ in range(6):
        items_sem.acquire()     # WAIT if buffer empty
        item = buffer.pop(0)
        space_sem.release()     # SIGNAL: "space free!"
```

**Key insight:** `release()` doesn't just "unlock" — it **signals** another thread. Producer's `items_sem.release()` wakes up a blocked consumer. Consumer's `space_sem.release()` wakes up a blocked producer.

> **Interview Ready**
>
> - Semaphore has two uses: **(1)** limit concurrency (N at a time), **(2)** signal between threads
> - Producer-Consumer uses TWO semaphores: `space_sem` (producer waits) + `items_sem` (consumer waits)
> - `acquire()` = wait, `release()` = signal
> - Mutex can't signal — it only protects. Semaphore can both protect AND signal.

---

## What If We Didn't Need Threads At All?

### The Cost of Threads

- Each thread uses ~1-8MB stack memory
- Context switching costs CPU time
- GIL limits Python threads to 1 at a time anyway
- Shared state needs locks — complexity

For I/O-bound work, threads spend **95% of their time sleeping** (waiting for network).

### The Super Waiter Analogy

**Thread pool** = 5 waiters, each serves one table at a time.

**Async** = **1 super waiter**. Takes order from table 1. While kitchen cooks, takes order from table 2. While both cook, takes order from table 3. Comes back to table 1 when food is ready.

ONE person. ZERO idle time. ZERO context switching. No locks needed.

---

## Async I/O — Building the Syntax Step by Step

### Step 1: A Regular Function

```python
def fetch(url):
    print(f"Fetching {url}...")
    time.sleep(1)            # Blocks everything
    return f"{url}: 200 OK"
```

### Step 2: Make It a Coroutine

```python
async def fetch(url):        # async def = coroutine
    print(f"Fetching {url}...")
    time.sleep(1)            # Still blocks! Wrong sleep.
    return f"{url}: 200 OK"
```

`async def` declares a coroutine — a function that CAN pause. But we haven't told it WHERE to pause yet.

### Step 3: Use `await` for Non-Blocking Wait

```python
async def fetch(url):
    print(f"Fetching {url}...")
    await asyncio.sleep(1)   # Yields to event loop!
    return f"{url}: 200 OK"
```

`await` = "I'm waiting for I/O. Event loop, go run other tasks. Come back when done."

### Step 4: Run It

```python
async def main():
    result = await fetch("a.com")
    print(result)

asyncio.run(main())          # Starts the event loop
```

### Step 5: Run Concurrently with `gather()`

```python
async def main():
    results = await asyncio.gather(
        fetch("a.com"),
        fetch("b.com"),
        fetch("c.com"),
    )
    # All 3 run concurrently — 1 second total, not 3!
```

### Key Rules

| Concept | What It Does |
|---|---|
| `async def` | Declares a coroutine (can pause) |
| `await` | Non-blocking pause — event loop runs other tasks |
| `asyncio.gather()` | Run multiple coroutines concurrently |
| `asyncio.run()` | Start the event loop (call once) |

### Common Mistakes

> **Question:** What's the difference between `time.sleep(1)` and `await asyncio.sleep(1)`?

<details>
<summary>Answer</summary>

`time.sleep(1)` **BLOCKS the entire event loop** — nothing else runs. `await asyncio.sleep(1)` **yields to the event loop** — other tasks run during the wait. ALWAYS use `asyncio.sleep` in async code.

</details>

> **Question:** What happens if you forget `await`?

<details>
<summary>Answer</summary>

```python
result = fetch("a.com")  # Missing await!
print(result)             # <coroutine object fetch at 0x...>
```

Without `await`, the function doesn't execute — it returns a coroutine object. Always `await` coroutines.

</details>

### Blocking vs Async Libraries

**Use threading** when your library is **blocking** — it doesn't know about async and will freeze the event loop:
- `requests` → blocks while waiting for HTTP response
- `psycopg2` → blocks while waiting for DB query
- `time.sleep()` → blocks the entire thread

**Use async** when your library **supports it** — it yields to the event loop during I/O:
- `aiohttp` → async HTTP client (replaces `requests`)
- `asyncpg` → async PostgreSQL (replaces `psycopg2`)
- `asyncio.sleep()` → non-blocking sleep

You can't mix them! Using `requests` inside `async def` blocks the entire event loop. Use `aiohttp` instead.

> **Interview Ready**
>
> - `async def` = coroutine. `await` = non-blocking pause.
> - `asyncio.gather(*coros)` = run concurrently, wait for all
> - `asyncio.run(main())` = start the event loop
> - Single-threaded: no GIL issues, no locks needed
> - NEVER use blocking calls (`time.sleep`, `requests.get`) inside async
> - Use async-compatible libraries: `aiohttp`, `asyncpg`, `asyncio.sleep`

---

## Threading vs Async

| | Threading | Async (asyncio) |
|---|---|---|
| **Model** | Multiple OS threads, OS schedules | Single thread, event loop schedules |
| **GIL impact** | Affected (released during I/O) | Not affected (single thread!) |
| **Shared state** | Need locks (mutex, semaphore) | No locks needed (single thread) |
| **Overhead** | Thread creation, context switching, memory | Very low (coroutines are cheap) |
| **Libraries** | `requests`, `psycopg2` | `aiohttp`, `asyncpg`, FastAPI |
| **Best for** | I/O-bound with blocking libraries | I/O-bound with async libraries, high concurrency |

---

## Which Tool for Which Job?

After 4 concurrency classes, here's the complete decision guide:

```
CPU-bound (math, image resize)  →  ProcessPoolExecutor
                                    (bypasses GIL, true parallelism)

I/O-bound + blocking libs       →  ThreadPoolExecutor
  (requests, psycopg2)              (GIL released during I/O)

I/O-bound + async libs          →  asyncio
  (aiohttp, asyncpg, FastAPI)       (single thread, no locks, lightest)

Limit concurrency               →  Semaphore(N)
  (max N connections at once)       (works with threads AND async)

Mutual exclusion                →  Lock (mutex)
  (only 1 thread modifies data)     (Semaphore(1) is equivalent)
```

> **Question:** FastAPI app calling 3 external APIs per request. Which approach?

<details>
<summary>Answer</summary>

`asyncio` with `aiohttp` — FastAPI is built on async. Use `asyncio.gather()` for all 3 APIs concurrently. No threads needed.

</details>

> **Question:** Resize 1000 images. Which approach?

<details>
<summary>Answer</summary>

**ProcessPoolExecutor** — image resize is CPU-bound. Threads don't help (GIL). Async doesn't help (no I/O wait). Processes bypass GIL.

</details>

---

## Code Files

| File | What It Demonstrates |
|---|---|
| `00_race_condition_3_acts.py` | Plain int vs @property vs Lock — why races happen |
| `00d_toll_no_lock.py` | Toll booth: no protection → violations |
| `00e_toll_with_mutex.py` | Toll booth: mutex → only 1 booth used |
| `00f_toll_with_semaphore.py` | Toll booth: semaphore → all 3 booths used |
| `00g_producer_no_protection.py` | Producer-consumer: buffer overflow |
| `00h_producer_with_mutex.py` | Producer-consumer: mutex can't signal |
| `00i_producer_with_semaphore.py` | Producer-consumer: semaphore signalling |
| `01_mutex_vs_semaphore.py` | Side-by-side mutex vs semaphore |
| `02_semaphore_parking_lot.py` | Parking lot analogy with semaphore |
| `03_semaphore_rate_limiter.py` | Rate limiting API calls |
| `04_semaphore_with_executor.py` | Semaphore + ThreadPoolExecutor |
| `05_bounded_semaphore.py` | BoundedSemaphore catches over-release |
| `06_async_basics.py` | async/await fundamentals |
| `07_async_gather.py` | asyncio.gather() for concurrency |
| `08_async_vs_threading.py` | Threading vs async comparison |
| `09_async_common_mistakes.py` | time.sleep vs asyncio.sleep, missing await |
| `10_async_real_world.py` | Real-world async patterns |
| `11_which_tool.py` | Decision guide: processes vs threads vs async |

---

## Concurrency Module Complete!

What you've learned across 4 classes:

- **Processes & Threads** — OS fundamentals, context switching, concurrency vs parallelism
- **GIL** — why Python threads can't truly parallelize CPU work
- **Executors** — ThreadPoolExecutor, ProcessPoolExecutor, submit(), map()
- **Mutex** — Lock, critical sections, deadlock prevention
- **Semaphore** — controlling concurrency (N at a time) + signalling (producer-consumer)
- **Async I/O** — single-threaded concurrency with async/await

**Next: Python Advanced Concepts** — typing, generics, collections, lambda functions, exception handling.

---

## Resources

- [Real Python — asyncio](https://realpython.com/async-io-python/) — Comprehensive async/await guide
- [Python docs — asyncio](https://docs.python.org/3/library/asyncio.html) — Official documentation
- [FastAPI — async first](https://fastapi.tiangolo.com/async/) — Modern Python web framework built on async
