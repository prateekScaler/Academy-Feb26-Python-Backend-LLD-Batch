# LLD-17: Factory Design Pattern Family

> Centralize the "which concrete class do I instantiate, and with what
> configuration?" choice. Three variants — Simple Factory, Factory Method,
> Abstract Factory — each solving a slightly different version of the
> same problem.

---

## What's Covered

1. **Recap of Builder** — 3 quizzes (Builder's main advantage with UML &
   honest negatives, when Builder is overkill with classic LLD examples,
   the state-sharing bug + fix code)
2. **Intro & family map** — what *Factory* means, three variants in one
   visual map
3. **Prereq quiz** — the scattered-creation smell (DRY + SOLID)
4. **The Problem** — a notification layer that's drowning in duplicated
   construction across 30 files
5. **Simple Factory** — one static `create()` method with `if/elif`,
   plus two more worked examples (parser factory, logger factory) and
   "how often you'll see it" stat
6. **Factory Method** — abstract creator + one subclass per type, DIP
   bonus, *Creator vs *Factory naming convention diagram, document export
   example, frequency stat
7. **Abstract Factory** — progressive narrative (original naive code →
   Attempt 1 Simple Factory → Attempt 2 per-widget Factory Method →
   Attempt 3 Abstract Factory), plus two worked examples (test
   infrastructure factory, cloud provider SDK) with UMLs, frequency stat
8. **Comparison & decision tree** — table of all three + decision flow
   + the "when no factory is right" question
9. **Mindmap summary** — every variant at a glance + interview cheat
   sheet
10. **Resources** — canonical references, Python idioms, real codebases
    where each variant shows up

---

## File Layout

```
LLD-17-Factory-Design-Pattern/
├── README.md                                  ← you are here
├── index.html                                 ← interactive class notes
└── code/
    ├── 01_simple_factory.py                   ← Notification Simple Factory
    ├── 02_factory_method.py                   ← Notification Factory Method (Discord added later, zero edits)
    ├── 03_abstract_factory.py                 ← Windows/Mac/Linux widget families
    ├── 04_payment_gateway_factory_method.py   ← Stripe/PayPal/Razorpay second example
    ├── 05_anti_pattern_overengineered.py      ← PointFactory anti-pattern + @classmethod alternative
    ├── 06_vehicle_factory_method.py           ← Cars/Trucks/Motorcycles - rich UML in PyCharm
    ├── 07_theme_abstract_factory.py           ← Light/Dark/HighContrast theme families - 3 product types
    └── 08_all_three_side_by_side.py           ← Same Pet domain, three variants side-by-side
```

Each `.py` file is runnable: `python3 code/01_simple_factory.py`

### 🔬 Viewing UML diagrams in PyCharm

Files **06, 07, 08** are designed to render cleanly as UML class
diagrams. In PyCharm:

1. Right-click the file in the Project pane
2. **Diagrams** → **Show Diagram…**
3. Enable: **Methods**, **Fields**, **Constructors**,
   **Implements / Extends edges**, **Dependencies**

You'll see the abstract base + concrete subclasses + composition arrows
visually — useful when revising the patterns before an interview.

---

## The Three Variants at a Glance

| | Simple Factory | Factory Method | Abstract Factory |
|---|---|---|---|
| **Solves** | Duplicated construction | Adding new types without modifying old code | Family-consistency of related products |
| **Mechanism** | One static method with `if/elif` | Abstract base + one subclass per type | Abstract base producing many products + one subclass per family |
| **Number of products** | 1 abstract | 1 abstract | Many abstract that go together |
| **OCP compliant?** | ❌ Modify to add | ✅ Add subclass | ✅ Add family subclass |
| **Complexity** | ⭐ lowest | ⭐⭐ medium | ⭐⭐⭐ highest |
| **Frequency** | 📊 ~7–8 / 10 | 📊 ~4–5 / 10 | 📊 ~1–2 / 10 |

---

## Decision Tree

```
Do callers need to pick a concrete class?
├─ No, one obvious class                       → just the constructor
├─ Yes, few stable types                       → Simple Factory
├─ Yes, types added often                      → Factory Method
└─ Yes AND products travel in matching families → Abstract Factory
```

---

## Interview Cheat-Sheet

When asked "implement a Factory for X":

1. Sketch the **abstract product** first.
2. Show **concrete products**.
3. Add the simplest variant: `@staticmethod create()` with `if/elif`.
   Name the OCP problem out loud.
4. Refactor to Factory Method (abstract creator + concrete subclasses).
   Point out the DIP win (callers depend on the abstraction).
5. If asked "but what if products must match families?" — that's the
   Abstract Factory cue.
6. Mention the anti-pattern (`PointFactory`) — names the over-engineering
   case, shows pattern fluency.

---

## Related Reading

### From this batch
- [LLD-15: Singleton](../LLD-15-Design-Patterns-Singleton/) — controls *how many*
- [LLD-16: Builder](../LLD-16-Builder-Design-Pattern/) — controls *how assembled*
- [LLD-13: OCP](../LLD-13-SOLID-Principles/#ocp) — what motivates Factory Method
- [LLD-14: DIP](../LLD-14-SOLID-Principles-2/#dip) — what Factory Method delivers for free

### External
- [Refactoring.Guru — Factory Method in Python](https://refactoring.guru/design-patterns/factory-method/python/example)
- [Refactoring.Guru — Abstract Factory in Python](https://refactoring.guru/design-patterns/abstract-factory/python/example)
- [python-patterns.guide — Abstract Factory (Brandon Rhodes)](https://python-patterns.guide/gang-of-four/abstract-factory/)
- [`functools.singledispatch`](https://docs.python.org/3/library/functools.html#functools.singledispatch) — modern Python alternative to Simple Factory

### Factories in real Python code
- `logging.getLogger(name)` — Simple Factory
- `sqlalchemy.create_engine(url)` + dialects — Abstract Factory
- Django DB backends — Abstract Factory
- `boto3.client("s3")` — Simple Factory dispatch
- `requests.adapters.HTTPAdapter` subclasses — Factory Method

---

*LLD-17 · Academy Feb 26 — Python Backend LLD Batch · Instructor: Prateek Vijay*
