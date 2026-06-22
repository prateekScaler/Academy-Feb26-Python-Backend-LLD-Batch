# Academy Feb 26 - Python Backend LLD Batch

Interactive course materials for the Python Backend Low Level Design module.

## Modules

| Module | Classes | Status |
|--------|---------|--------|
| [Backend Project](Class-01-Module-Overview-Intro-Backend/) | 16 | Completed |
| [Advanced Programming Concepts](LLD-01-Intro-to-LLD-Module-Overview/) | 12 | Completed |
| [Low Level Design](LLD-13-SOLID-Principles/) | 18 | In Progress |
| Advanced Software Engineering | 10 | Upcoming |

## Module 1: Backend Project (Completed)

| # | Class | Topics |
|---|-------|--------|
| 1 | [Module Overview & Intro to Backend](Class-01-Module-Overview-Intro-Backend/) | Client-server, HTTP basics, restaurant analogy |
| 2 | [Git: Commits, Merge, Rebase](Class-02-Git-Commits-Merge-Rebase/) | Version control fundamentals |
| 3 | [Git: Remotes, Forks, PRs](Class-03-Git-Remotes-Forks-PRs/) | Collaboration workflows |
| 4 | [Django: Apps, Views, URLs](Class-04-Django-Apps-Views-URLs/) | Django project setup, routing |
| 5 | [Django: Models & Admin](Class-05-Django-Models-Admin/) | ORM, database models, admin panel |
| 6 | [REST Framework & Serializers](Class-06-REST-Framework-Serializers/) | DRF, serialization, API design |
| 7 | [Inheritance, IDs, Custom Queries](Class-07-Inheritance-IDs-Custom-Queries/) | Model inheritance, UUID, querysets |
| 8 | [Cardinalities, N+1, Migrations](Class-08-Cardinalities-N1-Migrations/) | Relationships, query optimization |
| 8A | [N+1 Demo & Migrations](Class-08A-N1-Demo-Migrations/) | Hands-on N+1 fixes, migration strategies |
| 9 | [Exception Handling, Decorators, Middleware](Class-09-Exception-Decorators-Middleware/) | Error handling, request pipeline |
| 10 | [Intro to AWS: EC2 & RDS](Class-10-Intro-AWS-EC2-RDS/) | Cloud deployment basics |
| 11 | [AWS: EBS, VPC, Route 53, CloudWatch](Class-11-AWS-EBS-VPC-Route53-Metrics/) | Infrastructure & monitoring |
| 12 | [Payment Integration, Callbacks & Webhooks](Class-12-Payment-Callbacks-Webhooks/) | Razorpay integration |
| 13 | [Reconciliation, Crons & Razorpay](Class-13-Reconciliation-Crons-Razorpay/) | Scheduled jobs, payment reconciliation |
| 14 | [Pagination, Searching & Sorting](Class-14-Pagination-Searching-Sorting/) | API query features |
| 15 | [Redis Caching & Resume](Class-15-Redis-Caching-Resume/) | Caching strategies, resume building |

## Module 2: Advanced Programming Concepts (Completed)

| # | Class | Topics |
|---|-------|--------|
| 1 | [Intro to LLD & Module Overview](LLD-01-Intro-to-LLD-Module-Overview/) | HLD vs LLD, code qualities, interview types |
| 2 | [OOP-1: Intro to OOP, Access Modifiers, Constructors](LLD-02-OOP-1-Intro-Access-Modifiers-Constructors/) | Classes, objects, self, encapsulation, @property |
| 3 | [OOP-2: Inheritance and Polymorphism](LLD-03-OOP-2-Inheritance-Polymorphism/) | Inheritance, super(), MRO, polymorphism, duck typing, operator overloading |
| 4 | [OOP-3: Static and Abstract Base Class](LLD-04-OOP-3-Static-Abstract-Base-Class/) | @staticmethod, @classmethod, ABC, @abstractmethod |
| 5 | [Concurrency-1: Processes and Threads](LLD-05-Concurrency-1-Processes-Threads/) | Processes, threads, context switching, concurrency vs parallelism, GIL |
| 6 | [Concurrency-2: Executors and Futures](LLD-06-Concurrency-2-Executors-Futures/) | GIL deep dive, ThreadPoolExecutor, ProcessPoolExecutor, Futures |
| 7 | [Concurrency-3: Executor Syntax, Merge Sort, Mutex & Deadlock](LLD-07-Concurrency-3-Executor-Syntax-Mutex-Deadlock/) | submit(), map(), parallel merge sort, race conditions, mutex, deadlock |
| 8 | [Concurrency-4: Semaphores & Async I/O](LLD-08-Concurrency-4-Semaphores-AsyncIO/) | Semaphores, producer-consumer, async/await, event loop, asyncio |
| 9 | [Python Advanced-1: Typing and Generics](LLD-09-Python-Advanced-1-Typing-Generics/) | Typing, generics, TypeVar, Protocol, mypy |
| 10 | [Python Advanced-2: Collections](LLD-10-Python-Advanced-2-Collections/) | defaultdict, Counter, deque, namedtuple, frozenset, UserDict, thread safety |
| 11 | [Python Advanced-3: Lambda Functions and FP](LLD-11-Python-Advanced-3-Lambda-FP/) | Functions as first-class objects, lambdas, map/filter/reduce, functools |
| 12 | [Python Advanced-4: Exception Handling](LLD-12-Python-Advanced-4-Exception-Handling/) | try/except/else/finally, EAFP vs LBYL, custom exceptions, copy & deepcopy |

