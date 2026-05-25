# LLD-16: Builder Design Pattern

> Stop writing constructors that take ten boolean parameters in a row.
> Build complex objects step-by-step with a clean, fluent API.

---

## What's Covered

1. **Recap of Singleton** — 3 quick checks (`__init__` trap, inheritance gotcha, pickle)
2. **Intro to Builder** — the four ingredients (Product, Builder, fluent setters, `build()`)
3. **Prereq quiz** — 6 questions on the smells Builder cures (boolean hell, two-phase construction, telescoping constructors, business logic in `__init__`, `@staticmethod`, `return self`)
4. **The Problem** — three concrete smells walked through with code
5. **The Solution** — building a Database Builder in 4 steps
6. **Three variations** — inner-class Builder, separate Builder, Director for presets
7. **Three real-world examples** — Order (variable composition), HTTP request (optional knobs), SQL query (accumulated state)
8. **4 common pitfalls + 6 best practices**
9. **When to use / when to skip Builder**
10. **Mindmap summary + interview cheat sheet**
11. **Resources** — books, Python tools, real codebases that use Builder

---

## File Layout

```
LLD-16-Builder-Design-Pattern/
├── README.md                          ← you are here
├── index.html                         ← interactive class notes
└── code/
    ├── 01_database_builder.py         ← canonical 4-step recipe
    ├── 02_order_builder.py            ← variable composition (add_item / apply_discount x N)
    ├── 03_http_request_builder.py     ← optional knobs with defaults
    ├── 04_query_builder.py            ← accumulated state → SQL string
    ├── 05_director.py                 ← named presets on top of the Builder
    ├── 06_dataclass_under_hood.py     ← homemade @dataclass in ~30 lines (how it works)
    ├── 07_notification_builder.py     ← the 10-param Notification → fluent Builder
    └── 08_test_data_builder.py        ← `a_user().premium().build()` pattern for test fixtures
```

Each `.py` file is runnable: `python3 code/01_database_builder.py`

---

## The 4-Step Recipe (memorize this)

| Step | What | Where |
|---|---|---|
| 1 | Product class with trivial `__init__` | `@dataclass` is usually enough |
| 2 | Inner `Builder` class with mutable state | Lives inside the Product |
| 3 | Setters that `return self` | One per field |
| 4 | `build()` validates, then constructs | All business logic lives here |

```python
@dataclass
class Database:
    host: str
    port: int
    username: str
    password: str

    @staticmethod
    def builder():
        return Database.Builder()

    class Builder:
        def __init__(self):
            self._host = self._port = self._username = self._password = None

        def set_host(self, host):         self._host = host;         return self
        def set_port(self, port):         self._port = port;         return self
        def set_username(self, username): self._username = username; return self
        def set_password(self, password): self._password = password; return self

        def build(self) -> Database:
            self._validate()
            return Database(self._host, self._port, self._username, self._password)

        def _validate(self):
            if not self._host:                         raise ValueError("host required")
            if not (1024 <= (self._port or 0) <= 65535): raise ValueError("bad port")
            # ...
```

---

## Three Variations at a Glance

| Variation | When to use |
|---|---|
| **A. Inner-class Builder** *(default)* | Tight encapsulation, clean entry point. Pick this unless you have a reason not to. |
| **B. Separate Builder class** | Builder is complex enough to live in its own file/test suite. |
| **C. Director on top** | You have *real* recurring presets (`DatabaseDirector.local()`, `.production()`). |

---

## Decision Tree

```
Does the constructor have many optional fields, or complex validation?
├─ No, just 2-3 required fields                 → plain __init__
├─ Mostly required + a couple defaults          → kwargs with defaults
├─ Many optional fields, no validation          → @dataclass with defaults
├─ Many optional + validation + assembly logic  → Builder ← TODAY
└─ Validation is THE main thing                 → pydantic
```

---

## Common Pitfalls

| Mistake | The fix |
|---|---|
| Forgot `return self` on a setter | Add it; chaining works again |
| No validation in `build()` | Move all `if not …` checks into `_validate()`, called from `build()` |
| Reused a Builder for two Products | One Builder, one Product. Start a new chain each time. |
| Business logic crept back to `__init__` | Move it back to the Builder; Product stays a `@dataclass` |
| Forgot defensive copy of a list / dict | `list(self._toppings)` in `build()`, not the original |

---

## Interview Cheat-Sheet

When asked to implement a Builder:

1. Sketch the Product first — just the fields. Use `@dataclass`.
2. Add the inner `Builder` with one private field per Product field, plus sensible defaults.
3. One setter per field, each returning `self`. Use `add_*` for list fields, `set_*` for scalars.
4. `build()`: call `_validate()`, then construct and return the Product. Make defensive copies of mutable state.
5. Add a `@staticmethod` entry point on the Product: `def builder(): return Cls.Builder()`.
6. Mention *when not* to use it — that's the signal you've understood the pattern.

---

## Related Reading

### From this batch
- [LLD-15: Singleton](../LLD-15-Design-Patterns-Singleton/) — the first creational pattern
- [LLD-14: SOLID Part 2](../LLD-14-SOLID-Principles-2/) — composition primer

### External
- [Refactoring.Guru — Builder in Python](https://refactoring.guru/design-patterns/builder/python/example)
- [python-patterns.guide — Builder](https://python-patterns.guide/gang-of-four/builder/) (Brandon Rhodes — opinionated, sharp)
- [Telescoping Constructor anti-pattern](https://www.vojtechruzicka.com/avoid-telescoping-constructor-pattern/) — the smell Builder cures
- [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) / [`pydantic`](https://docs.pydantic.dev/) / [`attrs`](https://www.attrs.org/) — Python tools that often replace a hand-rolled Builder

### Builder in real Python code
- `requests.PreparedRequest`
- SQLAlchemy `select()` and `Query` chaining
- Django `QuerySet` (filter / exclude / order_by chaining)

---

*LLD-16 · Academy Feb 26 — Python Backend LLD Batch · Instructor: Prateek Vijay*
