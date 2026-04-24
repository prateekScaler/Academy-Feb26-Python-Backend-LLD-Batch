
# LLD-05: Concurrency-1 — Processes, Threads, and the GIL

> OOP taught you how to **structure** code. Concurrency teaches you how to make it **fast.**

---

## Quick Recap Quiz

Before we dive into a completely new topic, let's make sure OOP-3 is solid. Try to answer without looking back.

**Q1:** What's the difference between `@staticmethod` and `@classmethod`?

<details>
<summary>Answer</summary>

`@staticmethod` gets **no automatic first argument** — no `self`, no `cls`. It's just a regular function that lives inside a class for organizational purposes. `@classmethod` gets `cls` (the class itself) as the first argument, so it can access class-level data and — most importantly — create instances using `cls()` instead of hardcoding the class name (which matters for inheritance).

</details>

**Q2:** What does ABC enforce?

<details>
<summary>Answer</summary>

ABC (Abstract Base Class) enforces a **contract**: any child class MUST implement all `@abstractmethod` methods. If a child forgets to implement even one abstract method, Python raises `TypeError` at **object creation time** — not later when the method is called. This catches bugs early, during development instead of in production.

</details>

**Q3:** Can you instantiate an ABC directly?

<details>
<summary>Answer</summary>

No. If a class inherits from `ABC` and has at least one `@abstractmethod`, you **cannot** create an instance of it directly. `PaymentGateway()` would raise `TypeError: Can't instantiate abstract class PaymentGateway with abstract methods charge, refund`. You must create a concrete child class that implements all abstract methods.

</details>

---

## The Restaurant That Explains Everything

No code. No jargon. Just a restaurant with waiters and customers.

### Act 1: The Problem — Sequential

**1 waiter, 5 tables. The waiter is DUMB — he STANDS at the kitchen waiting for each dish.**

Customer A orders --> waiter goes to kitchen --> **stands there 10 min** --> brings food --> THEN goes to Customer B --> stands 10 min again...

5 customers x 10 min = **50 minutes.** Customer E waits 40 min just to ORDER.

```
Waiter: [A: take order][A: wait 10m][A: serve]  [B: take order][B: wait 10m][B: serve]  ...
                        ^^^^^^^^^^                              ^^^^^^^^^^
                        DOING NOTHING                           DOING NOTHING
Total: 50 minutes. Waiter is idle 80% of the time.
```

### Act 2: Concurrency — 1 Smart Waiter

**Same 1 waiter, but SMART.** He doesn't stand at the kitchen waiting. While the kitchen prepares A's food, he takes B's order. While B's food cooks, he takes C's order...

He **SWITCHES** between customers during their wait times. Still 1 waiter, but he's never idle.

```
Waiter:  [A: order][B: order][C: order][D: order][E: order][A: serve][B: serve]...
Kitchen:           [A cooking...][B cooking...][C cooking...]
                    (happening in background while waiter takes other orders)
Total: ~14 minutes. Same 1 waiter. Just smarter scheduling.
```

**This is CONCURRENCY.** One worker, multiple tasks, switching between them during idle time.
The waiter switching from Customer A to Customer B while waiting = **context switching.**

> **Question:** Is the smart waiter doing two things at the SAME instant?

<details>
<summary>Answer</summary>

**No.** At any single moment, he's with ONE customer. He just switches between them during their wait times. It LOOKS simultaneous but isn't. **Concurrency is not doing things at the same time.** It's MANAGING multiple tasks by switching between them. Like juggling — you only hold one ball at a time, but you keep 5 in the air.

</details>

### Act 3: Context Switching — Is It Free?

Every time the waiter switches, he needs to: **remember where he left off** with the previous customer, **walk to the new table**, **recall their order status.**

This takes a few seconds each time. It's not free. If the waiter switches too often (every 2 seconds), he spends MORE time walking between tables than actually serving.

> **Question:** Is context switching always good?

<details>
<summary>Answer</summary>

**It depends.** Good when customers are WAITING (kitchen is cooking). Bad when they need continuous attention (explaining the menu). Switching during idle time = efficient. Switching during active work = overhead. This maps directly to computers: switching during I/O wait = good. Switching during CPU computation = wasted overhead. We'll formalize this as I/O-bound vs CPU-bound later.

