# Python Backend Engineering Course

Interactive course materials for the Python Backend LLD module — a comprehensive journey from fundamentals to production-ready applications.

## Course Structure

**4 Modules | 56 Classes | Hands-on Projects**

| Module | Classes | Focus |
|--------|---------|-------|
| Backend Project | 16 | Django, REST APIs, AWS, Payments |
| Advanced Programming | 12 | OOP, Concurrency, Python Advanced |
| Low Level Design | 18 | SOLID, Patterns, System Design |
| Advanced Engineering | 10 | Testing, Auth, Monitoring, Containers |

---

## Module 1: Backend Project (Current)

Building a production-ready backend using the **Restaurant Analogy** as our mental model.

### The Restaurant Mental Model

| Restaurant | Backend System |
|------------|----------------|
| Customer | Browser / Mobile App |
| Menu | API Specification |
| Waiter | Server / Controller |
| Kitchen/Pantry | Database |

**Golden Rule:** The customer never enters the kitchen. (Browser never talks directly to database)

### Class-by-Class Breakdown

| # | Topic | Restaurant Analogy |
|---|-------|-------------------|
| 1 | Module Overview, Intro to Backend | What is a restaurant? Who are the actors? |
| 2 | Git, Commits, Merge, Rebase | How do multiple chefs work on the same recipe book? |
| 3 | Git Remotes, Forks, PRs | How do chefs across branches share recipes? |
| 4 | Django Apps, Views, URLs | Who greets customers and routes them to tables? |
| 5 | Django Models and Admin | How does the kitchen track inventory? |
| 6 | REST Framework, Serializers | How do we design the menu and plate the food? |
| 7 | Inheritance, IDs, Queries | How do we handle dish categories and combos? |
| 8 | Cardinalities, N+1, Migrations | How do we manage ingredient relationships? |
| 9 | Exception Handling, Middlewares | What if a dish fails? How do we handle complaints? |
| 10 | AWS, EC2, RDS | Moving from home kitchen to commercial kitchen |
| 11 | VPC, Security, Route 53 | Securing the building, staff-only areas |
| 12 | Payment Callbacks, Webhooks | How does the card machine talk to the bank? |
| 13 | Payment Deep Dive | What if payment fails mid-transaction? |
| 14 | Reconciliation, Crons, Stripe | Daily cash register balancing |
| 15 | Pagination, Searching, Sorting | Organizing a 100-page menu efficiently |
| 16 | Redis, API Optimization | Making the kitchen faster during rush hour |

---

## Core Concepts

### Client-Server Architecture

```
┌──────────┐         HTTP Request          ┌──────────┐
│  Client  │  ───────────────────────────► │  Server  │
│ (Browser)│                               │ (Django) │
│          │  ◄─────────────────────────── │          │
└──────────┘         HTTP Response         └──────────┘
                    (JSON data)
```

### HTTP Methods

| Method | Purpose | SQL Equivalent | Safe? |
|--------|---------|----------------|-------|
| `GET` | Read data | SELECT | Yes |
| `POST` | Create new | INSERT | No |
| `PUT` | Update existing | UPDATE | No |
| `DELETE` | Remove | DELETE | No |

**Important:** GET requests must be "safe" — no side effects. Never use GET for destructive operations.

### JSON: The Data Format

```json
{
  "user_id": 101,
  "username": "backend_dev",
  "is_verified": true,
  "skills": ["Python", "Django", "REST APIs"]
}
```

Why JSON?
- Human readable
- Machine parseable
- Language agnostic
- Maps directly to Python dictionaries

### Localhost vs Cloud

| Aspect | Localhost (Home Kitchen) | Cloud (Cloud Kitchen) |
|--------|-------------------------|----------------------|
| Access | Only you | Anyone on internet |
| Uptime | When laptop is on | 24/7/365 |
| Scale | Single user | Millions of users |
| Cost | Free | Pay per use |
| Setup | Simple | More complex |

---

## Tech Stack Comparison

| Language | Framework | Best For | Learning Curve |
|----------|-----------|----------|----------------|
| **Python** | Django/FastAPI | Rapid dev, ML integration | Easy |
| Java | Spring Boot | Enterprise, large teams | Medium |
| Node.js | Express/NestJS | Real-time, JS everywhere | Easy |
| Go | Gin | High performance, infra | Medium |
| Rust | Actix/Axum | Max performance, safety | Hard |

**This course uses Python + Django** — optimal for learning backend concepts with readable, maintainable code.

Compare framework performance: [TechEmpower Benchmarks](https://www.techempower.com/benchmarks/)

---

## Prerequisites

- **Python**: Variables, loops, functions, classes
- **Data Structures**: Lists, dictionaries, sets
- **OOP**: Inheritance, encapsulation basics
- **Terminal**: Basic commands (`cd`, `mkdir`, `ls`)

**Terminal Practice:**
- [Terminal Tutor](https://www.terminaltutor.com/) — Interactive in-browser terminal
- [Linux Survival](https://linuxsurvival.com/) — Gamified Linux basics
- [CMD Challenge](https://cmdchallenge.com/) — Practice with challenges

---

## Key Interview Questions (Class 1)

1. **What is the difference between frontend and backend?**
   > Frontend is the UI users interact with. Backend is server logic, databases, and processing that powers the frontend.

2. **Explain client-server architecture.**
   > Client sends requests, server processes and responds. They're separate programs communicating over a network.

3. **What are HTTP methods and when do you use each?**
   > GET (read), POST (create), PUT (update), DELETE (remove). GET must be safe with no side effects.

4. **What is an API?**
   > A defined contract for how software components communicate — specifies available operations and data formats.

5. **Why can't browsers execute SQL directly?**
   > Security. Server acts as gatekeeper — validates requests, checks authentication, controls data access.

6. **What is JSON?**
   > Lightweight, human-readable data format for client-server communication. Language-agnostic, maps to Python dicts.

---

## View

```bash
# Open in browser
open index.html  # macOS
start index.html  # Windows
```

---

## Tools to Install

- [Postman](https://www.postman.com/downloads/) — API testing
- [Git](https://git-scm.com/downloads) — Version control
- [Python 3.x](https://www.python.org/downloads/) — Programming language
- [PyCharm](https://www.jetbrains.com/pycharm/) — Python IDE (recommended)

---

## License

Educational material for Scaler Academy Python Backend LLD Batch.
