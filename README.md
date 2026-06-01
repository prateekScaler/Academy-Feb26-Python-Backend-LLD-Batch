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
| 7 | Strategy, Observer | Upcoming |
| 8 | Decorator, UML Diagrams | Upcoming |
| 9 | Types of LLD Interviews, How to Approach LLD Problems | Upcoming |
| 10-11 | Design & Code TicTacToe | Upcoming |
| 12-13 | Design & Code Parking Lot | Upcoming |
| 14-15 | Design & Code BookMyShow | Upcoming |
| 16-17 | Design & Code Splitwise | Upcoming |
| 18 | Design Google Calendar | Upcoming |

## Latest

&#127919; **[LLD-18 &mdash; Prototype &amp; Adapter](LLD-18-Prototype-and-Adapter/)** &mdash; the last creational pattern + the first structural one, with a real-life travel-socket intro, BEFORE/AFTER UML diagrams for the interface-mismatch problem, parallel Razorpay &amp; Stripe adapters, and a full Adapter-pattern refactor of an actual Django payments view. 12 runnable Python examples.

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