</details>

### Act 4: Parallelism — Multiple Waiters

**Now hire 5 waiters.** Each waiter serves their own table. All 5 customers are being served **at the exact same time.** Not switching, not juggling — genuinely simultaneous.

```
Waiter 1: [A: order][A: serve]
Waiter 2: [B: order][B: serve]      All happening
Waiter 3: [C: order][C: serve]      AT THE SAME TIME
Waiter 4: [D: order][D: serve]
Waiter 5: [E: order][E: serve]
Total: ~10 minutes. True parallel execution.
```

**This is PARALLELISM.** Multiple workers, genuinely simultaneous. Not taking turns — truly at the same instant.

> **Question:** What's the difference between the smart waiter (concurrency) and 5 waiters (parallelism)?

<details>
<summary>Answer</summary>

**Concurrency** = 1 waiter juggling tasks (switching during idle time). **Parallelism** = 5 waiters working simultaneously. Concurrency is about structure. Parallelism is about execution. A single-core CPU is the smart waiter — it can be concurrent but not parallel. A multi-core CPU is 5 waiters — it can be both.

</details>

### Act 5: Connecting to Your Computer

| Restaurant | Computer |
|---|---|
| Dumb waiter (sequential) | Single-threaded program — does one thing, waits, does next |
| Smart waiter (concurrent) | **1 CPU core with threads** — switches between tasks during wait |
| Waiter switching tables | **Context switching** — OS saves/restores task state |
| 5 waiters (parallel) | **Multiple CPU cores** — truly simultaneous execution |
| Kitchen cooking in background | **I/O operation** — API call, DB query, file read |
| Waiter explaining menu (active) | **CPU computation** — math, resize, compress |

---

## What is a Process?

A **process** is a running program. This is an OS concept — no Python yet.

When you double-click Chrome, the OS creates a **process**. Open VS Code? Another process. Every running program is a process.

### See It on YOUR Machine

- **macOS:** Open **Activity Monitor** (Cmd + Space --> "Activity Monitor"). Every row = a process.
- **Windows:** Open **Task Manager** (Ctrl + Shift + Esc) --> "Details" tab.
- **Linux:** Run `htop` or `ps aux`.

Right now, your machine runs **hundreds** of processes — browser, IDE, Spotify, system services.

### What a Process Contains

```
┌─────────────────────────────────────────────────┐
│                 A Single Process                 │
├────────────┬────────────┬──────────┬────────────┤
│    Code    │    Heap    │  Stack   │ OS Resources│
│ (program   │ (variables,│ (function│ (file       │
│ instructions│  objects)  │  calls)  │  handles,   │
│            │            │          │  sockets)   │
└────────────┴────────────┴──────────┴────────────┘
Each process has its OWN copy of ALL of these.
Process A can't see Process B's memory.
```

### Chrome Tabs Example

> **Question:** Chrome has 20 tabs open. How many processes?

<details>
<summary>Answer</summary>

**~20+.** Chrome runs each tab as a separate process. Check Activity Monitor! One tab crashing doesn't kill the others. Chrome is a real-world example of multiprocessing — each tab is isolated with its own memory and its own crash boundary.

</details>

> **Question:** Process A sets `x = 100`. Can Process B read that value?

<details>
<summary>Answer</summary>

**No.** Each process has its own memory. B has its own `x`, completely separate. Processes are **isolated**. To communicate, they need special OS tools (pipes, queues, shared memory).

</details>

---

## OS Internals: PCB and TCB

The OS keeps a "profile card" for every process and every thread.

### PCB — Process Control Block

The OS keeps one for EVERY process:

```
PCB holds:
- PID (process ID)
- Memory mappings (page table)
- Open files
- Signal handlers
- User/group IDs
- Child processes
```

### TCB — Thread Control Block

The OS keeps one for EVERY thread:

```
TCB holds:
- TID (thread ID)
- Register state (snapshot)
- Stack pointer
- Program counter
- Pointer back to parent PCB
```

**Why context switching between threads is FASTER than between processes:**
- **Thread switch (same process):** swap the TCB only — registers, stack pointer. Memory mappings stay the same. Quick.
- **Process switch:** swap the entire PCB — including flushing and reloading memory mappings (TLB flush). **Expensive.**

