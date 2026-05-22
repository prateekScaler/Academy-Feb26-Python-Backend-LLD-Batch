# LLD-15: Design Patterns Intro & Singleton

> Patterns are vocabulary — the shorthand experienced engineers use to communicate proven solutions.

---

## What's Covered

1. **Intro to Design Patterns** — what they are, why they exist (Gang of Four, 1994), and the three categories
2. **The three categories** — Creational, Structural, Behavioral — with examples
3. **Pre-requisite quiz** — 4 warm-ups on class vs instance variables, encapsulation, `__new__` vs `__init__`, when Singleton makes sense
4. **The Singleton problem** — why duplicate database connections, loggers, configs hurt
5. **Four implementations**, each with breaking examples:
   - `__new__` override (classic textbook)
   - Decorator (cleanest separation)
   - Metaclass (most powerful)
   - Module-level instance (most Pythonic — the recommended default)
6. **Thread safety** — double-checked locking, when each approach needs it
7. **Practical use cases** — Config, Logger, Connection Pool
8. **Anti-patterns** — `Utils` god object, hidden dependencies, domain objects as singletons
9. **Decision guide** — which approach to use when

---

## File Layout

```
LLD-15-Design-Patterns-Singleton/
├── README.md                          ← you are here
├── index.html                         ← interactive class notes
└── code/
    ├── 01_new_singleton.py            ← A1: __new__ (init gotcha + threading race)
    ├── 02_thread_safe_singleton.py    ← A2: __new__ + double-checked locking
    ├── 03_module_singleton.py         ← Optional A: module-level (+ breaks)
    ├── 04_decorator_singleton.py      ← Optional B: decorator (+ breaks)
    ├── 05_metaclass_singleton.py      ← Optional C: metaclass (+ breaks)
    ├── 06_use_cases.py                ← Config, Logger, ConnectionPool
    └── 07_hardened_singleton.py       ← Combines every defense (verified at runtime)
```

Each `.py` file is runnable: `python3 code/01_new_singleton.py`

---

## The Approaches at a Glance

**Mandatory path (covered in depth):**

| # | Approach | Thread-safe? | Notes |
|---|---|---|---|
| A1 | `__new__` (classic) | ❌ | Init gotcha + race condition shown |
| A2 | `__new__` + double-checked locking | ✅ | The default working Singleton |

**Optional alternatives (each with its own break modes):**

| Letter | Approach | Best for |
|---|---|---|
| Opt A | Module-level instance | Default choice in plain Python apps |
| Opt B | Decorator (`@singleton`) | Bolt-on, clean classes |
| Opt C | Metaclass | Libraries, framework code, `isinstance()` |

**Production-grade:**

| | Approach | What it defends |
|---|---|---|
| 💎 | Hardened (metaclass + lock + `__copy__` + `__reduce__`) | Threading, deepcopy, pickle, subclassing |

---

## How Each One Can Break

This is the unique angle for this class — for *each* implementation, we
show concrete code where the singleton invariant breaks. The `code/`
files demonstrate every failure mode at runtime.

| Implementation | Breaks under… |
|---|---|
| `__new__` | subclassing leaks instances · `copy.deepcopy` · `pickle.loads` · threading races |
| Decorator | `isinstance()` (class is now a function) · subclassing · silent arg-drop · `deepcopy`/`pickle` |
| Metaclass | metaclass conflict with `ABCMeta` · `object.__new__` bypass · `deepcopy`/`pickle` |
| Module-level | `_Class` instantiated directly · `importlib.reload` · two import paths · multiprocessing |

---

## Decision Tree

```
Need exactly one instance?
├─ Application code, simple case → module-level instance (recommended)
├─ Threaded application         → module-level (already safe) OR double-checked locking
├─ Library / framework / need isinstance() + subclassing → metaclass
├─ Want to bolt singleton onto a clean class → decorator
└─ Learning / interview          → start with __new__, mention thread safety
```

---

## Interview Cheat-Sheet

When asked to implement Singleton:

1. Write the `__new__` version first — shows you understand object creation.
2. Add the `__init__` guard (initialization flag) — shows you know `__init__` still runs.
3. Mention thread safety with **double-checked locking**.
4. Close with: *"In real Python code I'd usually just use a module-level instance — it's the simplest correct singleton in the language."*

That answer signals you know the pattern *and* when not to over-engineer it.

---

## When NOT to Use Singleton

- **`Utils` god class** — unrelated methods bolted together. Just use a module.
- **Hidden dependencies** — reaching for `Logger()` inside method bodies hides what code depends on, makes testing painful. Inject instead.
- **Domain objects** — `User`, `Order`, `Product` should have many instances. Singleton is for *infrastructure*.

---

## Related Reading

- **In this repo:** [LLD-14: SOLID Principles Part 2](../LLD-14-SOLID-Principles-2/) — composition, DIP, Python DI ecosystem
- *Design Patterns* (Gang of Four, 1994) — the original catalog
- Brandon Rhodes — *Composition over Inheritance* — argues most singletons should be modules

---

*LLD-15 · Academy Feb 26 — Python Backend LLD Batch · Instructor: Prateek Vijay*