## Module 3: Low Level Design (In Progress)

| # | Class | Topics |
|---|-------|--------|
| 1 | [SOLID Principles &mdash; Part 1](LLD-13-SOLID-Principles/) | Why SOLID, God classes, SRP, OCP, LSP intro |
| 2 | [SOLID Principles &mdash; Part 2](LLD-14-SOLID-Principles-2/) | OCP/LSP recap, ISP, composition, DIP, LSP vs ISP, SOLID critique |
| 3 | [Intro to Design Patterns, Singleton](LLD-15-Design-Patterns-Singleton/) | GoF intro, 3 categories, Singleton (4 implementations + how each breaks) |
| 4 | [Builder Pattern](LLD-16-Builder-Design-Pattern/) | The problem (boolean hell, telescoping constructors), 4-step recipe, Pizza/HTTP/SQL builders, Director |
| 5 | [Factory Pattern Family](LLD-17-Factory-Design-Pattern/) | Simple Factory, Factory Method (OCP + DIP), Abstract Factory (family-consistency); decision tree; 8 runnable examples + UML-friendly code for PyCharm |
| 6 | [Prototype &amp; Adapter](LLD-18-Prototype-and-Adapter/) | Prototype (clone vs. construct), Adapter (translate mismatched interfaces); travel-socket intro; Django payments refactor case study; 12 runnable Python examples + BEFORE/AFTER UML diagrams |
| 7 | [Strategy &amp; Observer](LLD-19-Strategy-and-Observer/) | First two behavioural patterns &mdash; Strategy (swap the algorithm) and Observer (one event, many reactions). Recap teaches Prototype Registry + Adapter variations (Object/Class/Two-Way). 11 runnable Python examples including a stdlib Strategy survey and an asyncio Observer. |
| 8 | [Decorator &amp; UML Diagrams](LLD-20-Decorator-and-UML-Diagrams/) | Decorator (wrap an object to add behaviour) + UML for backend design. Chai-shop case study (MasalaChai / FilterCoffee with Elaichi / Adrak), stacked API-client decorators, inheritance-explosion trap. UML: class + sequence diagrams, 6 relationship arrow types as mini-SVGs, Three Amigos history, full 14-diagram-type classification, is-a vs has-a deep-dive (Composition / Aggregation / Association / Inheritance), sequence-diagram anatomy mini-gallery (sync / async / return arrows + alt / loop / par / opt frames). Python GC + weakref primer. 8 runnable examples + Pattern Cheat Sheet appendix covering 12 patterns. |
| 9 | [Types of LLD Interviews &amp; How to Approach](LLD-21-Types-of-LLD-Interviews-Approach/) | The methodology class. Indian-tech tiers (Traditional IT / Product MNCs / Modern startups) + the six concrete formats. The 7-step playbook (Clarify → Requirements → Entities → APIs → Code → Demo → Trade-offs) with worked examples (Zoomcar, Splitwise, BookMyShow, Uber matching) as collapsibles. Mistakes that tank interviews. Design-a-Pen warm-up with 5 evolutions (single class → inheritance → Strategy → abstract intermediates → Protocols). Recap with 6 spot-the-pattern-from-UML quizzes (neutral domain labels) + 4 UML-relationship quizzes. 39 quizzes, balanced answer distribution (A 28% / B 28% / C 23% / D 20%). 5 runnable Python files (Parking Lot, 7-step template, Splitwise skeleton, code-review target, interview clock CLI). |
| 10 | [Design Tic-Tac-Toe](LLD-22-TicTacToe-Design/) | From the FRs and [Discussion #12](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/12) submissions to the decided classes: re-derive every relationship (composition vs aggregation via the lifetime question &mdash; *can the part outlive the whole, or be shared?*), settle the reference class diagram, and freeze the API signatures before any code is written. |
| 11 | [Code Tic-Tac-Toe](LLD-23-TicTacToe-Code/) | Build the engine live from LLD-22's diagram &mdash; a single file **and** a packaged tree (models / strategies / game / `console.py` toolkit / CLI). Win-check complexity tiers (O(n&sup2;&middot;k) &rarr; O(k) &rarr; O(1)), Gomoku as a two-argument extension. Companion challenges open as Issues #14&ndash;16 (code smells, undo, winner-check). |
| 12 | [Design Parking Lot](LLD-24-ParkingLot-Design/) | The most-asked machine-coding problem, same playbook: align &rarr; actors &rarr; FR sentences &rarr; derive every class &rarr; ownership. Two Strategies (assignment + pricing) from minute one, the exception-vs-value flip (a full lot is not an error), `Spot` as the `Cell` analogue, the `Ticket`/`Payment` records. Use-case diagram, three labelled lot diagrams, derive-the-methods quizzes. Homework: class diagram ([Discussion #21](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/21)) + REST API ([Discussion #20](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/20)). |
| 13 | [Code Parking Lot](LLD-25-ParkingLot-Code/) | Build it live: reference class diagram (skeleton &rarr; derive methods &rarr; complete) &rarr; API signatures &rarr; the layered package (domain / strategies / **repositories** / service / CLI) &rarr; sequence diagram + Ticket/Spot state machines &rarr; the backend mapping (layers, REST endpoints, **schema**) &rarr; trade-offs. Single-file + packaged versions, both assert green. API & design-decision quizzes, a full API doc, and a schema-from-the-diagram exercise. |
| 14 | [Design BookMyShow](LLD-26-BookMyShow-Design/) | The concurrency problem, same playbook: overview &rarr; clarify &rarr; structural-vs-behavioural FRs &rarr; derive every class round-by-round &rarr; class diagram &rarr; schema &rarr; trade-offs. The star entity is the **ShowSeat** (the seat &times; show pairing) &mdash; arrived at intuitively in a second round, then resolved as an **association class = associative table**. Use-case diagram, click-to-reveal FRs, the seat-map &amp; user-journey pictures, decision quizzes (where status+price live, FK placement), an ER diagram off the class diagram, and a brief survey of concurrency approaches (code lock / pessimistic / optimistic / DB constraint / Redis) deferred to LLD-27. Homework: class diagram ([Discussion #23](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/23)) + REST API ([Discussion #22](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/22)). |
| 15 | [Code BookMyShow](LLD-27-BookMyShow-Code/) | The promise from LLD-26, delivered: build the **ShowSeat** model (`Show → ShowSeat`, the hold = `LOCKED` + TTL, `Ticket` + `Payment`) and make **concurrency** the headline. A **tournament** runs the *same* seat-stampede under every approach &mdash; naive (the bug) · in-process lock · pessimistic `SELECT … FOR UPDATE` · optimistic (version/CAS) · DB `UNIQUE` · Redis · the soft-lock hold &mdash; and shows code/DB/**UI** for each. **Optimistic vs pessimistic** intuition, why the `UNIQUE` constraint alone isn't enough (INSERT vs UPDATE → lost update), a **DDIA Ch.7 transactions** quiz + anomalies diagram, an animated [concurrency visualizer](LLD-27-BookMyShow-Code/concurrency-visualizer.html), and a runnable `02_concurrency_demo.py`. Discussion: [#24 freeing expired holds without overloading the DB](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/24). |
| 16-17 | Design & Code Splitwise | Upcoming |
| 18 | Design Google Calendar | Upcoming |

## Latest

&#127919; **[LLD-27 &mdash; BookMyShow: Code](LLD-27-BookMyShow-Code/)** &mdash; the promise from LLD-26, delivered. Build the **ShowSeat** model in code (`Show → ShowSeat`, the hold = `status=LOCKED` + a `locked_until` TTL, `Ticket` + `Payment`), then make **concurrency** the headline. A **tournament** (`02_concurrency_demo.py`) runs the *same* N-users-one-seat stampede under every approach &mdash; naive (the bug) · in-process lock · pessimistic `SELECT … FOR UPDATE` · optimistic (version / CAS) · DB `UNIQUE` · Redis lock · the soft-lock hold &mdash; and the page breaks each down by **code, DB, and UI** (the spinner, the optimistic rollback, the BookMyShow countdown). The hard ideas, made simple: **optimistic vs pessimistic** ("lock the door first" vs "act, then check at checkout"); why a `UNIQUE(show_id, seat_id)` constraint *alone* isn't enough (it guards an INSERT, but the hold is an UPDATE &rarr; a lost update); and a **DDIA Ch.7 transactions** quiz with a visual anomalies diagram (dirty read &rarr; read skew &rarr; lost update &rarr; the seat race = **write skew**). Plus an animated **[concurrency visualizer](LLD-27-BookMyShow-Code/concurrency-visualizer.html)**. Built on the LLD-26 design; discussions [#22](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/22)/[#23](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/23)/[#24](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/24).

## Quick Start

Open any class folder and view its `index.html` in your browser. From LLD-13 onward, every class also ships a [`code/`](LLD-18-Prototype-and-Adapter/code/) directory with self-contained `python3`-runnable examples (no `pip install` needed) and a class-level `README.md` you can read instead of the HTML.

```bash
# Browse a class's interactive notes
open LLD-18-Prototype-and-Adapter/index.html

# Run one of its code examples
python3 LLD-18-Prototype-and-Adapter/code/06_payment_gateway_adapter.py

# Or just read the long-form lesson
less LLD-18-Prototype-and-Adapter/README.md
```