### Memory Layout — Two Processes Side by Side

```
PROCESS A                        PROCESS B
┌─────────────────────┐          ┌─────────────────────┐
│  Code segment        │          │  Code segment        │
│  (read only)         │          │                      │
├─────────────────────┤          ├─────────────────────┤
│  Heap                │          │  Heap                │
│  (shared by all      │          │                      │
│   threads in A)      │          │                      │
├─────────────────────┤          ├─────────────────────┤
│  Stack — Thread 1    │          │  Stack — Thread 1    │
├─────────────────────┤          ├─────────────────────┤
│  Stack — Thread 2    │          │  Stack — Thread 2    │
├─────────────────────┤          └─────────────────────┘
│  Stack — Thread 3    │
└─────────────────────┘

Process A and B CANNOT touch each other's memory.
But threads within A SHARE the heap — fast but dangerous.
```

### Resource Ownership — What's Shared, What's Separate?

| Resource | Process | Thread |
|---|---|---|
| **Memory space** | Own, isolated | Shared with all threads in process |
| **Stack** | Own | Own (each thread gets its own) |
| **Heap** | Own | Shared |
| **Code segment** | Own | Shared |
| **File descriptors** | Own | Shared |
| **PID** | Own | Shares parent's PID (has own TID) |
| **CPU registers** | Own snapshot | Own snapshot |

**The only things a thread owns exclusively:** its stack and its register state. Everything else is shared with the process. This is why threads are "lightweight" — creating one doesn't duplicate memory.

> **Question:** A thread in Process A crashes (segfault). What happens?

<details>
<summary>Answer</summary>

**The entire Process A dies — ALL threads in A die.** But Process B is completely unaffected (isolated memory). Threads share fate within a process. Processes are isolated. This is why Chrome runs tabs as separate processes — one bad tab can't crash others.

</details>

---

## What is a Thread?

You'll hear "a lightweight process." That's misleading. Here's what it actually is.

### The Misleading Definition

Textbooks say: *"A thread is a lightweight process."*

This is confusing because it implies a thread IS a process, just smaller. It's not. A thread is a **unit of execution WITHIN a process.** A process can have many threads.

### The House Analogy

- **Process** = a house. Own kitchen, bathroom, electricity. Completely independent.
- **Threads** = people in the house. Share the kitchen and bathroom (shared memory), each has their own bedroom (own stack).

New process = build a new house (expensive).
New thread = move a person into existing house (cheap).

### One Process, Three Threads

```
┌──────────────────────────────────────────────┐
│       Process (shared: code, heap, files)     │
│                                              │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│   │ Thread 1 │ │ Thread 2 │ │ Thread 3 │    │
│   │own stack │ │own stack │ │own stack │    │
│   └──────────┘ └──────────┘ └──────────┘    │
│                                              │
│  Threads share everything EXCEPT their stack.│
│  Fast to create, fast to communicate —       │
│  but dangerous (shared data = race conds).   │
└──────────────────────────────────────────────┘
```

### Why Do Threads Exist?

> **Question:** Why not just create more processes?

<details>
<summary>Answer</summary>

Processes are expensive (duplicate all memory). Threads are cheap (share memory). If 1000 requests each need their own process, you'd run out of RAM. Threads handle this with minimal overhead. A web server handling 1000 concurrent requests with 1000 processes would use ~1000x the memory. With threads, they share the same memory space — vastly more efficient.

</details>

### Shared Memory — The Power and the Danger

> **Question:** Thread A sets `x = 100`. Can Thread B (same process) read it?

<details>
<summary>Answer</summary>

**Yes.** Threads share memory. B sees the same `x`. Fast, but dangerous if both modify it simultaneously. Shared memory = fast communication but risk of race conditions. We'll fix this in Concurrency-3 with locks.

</details>

---

## Concurrency vs Parallelism — Formalized

You saw smart waiter (concurrency) vs 5 waiters (parallelism). Now the technical version with CPU diagrams.

**Concurrency** = dealing with multiple things at once (structure).
**Parallelism** = doing multiple things at the exact same instant (execution).

A **single-core** machine can be concurrent (switching between tasks) but NEVER truly parallel.
A **multi-core** machine can be both concurrent AND parallel.

### The 4 Scenarios

**Scenario 1: Not concurrent, not parallel**

```
1 core, 1 task at a time, NO switching
Core: [AAAAAAA][BBBBBBB][CCCCCCC]
Finish A completely, then B, then C.
Sequential. Slow.
```

**Scenario 2: Concurrent, NOT parallel**

```
1 core, multiple tasks, switching between them
Core: [AA][BB][C][AA][BB][CC][A]
Tasks INTERLEAVE on 1 core.
Concurrent (juggling) but not parallel.
```

**Scenario 3: Parallel, NOT concurrent (rare)**

```
2 cores, 2 tasks, each on its own core, no sharing
Core 1: [AAAAAAA]
Core 2: [BBBBBBB]
Truly simultaneous, but no interleaving.
```

**Scenario 4: Concurrent AND parallel**

```
2 cores, 4 tasks, switching + parallel
Core 1: [AA][CC][AA][CC]
Core 2: [BB][DD][BB][DD]
2 tasks run AT THE SAME TIME on 2 cores,
while also switching with other tasks.
This is what modern computers do.
```

> **Question:** You have 1 CPU core and 3 threads. Is this concurrent, parallel, or both?

<details>
<summary>Answer</summary>

**Concurrent but NOT parallel.** 1 core = can only run 1 thread at any instant. The OS switches between them rapidly (context switching). It LOOKS parallel but isn't. Concurrency is about STRUCTURE (handling multiple tasks). Parallelism is about EXECUTION (running at the same instant). You need multiple cores for true parallelism.

</details>

> **Question:** You have 4 CPU cores and 4 threads, each doing heavy computation. Concurrent, parallel, or both?

<details>
<summary>Answer</summary>

**Both!** 4 threads on 4 cores = all running at the exact same instant (parallel) while being managed concurrently by the OS. This is Scenario 4. Modern apps use both.

</details>

**Rob Pike (creator of Go):** *"Concurrency is about dealing with lots of things at once. Parallelism is about doing lots of things at once. Not the same, but related."*

---

## Your Processor

### This machine: Apple M2 Pro — 12 cores

**12 things can truly run at the exact same time.** Not switching — genuinely parallel.

- 1 thread = 1 core busy, 11 idle
- 12 threads = all cores busy = maximum parallelism
- 100 threads = only 12 run at once, rest take turns (context switching)

Check yours:

```bash
python3 -c "import os; print(os.cpu_count())"
```

> **Question:** Your laptop has 8 cores. You create 16 CPU-heavy processes. Faster than 8?

<details>
<summary>Answer</summary>

**No.** Only 8 can run at once. The extra 8 wait + context switching overhead. For CPU-bound, processes = cores is the sweet spot. For I/O-bound, you CAN have many more threads than cores because they spend most time waiting.

</details>

---

## What Actually Runs? (Instructions)

Your Python code becomes machine instructions. The CPU executes those one at a time per core.

### From Python to Machine Instructions

```
# You write:
x = a + b

# Python compiles to bytecode (dis module):
# LOAD_FAST    a
# LOAD_FAST    b
# BINARY_ADD
# STORE_FAST   x

# Which ultimately becomes CPU assembly instructions:
# MOV  R1, [a]      ; load a into register
# MOV  R2, [b]      ; load b into register
# ADD  R1, R2       ; add them
# MOV  [x], R1      ; store result

# The CPU executes ONE instruction at a time per core.
# A context switch can happen BETWEEN any two instructions.
```

**Everything is instructions.** Your Python, Java, Go, Rust — all become assembly instructions the CPU executes. The difference is HOW they get there (interpreted vs compiled) and HOW MANY instructions the same task takes.

See it yourself at [godbolt.org](https://godbolt.org/) — type C/C++/Rust code and see the assembly output. Compare with [language benchmarks](https://benjdd.com/languages/).

> **Question:** `counter += 1` looks like one operation. Is it one CPU instruction?

<details>
<summary>Answer</summary>

**No.** It's at least 3: READ counter, ADD 1, WRITE back. A context switch can happen between READ and WRITE, causing race conditions. This is WHY race conditions exist. `counter += 1` is NOT atomic. Two threads can both READ the same value, both ADD 1, both WRITE — one increment is lost. We'll fix this in Concurrency-3.

</details>

---

## Process vs Thread — Comparison Table

| | **Process** | **Thread** |
|---|---|---|
| **Memory** | Separate — isolated, can't see each other | Shared — same heap, same globals. Fast but dangerous. |
| **Creation cost** | Heavy — duplicates entire memory | Light — just a new stack |
| **Communication** | IPC: pipes, queues (slow, explicit) | Direct: shared variables (fast, needs locks) |
| **Crash impact** | Isolated — one crash, others fine | Shared fate — one crash kills all threads |
| **Best for** | CPU-bound (bypass GIL in Python) | I/O-bound (waiting for APIs, DB, files) |
| **Python module** | `multiprocessing` | `threading` |

---

## CPU-bound vs I/O-bound

THIS decides your concurrency strategy. Get this right and everything follows.

### I/O-bound — WAITING

CPU idle. Waiting for: API response, database query, file read, network response.

Context switching **HELPS** — while one task waits, another runs. **Use threads.**

### CPU-bound — COMPUTING

CPU at 100%. Doing: image resize, ML training, video compression, password hashing.

Context switching **HURTS** — adds overhead, no idle time to fill. **Use processes (multiple cores).**

### Test Yourself

> **Question:** Django view calls Razorpay API (500ms wait) — CPU-bound or I/O-bound?

<details>
<summary>Answer</summary>

**I/O-bound.** The Django view sends an HTTP request to Razorpay's server and then waits for the response. The CPU is idle during this wait. Threading would help here.

</details>

> **Question:** Resizing 1000 user-uploaded profile pictures — CPU-bound or I/O-bound?

<details>
<summary>Answer</summary>

**CPU-bound.** Resizing an image involves heavy pixel manipulation — mathematical operations that keep the CPU busy. Multiprocessing would help here (one process per CPU core), but threading would NOT help because the CPU is already at full utilization. Reading the file is I/O, but the resize is heavy computation. Bottleneck = CPU.

</details>

---

## Threads & Processes in Python

Now that you understand the concepts, here's how to use them.

### The Syntax — Line by Line

```python
import threading

# Step 1: Define the function your thread will run
def task(name):
    print(f"Running {name}")

# Step 2: Create a Thread object
# target = WHICH function to run (don't add () — you're passing the function, not calling it)
# args   = arguments to pass to the function (must be a TUPLE — note the trailing comma)
t = threading.Thread(
    target=task,          # task, NOT task() — no parentheses!
    args=("worker-1",)    # trailing comma makes it a tuple
)

# Step 3: Start the thread — it begins running task("worker-1") in the background
t.start()

# Step 4: Wait for it to finish — main thread blocks here until t is done
t.join()

# Without join(), the main program might exit before the thread finishes!
```

> **Question:** Why `target=task` and NOT `target=task()`?

<details>
<summary>Answer</summary>

`task` = the function object (pass it to the thread, let the THREAD call it). `task()` = call it NOW in the main thread, pass the return value. You'd be running it sequentially, defeating the purpose. `target=task` says "here's the function, call it when you start." `target=task()` would call `task()` immediately and pass `None` (the return value) as the target.

</details>

> **Question:** What does `t.join()` do? What happens if you skip it?

<details>
<summary>Answer</summary>

`join()` = "main thread, WAIT here until thread t is done." Without it, the main program might exit (or move to the next step) while the thread is still running in the background. `start()` = launch it. `join()` = wait for it. If you launch 5 threads without joining, the program might print "Done" before any thread finishes.

</details>

**`multiprocessing` has the EXACT same API.** Replace `threading.Thread` with `multiprocessing.Process`. Same `target`, `args`, `.start()`, `.join()`. Switching between threads and processes is literally a one-word change.

### Demo 1: `time.sleep()` Releases the GIL

`time.sleep()` is NOT just "pretending." It's a real I/O call that **releases the GIL**, just like a real API call would.

```python
import time, threading

def simulate_api(name, seconds):
    print(f"  {name}: starting (sleeping {seconds}s — GIL released)")
    time.sleep(seconds)    # Releases GIL! Other threads can run.
    print(f"  {name}: done!")

# Sequential: 2+1+1+1 = 5 seconds
start = time.time()
simulate_api("Razorpay", 2)
simulate_api("Email", 1)
simulate_api("SMS", 1)
simulate_api("Push", 1)
print(f"  Sequential: {time.time()-start:.1f}s\n")

# Threaded: all sleep at the same time = ~2 seconds (the longest one)
start = time.time()
threads = [
    threading.Thread(target=simulate_api, args=("Razorpay", 2)),
    threading.Thread(target=simulate_api, args=("Email", 1)),
    threading.Thread(target=simulate_api, args=("SMS", 1)),
    threading.Thread(target=simulate_api, args=("Push", 1)),
]
[t.start() for t in threads]
[t.join() for t in threads]
print(f"  Threaded:   {time.time()-start:.1f}s")
```

### Demo 2: Real Operations That Release the GIL

`time.sleep()` isn't the only thing that releases the GIL. **ALL I/O operations do:**

```python
import threading, urllib.request, time

# These ALL release the GIL while waiting:
# - time.sleep()         — OS sleep call
# - urllib.request       — network I/O
# - open().read()        — file I/O
# - socket.recv()        — network I/O
# - subprocess.run()     — waiting for child process
# - database drivers     — waiting for DB response

def fetch_url(url):
    try:
        resp = urllib.request.urlopen(url, timeout=5)  # GIL released during network wait!
        print(f"  {url[:30]}... — {len(resp.read())} bytes")
    except:
        print(f"  {url[:30]}... — failed (no internet?)")

urls = [
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
]

# Sequential: ~3 seconds
start = time.time()
for u in urls: fetch_url(u)
print(f"  Sequential: {time.time()-start:.1f}s\n")

# Threaded: ~1 second (all waiting simultaneously)
start = time.time()
threads = [threading.Thread(target=fetch_url, args=(u,)) for u in urls]
[t.start() for t in threads]
[t.join() for t in threads]
print(f"  Threaded:   {time.time()-start:.1f}s")
```

### What Releases the GIL?

Any operation where Python calls out to the OS or a C library and **waits**:

**Releases GIL:** `time.sleep()`, `requests.get()`, `open().read()`, `socket.recv()`, `subprocess.run()`, database queries, `urllib.request`

**Does NOT release GIL:** pure Python computation (`for i in range(10_000_000): x += i`). That's why threads don't help for CPU-bound work.

---

## The GIL & Language Comparison

Python has a unique limitation other languages don't. Here's what it is and why.

### GIL = Only 1 Thread Runs Python at a Time

```
WITHOUT GIL (Java, Go, Rust) — true parallel threads:
Core 1: [Thread 1 ████████████████]
Core 2: [Thread 2 ████████████████]
Core 3: [Thread 3 ████████████████]
Core 4: [Thread 4 ████████████████]

WITH GIL (Python) — threads take turns on 1 core:
Core 1: [T1][T2][T3][T4][T1][T2][T3][T4]
Core 2: [idle]
Core 3: [idle]
Core 4: [idle]
```

> **Question:** If GIL blocks parallel threads, why do threads still help with I/O?

<details>
<summary>Answer</summary>

When a thread waits for I/O (API call), it RELEASES the GIL. Other threads grab it. The waiting thread isn't doing Python work anyway — it's waiting for a network response. For CPU-bound, use `multiprocessing` — each process has its own GIL, its own Python interpreter, runs on a separate core.

</details>

### Why Does Python Have GIL?

CPython uses **reference counting** for memory management. The GIL protects the reference count from corruption by multiple threads. It's simple but limiting.

### Language Comparison

| Language | GIL? | True parallel threads? | Concurrency model |
|---|---|---|---|
| **Python** | Yes (CPython) | No (use multiprocessing) | Threads for I/O, processes for CPU |
| **Java** | No | Yes | Native threads, thread pools |
| **Go** | No | Yes | Goroutines (lightweight green threads) |
| **Rust** | No | Yes | Ownership system prevents data races at compile time |
| **JavaScript** | Single-threaded | No (Web Workers for parallel) | Event loop (like asyncio) |

**Why the difference?** Java/Go/Rust were designed for concurrency from the start. Python was designed for simplicity; concurrency was added later. The GIL was the simplest solution.

### Deep Dive: OS Threads vs Green Threads

<details>
<summary>Are Python threads real OS threads? How does GIL actually block them?</summary>

#### Two Kinds of Threads Exist

**OS Threads (Kernel Threads):** Created and scheduled by the OS kernel. The OS sees them, context-switches them. Heavy — each needs a TCB, stack (1-8MB). **Java, Python, C++ use these.**

**Green Threads (User-space):** Created by the language runtime. OS has NO idea they exist. Light — runtime controls scheduling, tiny stacks. **Go's goroutines, Erlang's processes use these.**

#### Java: 1:1 Mapping, Truly Parallel

```
Java Thread --> OS Thread --> CPU Core

Thread t1 = new Thread(...) --> OS Thread 1 --> Core 1
Thread t2 = new Thread(...) --> OS Thread 2 --> Core 2
Thread t3 = new Thread(...) --> OS Thread 3 --> Core 3

OS sees all 3. OS schedules all 3. Truly parallel.
JVM says: "OS, here's a thread, you handle it."
```

#### Python: Also 1:1 OS Threads, but GIL on Top

```
Python threads ARE real OS threads. OS sees them, schedules them.
But CPython puts a lock around its interpreter:

┌─── GIL (one mutex lock) ─────────────────────┐
│  Only ONE thread runs Python bytecode         │
│  at any instant                               │
└───────────────────────────────────────────────┘

Thread t1 --> OS Thread 1 --> Core 1  (has GIL --> running)
Thread t2 --> OS Thread 2 --> Core 2  (waiting for GIL --> idle!)
Thread t3 --> OS Thread 3 --> Core 3  (waiting for GIL --> idle!)

OS gave t2 a core. But t2 is spinning on the GIL mutex.
The OS has no idea — it thinks t2 is "running."
```

#### How GIL Releases Work — The Timeline

```
CPython releases GIL every ~5ms (sys.getswitchinterval()).
And immediately during any I/O call.

CPU-bound (GIL held, threads take turns):
Thread 1: ██████░░░░░░██████░░░░░░██████
Thread 2: ░░░░░░██████░░░░░░██████░░░░░░
           ^           ^
           GIL released every 5ms, other thread grabs it

I/O-bound (GIL released during wait):
Thread 1: ██░░░░░░░░░░░░░░░░██████    (network wait = GIL free)
Thread 2: ░░██████████████░░░░░░░░    (runs freely)
             ^
             Thread 2 gets the GIL for the entire wait duration
```

#### The Irony of Python Threads

Python threads are REAL OS threads. You pay the full cost (heavy, expensive context switches). But you get NONE of the parallelism for CPU-bound work. You get the worst of both worlds.

This is why `multiprocessing` exists (each process = own GIL) and why Python 3.13+ is experimenting with a **"no-GIL" build**.

</details>

---

## What's Next

| Today (Concurrency-1) | Concurrency-2 | Concurrency-3 | Concurrency-4 |
|---|---|---|---|
| Concepts + basics | Thread Pools & Futures | Locks & Deadlocks | Async I/O |
| Manual threads | Let Python manage for you | Safe shared resources | Single-thread concurrency |

---

## Resources

- [cpu.land](https://cpu.land/) — Interactive guide to how CPUs work. Beautifully explained.
- [PlanetScale — Processes & Threads](https://planetscale.com/blog/processes-and-threads) — Clear visual explainer with diagrams.
- [PlanetScale — I/O & Latency](https://planetscale.com/blog/io-devices-and-latency) — Why I/O is slow at the hardware level.
- [David Beazley — Understanding the Python GIL (YouTube)](https://www.youtube.com/watch?v=Obt-vMVdM8s) — THE classic deep-dive talk on the GIL.
- [Compiler Explorer (godbolt.org)](https://godbolt.org/) — See assembly output of C/Rust code.
- [Language Benchmarks (benjdd.com)](https://benjdd.com/languages/) — Python vs Java vs Go vs Rust speed.
- [Real Python — Threading](https://realpython.com/intro-to-python-threading/) — Practical threading guide.
- [Real Python — Concurrency](https://realpython.com/python-concurrency/) — Threading, multiprocessing, asyncio compared.
