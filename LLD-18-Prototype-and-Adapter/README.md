# LLD-18 — Prototype & Adapter

*The last creational pattern, the first structural one — and the two everyday tools they unlock.*

> This README is the **full lesson in long form**. If you'd rather click through interactive quizzes, open [`index.html`](./index.html). If you want to run the patterns, the [`code/`](./code/) directory has 12 self-contained Python examples — each file is `python3`-runnable with no dependencies.

---

## Table of contents

1. [At a glance](#at-a-glance)
2. [Recap from LLD-17 — Factory family](#recap-from-lld-17--factory-family)
3. [Pattern-selection warm-up](#pattern-selection-warm-up)
4. [Part 1 — Prototype](#part-1--prototype)
   - 4.1 [Prerequisite: the `copy` module](#41-prerequisite-the-copy-module)
   - 4.2 [The problem](#42-the-problem--building-from-scratch-is-sometimes-very-expensive)
   - 4.3 [The pattern](#43-the-pattern--clone-instead-of-new)
   - 4.4 [Variations](#44-variations)
   - 4.5 [Pitfalls](#45-pitfalls)
   - 4.6 [UML & 4-step recipe](#46-uml--4-step-recipe)
   - 4.7 [When Prototype earns its keep](#47-when-prototype-earns-its-keep)
5. [Part 2 — Adapter](#part-2--adapter)
   - 5.1 [Before the code — the travel adapter you already know](#51-before-the-code--the-travel-adapter-you-already-know)
   - 5.2 [Prerequisites: duck typing + composition](#52-prerequisites-duck-typing--composition)
   - 5.3 [The problem](#53-the-problem--two-interfaces-that-just-dont-match)
   - 5.4 [Case study — refactoring `restaurant_project/payments/views.py`](#54-case-study--refactoring-restaurant_projectpaymentsviewspy)
   - 5.5 [The pattern](#55-the-pattern--object-adapter-via-composition)
   - 5.6 [Variations](#56-variations)
   - 5.7 [Adapter in the wild](#57-adapter-in-the-wild)
   - 5.8 [Pitfalls](#58-pitfalls)
   - 5.9 [Production conventions](#59-production-conventions)
   - 5.10 [When Adapter earns its keep](#510-when-adapter-earns-its-keep)
6. [Compare — Adapter vs the rest of the structural family](#compare--adapter-vs-the-rest-of-the-structural-family)
7. [Cross-family — Factory vs Adapter vs Strategy](#cross-family--factory-vs-adapter-vs-strategy)
8. [Summary mindmap](#summary-mindmap)
9. [Interview cheat sheet](#interview-cheat-sheet)
10. [Code companions](#code-companions)
11. [Further reading](#further-reading)

---

## At a glance

Today's class crosses a boundary. We finish the **Creational** family with **Prototype**, then step into **Structural** patterns with **Adapter**.

```
The 23 GoF patterns — where we are after today

  Creational (5)               Structural (7)              Behavioural (11)
  "How is the object made?"   "How are objects composed?"  "How do they collaborate?"

  Singleton    ✓                Adapter         ← today    Strategy
  Builder      ✓                Decorator                  Observer
  Factory Method ✓              Facade                     Command
  Abstract Factory ✓            Proxy                      State
  Prototype    ← today          Bridge                     Iterator …
                                Composite
                                Flyweight
```

**Prototype** — when constructing an object from scratch is expensive and you'll need many similar instances, clone an existing one instead of building from zero. Think Notion's **Duplicate** button on a page.

**Adapter** — when two interfaces don't match and you can't change either side (legacy code, a vendor SDK), slip a translator between them. Think the **travel power adapter** you use abroad: same electricity, different shape.

Both patterns are small. Both are easy to over-apply. Both have a Python-native shortcut that often makes the explicit pattern unnecessary (`dataclasses.replace` for Prototype, duck typing for Adapter). The skill is knowing **when to reach for them and when to skip them**.

---

## Recap from LLD-17 — Factory family

Three checks before we move on. The Factory family answered: *"Which concrete class do I instantiate?"* Today's first pattern asks a related but different question: *"What if construction is so expensive I don't want to do it twice?"*

### Quiz 1 — Which Factory variant?

> A food-delivery app needs to render a **themed checkout** per restaurant brand.
> - Three widgets: Header, Button, Toast.
> - Three brand themes: McDonald's (red-yellow), Starbucks (green-cream), Subway (green-yellow).
> - Brand can switch mid-session.
> - Invariant: all three widgets on screen share the same brand.

**Answer: Abstract Factory.** Each concrete factory (`McDFactory`, `StarbucksFactory`) produces a coordinated set of related products. Family consistency is the defining requirement.

```python
class BrandFactory(ABC):
    @abstractmethod
    def make_header(self) -> Header: ...
    @abstractmethod
    def make_button(self) -> Button: ...
    @abstractmethod
    def make_toast(self) -> Toast: ...

class McDFactory(BrandFactory):
    def make_header(self): return RedYellowHeader()
    def make_button(self): return RedYellowButton()
    def make_toast(self):  return RedYellowToast()

class StarbucksFactory(BrandFactory): ...

def render_checkout(f: BrandFactory):
    f.make_header().draw()
    f.make_button().draw()
    f.make_toast().draw()
```

Simple Factory returns one product at a time — nothing forces the three calls to share a brand. Factory Method defers *which subclass* per product — solves "extend with new types," not "keep families coherent." Builder assembles *one* complex object step-by-step — the three widgets here are independent peers.

### Quiz 2 — Which line does Factory Method eliminate?

```python
# Simple Factory
class NotificationFactory:
    @staticmethod
    def create(kind: str):
        if   kind == "email": return Email()
        elif kind == "sms":   return SMS()
        elif kind == "push":  return Push()
        raise ValueError(kind)
```

**Answer: the whole `if/elif` chain.** Simple Factory edits that chain every time a new product is added — that's an OCP violation. Factory Method flips this: each product gets its own subclass with a single `create()`, and adding a new product means a new subclass, never a touch to an existing class.

### Quiz 3 — Is `PointFactory.create(3, 4)` a sensible Factory?

```python
class PointFactory:
    @staticmethod
    def create(x: float, y: float) -> Point:
        return Point(x, y)
```

**Answer: no — classic over-engineered factory.** Factory earns its keep when there's a real decision the caller would otherwise have to make: which subclass, with which args, possibly cached, possibly validated. Wrapping a single constructor with one line of indirection adds a class, a static method, and a name to remember — and buys nothing. Just call `Point(3, 4)`.

---

## Pattern-selection warm-up

Before introducing today's two patterns, two scenarios that practise *picking the right tool from what you already know*.

### Pick the pattern: HTTP connection pool

> "A microservice's `HttpClient` wraps a connection pool. The pool is expensive to create (~300 ms) and the rest of the app must always use the same one, otherwise we leak sockets."

**Answer: Singleton.** Two clues both point there:
- *"the rest of the app must always use the same one"* — that's literally the Singleton guarantee.
- *"the pool is expensive to create"* + *"leak sockets if we don't"* — you want to pay the construction cost **once**.

```python
class HttpClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.pool = _make_pool()    # ~300 ms, runs ONCE
        return cls._instance

client = HttpClient()      # first call: builds the pool
again  = HttpClient()      # second call: returns the SAME instance
assert client is again
```

### Pick the pattern: SearchQuery with 12 filters

> "Constructing a `SearchQuery` object can mean any subset of 12 filters (price range, brand, rating, in-stock, free-delivery, …). The constructor takes 12 optional kwargs and call sites are unreadable."

**Answer: Builder.** Classic telescoping-constructor pain — Builder fixes it by making each setter a named fluent step.

```python
@dataclass(frozen=True)
class SearchQuery:
    price_min: int | None = None
    price_max: int | None = None
    brand:     str | None = None
    in_stock:  bool       = False
    # ... 8 more optional fields

class SearchQueryBuilder:
    def __init__(self): self._q = {}
    def price(self, lo, hi): self._q.update(price_min=lo, price_max=hi); return self
    def brand(self, b):      self._q["brand"] = b;                       return self
    def in_stock(self, v=True): self._q["in_stock"] = v;                 return self
    def build(self) -> SearchQuery: return SearchQuery(**self._q)

q = (SearchQueryBuilder()
        .price(0, 500)
        .brand("Nike")
        .in_stock(True)
        .build())
```

Singleton is wrong: every search is a fresh, ephemeral object. Factory Method via subclassing would explode (2¹² = 4096 combinations — one subclass each? no). Abstract Factory solves *family consistency*, not *"too many ways to configure one thing"*.

---

## Part 1 — Prototype

### 4.1 Prerequisite: the `copy` module

Prototype is built on top of copying objects. Before we look at the pattern, let's make sure four facts about `copy` are crisp.

#### Pre-question — why does `copy` exist?

Pretend the `copy` module doesn't exist. You have a `Cart` with `items` and `customer`. You want a second cart that's the same as the first **but independent**. Which "by-hand" duplication is actually correct?

```python
class Cart:
    def __init__(self, items, customer):
        self.items = items            # list[str]
        self.customer = customer      # dict[str, str]

c1 = Cart(items=["book"], customer={"name": "Jay"})

# A) c2 = c1
# B) c2 = Cart(c1.items, c1.customer)
# C) c2 = Cart(list(c1.items), dict(c1.customer))
# D) c2 = Cart.__new__(Cart); c2.__dict__ = c1.__dict__
```

**Answer: C.** And it's exactly what `copy.deepcopy` automates for you.

- **A** is aliasing — `c1` and `c2` are the **same** object.
- **B** allocates a new `Cart` but the inner `items` list and `customer` dict are still shared. Mutating `c2.items` bleeds into `c1.items`. *(This is what `copy.copy` does — "shallow" copy.)*
- **C** explicitly recreates the inner containers too. Fully independent.
- **D** copies the dict reference — same bug as A, dressed up.

That's the whole point of the `copy` module: it walks the reference graph and rebuilds new objects at every level so you don't have to remember to wrap every nested field. Without it, every prototype implementation would be a hand-rolled tour of every field. With it, one line: `copy.deepcopy(self)`.

> *We covered the `copy` module — shallow vs deep, the memo dict, picklable types — in **LLD-12 · Exception Handling, § copy & deepcopy**. The Prototype pattern is just "build the cheap-clone API on top of what you already know about `copy.deepcopy`."*

#### Shallow vs deep — the mental model

```python
import copy
original = {"name": "Ada", "skills": ["python", "go"]}
shallow  = copy.copy(original)
shallow["skills"].append("rust")
print(original["skills"])   # ['python', 'go', 'rust']  ← shared list!
```

A shallow copy makes **one level** of new object. Everything *inside* that object is still pointer-equal to the original. `original["skills"]` and `shallow["skills"]` are literally the same list, with two different dicts pointing at it.

```python
deep = copy.deepcopy(original)
deep["skills"].append("rust")
print(original["skills"])   # ['python', 'go']  ← untouched
```

Deep copy walks the entire reference graph, allocating a new object for every container it sees. Cost is O(total reachable objects); shallow is O(1).

You can customise per-class via the `__copy__(self)` and `__deepcopy__(self, memo)` dunder methods — we'll use this later to keep `clone()` cheap.

#### Manual deepcopy — what `copy.deepcopy` does for you

To make the magic concrete, here's `deepcopy` written by hand (omitting class registry support):

```python
def manual_deepcopy(obj, memo=None):
    if memo is None:
        memo = {}
    # Already cloned this object in the current walk? Return the cached clone.
    # This is what prevents cycles from looping forever.
    if id(obj) in memo:
        return memo[id(obj)]

    if isinstance(obj, dict):
        new = {}
        memo[id(obj)] = new          # register BEFORE recursing
        for k, v in obj.items():
            new[manual_deepcopy(k, memo)] = manual_deepcopy(v, memo)
        return new

    if isinstance(obj, list):
        new = []
        memo[id(obj)] = new
        for item in obj:
            new.append(manual_deepcopy(item, memo))
        return new

    # Immutable atoms (int/str/tuple of immutables) — safe to share
    return obj
```

The trick on line 4 / line 12: `memo[id(obj)] = new` happens **before** recursing into the children. If a child contains a reference back to `obj`, the recursive call finds it in `memo` and returns the half-built clone — that's how cycles (`a.peer = b; b.peer = a`) are handled without infinite loops.

`copy.deepcopy` adds a richer type registry (class instances via `__deepcopy__`, classes via `__reduce_ex__`) and battle-tested edge cases (file handles, weakrefs, sockets). The *idea* is identical: recursive walk, memo for cycles.

---

### 4.2 The problem — "building from scratch" is sometimes very expensive

**Case study — Notion's "Duplicate" button.** When you click *Duplicate* on a Notion page, a brand-new page appears in about ~200 ms — complete with all the same blocks, embeds, properties, formulas, and database views as the original. Imagine if Notion didn't have Duplicate and instead made you re-create the page from scratch every time. That's the difference between `clone()` and `__init__`.

**Jayendra is building an A/B test platform.** The setup mirrors Notion's Duplicate exactly. Every experiment starts from a `BaseConfig` that's expensive to build:

- pulls 200+ feature flags from a slow remote config service — **~400 ms**
- loads a per-tenant pricing table from the database — **~150 ms**
- warms an in-memory ML model that scores user segments — **~600 ms of CPU**

Total: **~1.2 seconds** per `BaseConfig()`. Each experiment needs a config that's **99% identical** to the baseline — just one or two flags flipped. The naive approach pays the 1.2 s tax 50 times:

```python
# Naive — rebuild from scratch every time
for experiment in experiments:               # 50 experiments
    cfg = BaseConfig()                       # 1.2 s each → 60 s total
    cfg.flags[experiment.flag] = experiment.value
    run_experiment(cfg)
```

60 s of cold-start work for what is essentially "change one byte." This isn't a hypothetical. Three flavours, each with the code that wins:

#### Heavy initial state — DB / Network

```python
class TenantConfig:
    def __init__(self, tenant_id):
        self.flags   = api.get(f"/flags/{tenant_id}")
        self.pricing = db.query("SELECT ...")
        self.limits  = redis.hgetall(f"limits:{tenant_id}")
    def clone(self):
        return copy.deepcopy(self)
```

#### Pre-computed in-memory data

An ML model warmed up, a cache populated, a graph built — cheap to copy, expensive to rebuild.

```python
class RecommenderState:
    def __init__(self):
        self.embeddings = _load_embeddings()  # 800 MB
        self.index = _build_ann_index(self.embeddings)
        self.user_clicks: list = []
    def __deepcopy__(self, memo):
        new = RecommenderState.__new__(RecommenderState)
        new.embeddings = self.embeddings    # SHARE the 800 MB
        new.index      = self.index
        new.user_clicks = []                # fresh per clone
        return new
```

#### Simulator / what-if branches

Each branch starts from "where we are now" and explores a variant.

```python
class ChessPosition:
    pieces: dict
    castling_rights: set
    def clone(self):
        return copy.deepcopy(self)

# Minimax — explore every candidate move on a clone
for move in position.legal_moves():
    branch = position.clone()
    branch.apply(move)
    score = minimax(branch, depth - 1)
```

**The shape of the problem:** we already *have* an object that's 99% what we need. Constructing one from scratch is expensive. What if we just **copied** it and changed the 1% that differs?

---

### 4.3 The pattern — `clone()` instead of `new`

> *Have every object that's expensive to construct expose a `clone()` method. To make a similar object, call `existing.clone()` — not the constructor.*

**GoF definition** (worth memorising):
> "Specify the kinds of objects to create using a prototypical instance, and create new objects by copying this prototype."

Two motivations the GoF spell out, beyond raw cost:

- **Avoid subclass explosion.** If variants differ only in *data* (a "fast-attack orc" vs a "slow-defend orc" with different HP/damage numbers), don't make a new subclass for each — clone a configured prototype.
- **The concrete type isn't known until runtime.** A game spawns whatever enemy the level config says; an editor spawns whatever shape the user clicks. The caller doesn't write `OrcWarrior()` — it looks up the prototype by name and clones it.

Rewriting Jayendra's loop with Prototype:

```python
import copy
from dataclasses import dataclass, field

@dataclass
class BaseConfig:
    flags: dict[str, bool] = field(default_factory=dict)
    pricing: dict[str, float] = field(default_factory=dict)
    segments: dict[str, list[str]] = field(default_factory=dict)

    def __init__(self):
        # Slow one-time setup — 1.2 s
        self.flags    = _load_flags_from_remote()
        self.pricing  = _load_pricing_from_db()
        self.segments = _warm_segment_model()

    def clone(self) -> "BaseConfig":
        return copy.deepcopy(self)         # < 1 ms

# --- usage ---
prototype = BaseConfig()                       # 1.2 s — pay once
for experiment in experiments:
    cfg = prototype.clone()                    # < 1 ms each
    cfg.flags[experiment.flag] = experiment.value
    run_experiment(cfg)
```

| Before | After (Prototype) |
|---|---|
| 50 × 1.2 s = **60 s** of construction | 1 × 1.2 s + 50 × ~1 ms = **~1.25 s** total |

The minimal Prototype interface is just one method:

```python
from abc import ABC, abstractmethod

class Prototype(ABC):
    @abstractmethod
    def clone(self) -> "Prototype": ...
```

In the GoF book ([Design Patterns (1994), Chapter 3 — Prototype, p.117](https://archive.org/details/designpatternsel00gamm/page/116/mode/2up)) this is a formal abstract class. In Python you almost never need the ABC — duck typing handles it — but the contract is the same: *every concrete Prototype answers `clone()`*.

#### Why is `clone()` ~1000× faster than `__init__`?

It's the difference between **re-computing** the data and **copying already-computed bytes**:

| Step | `BaseConfig()` — full constructor | `prototype.clone()` — deepcopy |
|---|---|---|
| Load 200 feature flags | HTTPS call to remote config service — **~400 ms** | Walk the in-memory dict, allocate a new one — **~0.2 ms** |
| Load pricing table | TCP DB roundtrip, query plan, row decode — **~150 ms** | Allocate new dict, copy ~100 entries — **~0.1 ms** |
| Warm segment model | Read weights from disk, build lookup tables — **~600 ms** | Allocate the same shape of dict/array — **~0.5 ms** |
| **Total** | **~1200 ms** | **~0.8 ms ≈ < 1 ms** |

Constructor does **I/O** — network calls (10s of ms each), disk reads (1+ ms), CPU compute. Each one is at least a thousand instructions plus a wait for a remote system.

`deepcopy` does **memory work only** — `malloc`, write bytes, repeat. Modern CPUs do tens of gigabytes of memory copies per second. A few dictionaries with a few hundred entries is a vanishingly small amount of work.

Constructor time goes to *fetching* data from somewhere far away. Clone time goes to *duplicating* data already in RAM. Same outcome, wildly different cost.

**Caveat:** when an object holds genuinely large in-memory data (a 1 GB tensor, a 100k-edge graph), `deepcopy` stops being < 1 ms — it grows with the data size. That's exactly when you override `__deepcopy__` to **share** the giant read-only piece instead of duplicating it. See `code/11_deepcopy_override_recipes.py`, Recipe 1.

#### The cost equation

> cost(`__init__`) **≫** cost(`deepcopy`) **AND** you'll need N similar objects

| Scenario | `__init__` cost | `deepcopy` cost | N | Verdict |
|---|---|---|---|---|
| Jayendra's A/B test config | ~1200 ms | ~1 ms | 50 | ✓ Prototype — saves ~58 s |
| Chess position in minimax | ~3 ms | ~0.05 ms | 10,000+/move | ✓ Prototype — 60× speedup |
| `Point(x, y)` | < 1 µs | < 1 µs | anything | ✗ Skip — constructor is already trivial |
| App-wide `HttpClient` | ~300 ms | n/a (sockets!) | exactly 1 | ✗ Skip — only one needed → *Singleton*, not Prototype |
| Notion "Duplicate page" | ~200 ms | ~5 ms | 1+ on demand | ✓ Prototype — 40× faster UX |

The pattern is a **tool to spend cheaply**, not a habit. Ask the inequality before you reach for it.

---

### 4.4 Variations

#### A. Shallow vs Deep clone

|  | `copy.copy` — shallow | `copy.deepcopy` — deep |
|---|---|---|
| What it does | New outer object, inner references shared | New outer object, every reachable object also copied |
| Speed | Fast (one allocation) | Slower (proportional to graph size) |
| Safe when | Inner objects are *immutable* (`str`, `tuple`, `frozenset`, numbers) | Inner objects are *mutable* and each clone needs to evolve independently |
| Trap | Mutating `clone.list` silently mutates `original.list` too | Can blow up on objects holding sockets, file handles, locks, DB connections |

When the default isn't right, override the hooks:

```python
class MLPredictor:
    def __init__(self):
        self.model   = _load_giant_model()       # 800 MB, READ-ONLY
        self.history = []                        # per-clone, mutable

    def __deepcopy__(self, memo):
        new = MLPredictor.__new__(MLPredictor)
        new.model   = self.model                # SHARE the model
        new.history = []                        # fresh per clone
        return new
```

By customising `__deepcopy__` you tell Python *"share what's safe to share, copy what must be independent."* This is the single biggest lever for keeping `clone()` cheap.

#### B. Prototype Registry

If callers ask for clones *by name* — "give me a fresh welcome-email", "give me the staging config", "spawn an enemy of type 'orc'" — wrap the prototypes in a registry:

```python
class PrototypeRegistry:
    def __init__(self):
        self._prototypes: dict[str, Prototype] = {}

    def register(self, name: str, proto: Prototype) -> None:
        self._prototypes[name] = proto

    def get(self, name: str) -> Prototype:
        return self._prototypes[name].clone()

# --- one-time setup ---
registry = PrototypeRegistry()
registry.register("welcome-email", EmailNotification(template="Welcome!", retry=3))
registry.register("alert-sms",    SMSNotification(template="Alert!",   retry=5))

# --- usage ---
msg = registry.get("welcome-email")          # fresh clone each time
msg.recipient = "riya@scaler.com"
```

This is what notification template systems, IDE "new file from template" menus, and game engines (spawn enemy by name) all look like under the hood.

#### C. Prototype meets Singleton

A subtle interview gotcha: **what happens if someone calls `copy.deepcopy(my_singleton)`?** By default, Python's reduce protocol routes through `cls.__new__(cls)` and then `__setstate__` — which silently overwrites your singleton's live state with a deep-copied snapshot. The "exactly one" guarantee survives identity, but the state is no longer trustworthy.

The fix is to plug into the copy protocol from inside the Singleton:

```python
class ConfigStore:                       # Singleton
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.flags = {}
        return cls._instance

    # Block clone attempts — both shallow and deep return the SAME instance
    def __copy__(self):           return self
    def __deepcopy__(self, memo): return self

s1 = ConfigStore()
s2 = copy.deepcopy(s1)
assert s1 is s2                          # Singleton invariant preserved ✓
```

**The lesson:** Singleton's "exactly one" is enforced by the constructor (`__new__`). The `copy` module bypasses the constructor entirely, so a class that wants to remain a Singleton must also guard the `__copy__`/`__deepcopy__` entry points. Same lesson as "Singleton must guard `pickle` too" — any backdoor that creates objects without calling `__new__` is a hole.

---

### 4.5 Pitfalls

#### Shallow copy shares mutable inner state

```python
import copy

class Cart:
    def __init__(self):
        self.items: list[str] = []

    def clone(self) -> "Cart":
        return copy.copy(self)            # shallow

template = Cart()
template.items.append("free-sample")
c1 = template.clone(); c1.items.append("book")
c2 = template.clone()
print(c2.items)   # ['free-sample', 'book']  ← all three share the same list
```

This is the #1 Prototype bug. `copy.copy` made new `Cart` wrappers, but they all hold a reference to *the same* `items` list. Fix: use `copy.deepcopy(self)`, or explicitly `new.items = list(self.items)`.

#### Runtime-state leak

You're building a game. `spawn_orc()` clones a prototype Orc. What's wrong with this code?

```python
@dataclass
class Orc:
    name: str
    max_hp: int = 100
    hp: int = 100                  # current HP, mutates during battle
    target: "Orc" | None = None    # whoever it's currently attacking

    def clone(self):
        return copy.deepcopy(self)

orc_proto = Orc(name="orc")
# ... mid-battle, the prototype somehow took 30 damage and got a target ...
orc_proto.hp = 70
orc_proto.target = some_player

new_orc = orc_proto.clone()
print(new_orc.hp, new_orc.target)  # 70, some_player
```

The clone is born **mid-battle**: `hp=70`, already aggro'd. The prototype is leaking **runtime state**, not just blueprint state. Two clean fixes:

1. **Separate template from instance** — keep the prototype on a shelf, never let game code mutate it.
2. **Reset on clone:**
   ```python
   def clone_fresh(self):
       new = self.clone()
       new.hp = new.max_hp
       new.target = None
       return new
   ```

Same pitfall hits ML "pretrained model" clones (training state leaks), HTTP "session template" clones (auth cookies leak), and database "connection template" clones (transaction state leaks).

#### Prototype is overkill for simple immutable dataclasses

You have a frozen `@dataclass` with five primitive fields and want a copy with one field changed. **Use `dataclasses.replace()`** — one line, no clone method, no copy module, no extra class:

```python
@dataclass(frozen=True)
class PageRequest:
    url: str
    method: str = "GET"
    timeout: float = 5.0

base = PageRequest(url="https://scaler.com")
long_timeout = replace(base, timeout=30.0)
a_post = replace(base, method="POST")
```

Reach for explicit `clone()` when the object is mutable, expensive to build, holds non-trivial state, or you want the registry idiom. **Don't ceremonially apply Prototype to every data class.**

---

### 4.6 UML & 4-step recipe

```
                  <<interface>>
                   Prototype
                  +-----------+
                  | clone()   |
                  +-----------+
                        △
              ___________|___________
             |                       |
        ConcretePrototypeA       ConcretePrototypeB
        +-----------------+      +-----------------+
        | field1, field2  |      | fieldA, fieldB  |
        +-----------------+      +-----------------+
        | clone()         |      | clone()         |
        +-----------------+      +-----------------+

        Client ────uses────→ Prototype.clone()
                            (knows only the interface, not the concrete class)
```

In Python you can drop the formal `Prototype` interface — duck typing means any class that defines `clone()` qualifies.

**4-step recipe to implement Prototype:**

1. **Identify the expensive class.** Its `__init__` takes meaningful time and the rest of the code wants many similar-but-tweaked instances.
2. **Add a `clone(self)` method.** Default body: `return copy.deepcopy(self)`.
3. **Decide what to share vs independently copy.** Expensive read-only data (an ML model, a parser table)? Override `__deepcopy__` to share it. OS resources (sockets, file handles)? `clone()` is the wrong pattern entirely — rethink.
4. **(Optional) Wrap with a registry** if callers ask for clones by name (`registry.get("welcome-email")`).

---

### 4.7 When Prototype earns its keep

| ✅ Use Prototype when | ❌ Skip Prototype when |
|---|---|
| Construction is genuinely **expensive** (DB, network, heavy compute) | Constructor is fast — just call it |
| You'll need **many similar** instances at runtime | Object holds OS resources or external state |
| Object state is mostly *data* — no sockets, no file handles, no locks | It's a simple `@dataclass` — use `dataclasses.replace()` |
| You want to clone "by name" (registry pattern) | You only need one or two instances total |

---

## Part 2 — Adapter

### 5.1 Before the code — the travel adapter you already know

**The world has 15 different electrical socket shapes.** An Indian Type-D socket has three round pins. A US Type-B has two flat pins + a round ground. A UK Type-G has three big rectangular pins with a fuse. Visit any of these countries with a laptop charger built for another and your plug literally will not fit the wall. Watts, volts, current — all fine. **The shapes don't match.**

**Why hasn't the world standardised on one socket?**

- **Path dependence.** Each country electrified between ~1890 and ~1960 with the tech and patents of its day. Once 100 million homes are wired, switching is impossibly expensive.
- **Voltage / frequency differs too** (110 V/60 Hz in the US, 230 V/50 Hz in India), so the socket shape doubles as a "this socket is the right voltage for the plug" key.
- **Local safety standards diverged.** The UK Type-G has a built-in fuse and longer earth pin. India's Type-D doesn't. Each country's standard reflects its own historical preferences.

**The traveller's solution — a universal travel adapter.** It speaks Type-D to the wall (three round pins on one side) and accepts a Type-B plug (two flat slots + ground on the other). Two incompatible interfaces, neither modified. A third thing in the middle translates the shape — only the shape, not the electricity.

**That's exactly what the software Adapter pattern does:** two systems with non-matching interfaces, neither of which can be modified, with a small wrapper in the middle that *reshapes the calls* — not the data — so the two sides can talk. The wrapper is so simple that you've used dozens of physical ones; the software version is the same idea, in code.

---

### 5.2 Prerequisites: duck typing + composition

Adapter is the canonical "composition over inheritance" pattern. Two quick checks.

#### Duck typing — Python vs Java

> *"If it walks like a duck and quacks like a duck, it's a duck."*

Python doesn't care whether your object inherits from a base class or implements a formal interface — only whether `obj.method(...)` works at runtime.

```python
def make_it_quack(thing):
    return thing.quack()

class Duck:
    def quack(self): return "Quack!"

class Person:                     # no inheritance, no interface declared
    def quack(self): return "I'm imitating a duck"

class Dog:
    def bark(self): return "Woof"

make_it_quack(Duck())     # "Quack!"          works
make_it_quack(Person())   # "I'm imitating..." works
make_it_quack(Dog())      # AttributeError at RUNTIME
```

Compare with Java — the same idea would need an interface:

```java
interface Quackable { String quack(); }
class Duck   implements Quackable { public String quack() { return "Quack!"; } }
class Person implements Quackable { public String quack() { return "..."; } }
class Dog { public String bark() { return "Woof"; } }

static void makeItQuack(Quackable t) { System.out.println(t.quack()); }
makeItQuack(new Dog());   // won't even COMPILE — Dog doesn't implement Quackable
```

**Why this matters for Adapter:** in Java, an Adapter must `implements TargetInterface` — the wrapper class must be declared as the right type, by name, at compile time. In Python, the wrapper just needs *the right methods*. That's why all the GoF Adapter UML — with its explicit "implements Target" arrows — looks heavier than the equivalent Python code.

#### Composition over inheritance

When class B *inherits* from class A, B is permanently glued to A's interface, A's lifecycle, and A's internals — future changes to A ripple into B. When class B *holds* an A as a field, the coupling is just one method call.

| Inheritance — brittle | Composition — flexible |
|---|---|
| ```python\nclass EmailNotifier(SMTPClient):\n    def notify(self, user, msg):\n        self.send(user.email, msg)\n``` | ```python\nclass EmailNotifier:\n    def __init__(self, client):\n        self._client = client   # HAS-A\n    def notify(self, user, msg):\n        self._client.send(user.email, msg)\n``` |
| Exposes ALL of SMTPClient's methods (connect, quit, helo, ...). Callers can do `email.quit()`. If SMTP renames `send()`, EmailNotifier silently breaks. | Only `notify()` is public. Swap SMTPClient for SendgridClient by passing a different object — zero changes to EmailNotifier or its callers. Tests pass a MockClient. |

Adapter formalises the right side: *"hold the foreign object as a private field; expose only the interface you want."*

---

### 5.3 The problem — two interfaces that just don't match

#### Why this problem keeps happening — the SDK reality

Modern services pull in **5–15 third-party SDKs** across categories:

- Payments — Stripe, Razorpay, PayPal
- Storage — S3, GCS, Azure Blob
- Messaging — Twilio, MSG91, AWS SNS
- Auth — Auth0, Cognito, Firebase
- Analytics — Segment, Mixpanel, Amplitude
- Email — SendGrid, SES, Postmark

Each SDK is a complete world — *different client class, different auth model, different error types, different data shapes, different naming conventions.* **None of those worlds agree.**

**Why companies use multiple SDKs for the same job:**

- **Region** — Razorpay in India, Stripe in the US, PayPal in Europe.
- **Cost** — small transactions via the cheap provider, big ones via the reliable one.
- **Reliability** — when the primary goes down, fall over to the secondary.
- **Feature gaps** — SDK A supports recurring billing, SDK B supports UPI.

Every grown-up backend ends up with a layer of **in-house interfaces** (`PaymentGateway`, `CloudStorage`, `NotificationChannel`) that hide the vendor differences from the rest of the code. Adapter is the pattern that builds that quarantine layer.

```
                        Application code
                  (knows only IN-HOUSE interface)
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
          Adapter 1         Adapter 2         Adapter 3
              │                 │                 │
          Stripe SDK        Razorpay SDK      PayPal SDK
          (vendor 1)        (vendor 2)        (vendor 3)
```

#### Ragu's checkout system

**Ragu inherited a checkout system.** The team's payment code is uniform — every gateway implements:

```python
class PaymentGateway(ABC):
    @abstractmethod
    def pay(self, amount: float, currency: str) -> PaymentResult: ...
```

Now Marketing wants to add **Razorpay**. The Razorpay SDK is non-negotiable — pip-installed, with its own interface:

```python
# razorpay_sdk.py — pip-installed, untouchable
class RazorpayClient:
    def __init__(self, api_key: str, api_secret: str): ...
    def create_order(self, amount_in_paise: int, receipt_id: str) -> dict: ...
    def capture_payment(self, order_id: str) -> dict: ...
```

Three mismatches:

1. **Method name** — `pay()` vs `create_order()` + `capture_payment()`
2. **Units** — `amount: float` (rupees) vs `amount_in_paise: int` (paise = rupees × 100)
3. **Return type** — a `PaymentResult` object vs a raw `dict`

Ragu has three bad options and one good one:

| Approach | Why it breaks |
|---|---|
| 🚫 **Fork the SDK** and rename methods | You own every Razorpay upgrade forever. Their next breaking change becomes your maintenance work. Security patches lag your fork. |
| 🚫 **Edit the checkout system** with `if gateway == "razorpay": ...` everywhere | Vendor-specific shapes spread through dozens of files. Adding PayPal next quarter means doing it all again. |
| 🚫 **Subclass `RazorpayClient`** | Inheritance ties you to *their* class. Plus you've leaked all of their public methods into your type — callers can sidestep your `pay()` and reach the raw SDK. |
| 🔌 **Adapter** | A small wrapper class that *holds* a `RazorpayClient` and exposes the `PaymentGateway` interface. Translates calls in one place. |

---

### 5.4 Case study — refactoring `restaurant_project/payments/views.py`

> *In an earlier session we built `restaurant_project/payments/views.py` together — it works, but the file even has a comment from past-me saying "this should be refactored with a `PaymentGateway` interface in a later session." Today is that session.*

Three concrete code smells from that file:

```python
# restaurant_project/payments/views.py — today
import razorpay

# SMELL 1: Razorpay is hardcoded at MODULE IMPORT TIME.
#          Want to A/B test Stripe? Want to use a stub in tests?
#          You can't — every import of this module wires Razorpay.
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_payment_link(request):
    ...
    # SMELL 2: Razorpay-shaped dict bled into the VIEW function.
    link_data = client.payment_link.create({
        "amount": amount_paise,        # Razorpay's vocabulary: paise, not rupees
        "currency": "INR",
        "customer": { ... },
        "notify":   {"sms": True, "email": True},
        ...
    })
    # SMELL 3: Razorpay's name leaks into our Payment MODEL field names.
    payment.razorpay_payment_link_id = link_data["id"]
    payment.save()

def razorpay_webhook(request):           # ← URL name + handler both branded
    event = json.loads(request.body)
    if event["event"] == "payment_link.paid":              # Razorpay's event vocab
        payment_link = event["payload"]["payment_link"]["entity"]
        ...
```

**What it costs in practice:**

- Want to add Stripe? You're editing `views.py`, `models.py` (new Stripe fields), `urls.py` (new webhook URL), and every other file that mentions `razorpay_payment_link_id`.
- Want to unit-test the checkout flow? You can't — `razorpay.Client(...)` at module import means even importing the module hits the network.
- Razorpay v2 renames `payment_link` → `payment_links`? You hunt through every file.

**The Adapter refactor:**

```python
# payments/gateways/base.py — IN-HOUSE interface (no vendor mention)
@dataclass(frozen=True)
class PaymentLink:
    provider_link_id: str
    short_url: str
    amount_paise: int

class PaymentGateway(ABC):
    @abstractmethod
    def create_payment_link(self, *, amount_paise, order_id,
                            customer_name, customer_email, customer_phone,
                            description, callback_url) -> PaymentLink: ...
    @abstractmethod
    def verify_webhook(self, payload: bytes, signature: str) -> bool: ...

# payments/gateways/razorpay_adapter.py — vendor SDK quarantined HERE
import razorpay

class RazorpayGateway(PaymentGateway):
    def __init__(self, key_id, key_secret, webhook_secret):
        self._client = razorpay.Client(auth=(key_id, key_secret))
        self._webhook_secret = webhook_secret

    def create_payment_link(self, **kwargs) -> PaymentLink:
        link = self._client.payment_link.create({
            "amount":   kwargs["amount_paise"],
            "currency": "INR",
            ...
        })
        return PaymentLink(
            provider_link_id=link["id"],
            short_url=link["short_url"],
            amount_paise=kwargs["amount_paise"],
        )

# payments/views.py — now provider-agnostic
def create_payment_link(request):
    gateway = get_gateway()                # the only "which vendor?" decision
    link = gateway.create_payment_link(amount_paise=..., order_id=..., ...)
    payment.provider_link_id = link.provider_link_id   # vendor-NEUTRAL field
    payment.save()
    return JsonResponse({"url": link.short_url})
```

**What the refactor unlocks:**

- `Payment` field `razorpay_payment_link_id` → `provider_link_id` (vendor-neutral). A future migration to Stripe doesn't rename DB columns.
- `razorpay_webhook` URL+handler → `payment_webhook` + per-provider `parse_webhook_event`. Same URL serves Razorpay today, Stripe tomorrow.
- Tests inject a `FakeGateway()` instead of monkey-patching `razorpay.Client`. The whole checkout flow tests in 5 ms with no network.
- `razorpay.Client(...)` is no longer called at module import. The Django app starts even if Razorpay's keys are unset (useful in CI).

A runnable, self-contained version of this refactor lives in [`code/12_django_payments_adapter_refactor.py`](./code/12_django_payments_adapter_refactor.py) — including a unit test the original code couldn't have written.

---

### 5.5 The pattern — Object Adapter via composition

Three roles to name:

```
   Target  ────uses────  Adapter  ────wraps────  Adaptee
   (interface client      (implements Target,    (existing object with
    expects)              holds Adaptee)         "wrong" interface)
```

The Adapter speaks two languages: Target's outward, Adaptee's inward.

```python
from razorpay_sdk import RazorpayClient

class RazorpayAdapter(PaymentGateway):
    # 1. Hold the Adaptee (composition)
    def __init__(self, api_key: str, api_secret: str):
        self._client = RazorpayClient(api_key, api_secret)

    # 2. Implement the Target interface
    def pay(self, amount: float, currency: str) -> PaymentResult:
        # 3. Translate the call
        amount_in_paise = int(amount * 100)
        receipt = _new_receipt_id()
        order   = self._client.create_order(amount_in_paise, receipt)
        result  = self._client.capture_payment(order["id"])
        return PaymentResult(
            success      = result["status"] == "captured",
            txn_id       = result["id"],
            raw_response = result,
        )
```

Now do the **exact same thing for Stripe** — same Target interface, completely different vendor SDK. Notice the parallel structure with Razorpay's adapter:

```python
import stripe   # Stripe's SDK speaks module-level config + one-shot Charge.create

class StripeAdapter(PaymentGateway):
    # 1. Hold the Adaptee (composition)
    def __init__(self, api_key: str):
        stripe.api_key = api_key             # Stripe SDK uses module-level config
        self._stripe = stripe                # keep the handle behind a private field

    # 2. Implement the Target interface — same shape as RazorpayAdapter.pay
    def pay(self, amount: float, currency: str) -> PaymentResult:
        # 3. Translate the call
        amount_in_cents = int(amount * 100)            # dollars → cents (similar to paise)
        charge = self._stripe.Charge.create(           # one-shot, not the order+capture flow
            amount   = amount_in_cents,
            currency = currency.lower(),               # Stripe wants "usd", not "USD"
            source   = "tok_visa",                     # test token; real call passes user's token
        )
        return PaymentResult(
            success      = charge["status"] == "succeeded",  # Razorpay says "captured", Stripe says "succeeded"
            txn_id       = charge["id"],
            raw_response = charge,
        )
```

**What's the same vs what differs between the two adapters?**

|  | RazorpayAdapter | StripeAdapter |
|---|---|---|
| **Same** | Implements `PaymentGateway`, holds vendor SDK as private field, exposes only `pay()` | Same |
| **Auth model** | `RazorpayClient(api_key, api_secret)` — instance constructor | `stripe.api_key = ...` — module-level global |
| **Method shape** | Two calls: `create_order()` then `capture_payment()` | One call: `Charge.create()` |
| **Unit name** | rupees → paise | dollars → cents |
| **Success field** | `result["status"] == "captured"` | `charge["status"] == "succeeded"` |

The *interface mismatch* between Stripe and our codebase is completely different from the one between Razorpay and our codebase — but the *cost of bridging* it is the same: ~15 lines in one adapter file. That's what makes Adapter such a high-leverage pattern. Every new vendor is a single file, no other code changes.

From the rest of the codebase's point of view, both Razorpay and Stripe are now just `PaymentGateway`:

```python
# existing code — zero changes
def checkout(gateway: PaymentGateway, amount: float, currency: str):
    result = gateway.pay(amount, currency)
    if result.success:
        send_confirmation(result.txn_id)

# Same call site, swap one constructor:
checkout(RazorpayAdapter(KEY, SECRET), 499.00, "INR")     # via Razorpay
checkout(StripeAdapter(STRIPE_KEY),    59.99,  "USD")     # via Stripe
```

🎯 The Adapter does **three jobs** in one class: rename methods, convert units, translate return shapes. The mismatch is contained in *one file*.

**Why Adapter is "structural":** Creational patterns answer *"how do I make this object?"* Structural patterns answer *"how do I compose objects so they fit together?"* Adapter is the first — and simplest — member of the structural family: it changes nothing about *what* the wrapped object is, only about *how it's accessed*.

---

### 5.6 Variations

#### Object Adapter vs Class Adapter

|  | Object Adapter (composition) | Class Adapter (inheritance) |
|---|---|---|
| Mechanism | Adapter *holds* an Adaptee instance | Adapter *inherits* from both Target and Adaptee |
| Translation | Delegates: `self._adaptee.foo()` | Calls inherited: `self.foo()` |
| Can adapt subclasses? | Yes — any Adaptee subclass works | No — tied to one specific class |
| Multiple inheritance needed? | No | Yes — brittle when Adaptee has its own bases |
| Idiomatic in Python? | ✅ Yes — what you'll see in real code | ❌ Rarely — multiple inheritance is a code smell here |

A class adapter would look like this — you *can* write it, but you usually shouldn't:

```python
class RazorpayClassAdapter(PaymentGateway, RazorpayClient):    # multi-inheritance
    def pay(self, amount, currency):
        amount_in_paise = int(amount * 100)
        order  = self.create_order(amount_in_paise, _new_receipt_id())
        result = self.capture_payment(order["id"])
        return PaymentResult(...)
```

Drawback: `RazorpayClassAdapter` now exposes *every* public method of `RazorpayClient` too — `create_order()`, `capture_payment()`, etc. — leaking the Adaptee's surface to the world. Object adapter hides it cleanly.

#### Two-Way Adapter

An adapter that implements *both* interfaces, so calls can flow in either direction. The most famous everyday example is a **currency converter in a form**:

```python
class USDINRPriceField:
    # Speaks USD to "set from USD input"; speaks INR to "set from INR input".
    def __init__(self, rate: float):
        self._usd: float = 0.0
        self._rate = rate

    # direction 1: someone types USD → expose INR
    def set_usd(self, usd):
        self._usd = usd
    def get_inr(self) -> float:
        return self._usd * self._rate

    # direction 2: someone types INR → expose USD
    def set_inr(self, inr):
        self._usd = inr / self._rate
    def get_usd(self) -> float:
        return self._usd
```

Mostly a curiosity in Python — almost always the right answer is two one-way adapters, not one two-way. But naming it in an interview signals you've actually read the GoF chapter.

---

### 5.7 Adapter in the wild

You've already used Adapter without knowing it.

#### `io.StringIO` / `io.BytesIO` — strings as files

Any function that takes a file-like object (`.read()`, `.write()`, `.seek()`) can be tested with an in-memory string. `StringIO` is an Adapter: **Target** = file-like interface, **Adaptee** = a `str`.

```python
from io import StringIO

buffer = StringIO()
export_csv(rows, buffer)             # writes "as if" to a file
csv_text = buffer.getvalue()         # pull the string back out
```

#### Django auth backends

Django defines a Target interface for authentication: `authenticate(request, **credentials) → User | None`. To plug in LDAP, OAuth, SAML, or your custom SSO, you write an auth backend class implementing that interface while internally calling the LDAP / OAuth / SAML library.

```python
from django.contrib.auth.backends import BaseBackend       # the Target
from django.contrib.auth.models   import User
import ldap                                                # the Adaptee

class LDAPBackend(BaseBackend):                             # the Adapter
    def authenticate(self, request, username=None, password=None):
        conn = ldap.initialize("ldaps://corp.example.com")
        try:
            conn.simple_bind_s(_user_dn(username), password)
        except ldap.INVALID_CREDENTIALS:
            return None
        user, _ = User.objects.get_or_create(username=username)
        return user

# settings.py
AUTHENTICATION_BACKENDS = ["myapp.auth.LDAPBackend"]
```

#### SQLAlchemy database dialects

SQLAlchemy presents one uniform Python API for Postgres, MySQL, SQLite, Oracle, MSSQL. Each underlying database has its own driver. The "dialect" classes are Adapters: **Target** = SQLAlchemy's expected DB-API, **Adaptee** = the actual driver.

```python
postgres = create_engine("postgresql+psycopg2://u:p@host/db")  # → PostgresqlDialect wraps psycopg2
mysql    = create_engine("mysql+pymysql://u:p@host/db")        # → MySQLDialect wraps PyMySQL
sqlite   = create_engine("sqlite:///local.db")                 # → SQLiteDialect wraps stdlib sqlite3

# Identical code on top of each — the dialect (Adapter) hides the driver's quirks.
for engine in (postgres, mysql, sqlite):
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT id, name FROM users WHERE id = :id"),
                            {"id": 42}).all()
```

#### Game controllers — Xbox / PS / Switch behind one `InputDevice`

```python
class InputDevice(ABC):
    @abstractmethod
    def get_axis(self, name: str) -> float: ...    # -1.0 to +1.0
    @abstractmethod
    def get_button(self, name: str) -> bool: ...

class XboxAdapter(InputDevice):
    def __init__(self):
        self._hid = xinput.open()        # Microsoft's XInput SDK
    def get_axis(self, name):
        state = xinput.get_state(self._hid)
        return {"lx": state.thumb_lx / 32768, ...}[name]

class DualSenseAdapter(InputDevice):     # PS5 — totally different SDK
    def __init__(self):
        self._hid = hid.Device(vid=0x054c, pid=0x0ce6)
    def get_axis(self, name): ...        # parse raw HID report bytes

# Same game loop, any controller
def update_player(player, device: InputDevice):
    player.move(device.get_axis("lx"), device.get_axis("ly"))
    if device.get_button("A"): player.jump()
```

#### Cloud storage — S3 vs GCS vs Azure Blob

A backend storing user uploads picks more than one cloud — primary on AWS, DR on GCP, or different clouds per customer for compliance. Each SDK speaks a different dialect:

|  | Upload method | Container term | Generate URL |
|---|---|---|---|
| AWS S3 (`boto3`) | `put_object(Bucket, Key, Body)` | Bucket | `generate_presigned_url` |
| GCS (`google-cloud-storage`) | `blob.upload_from_string(data)` | Bucket → Blob | `blob.generate_signed_url` |
| Azure Blob | `upload_blob(name, data)` | Container | `generate_blob_sas` |

In-house `CloudStorage` interface stays uniform:

```python
class CloudStorage(ABC):
    @abstractmethod
    def upload(self, path: str, data: bytes) -> None: ...
    @abstractmethod
    def get_signed_url(self, path: str, expires_in: int) -> str: ...

class S3Adapter(CloudStorage):       # wraps boto3
    ...
class GCSAdapter(CloudStorage):      # wraps google-cloud-storage
    ...
class AzureBlobAdapter(CloudStorage): # wraps azure-storage-blob
    ...
```

The application never imports `boto3` directly — only the adapter file does. Switching providers = swap the adapter import.

---

### 5.8 Pitfalls

#### Leaky adapter — public client field

What's wrong with this adapter?

```python
class RazorpayAdapter(PaymentGateway):
    def __init__(self, key, secret):
        self.client = RazorpayClient(key, secret)   # PUBLIC field

    def pay(self, amount, currency):
        ...

# Elsewhere in the codebase:
adapter = RazorpayAdapter(K, S)
adapter.client.create_order(5000, "r1")            # reaching past the Adapter
```

The Adapter leaks the Adaptee — callers now depend on Razorpay's API directly, defeating the abstraction. Mark the field private (`_client`) so the only entry point stays `pay()`. If a caller genuinely needs functionality the Target interface doesn't expose, the right answer is to *add a method to the Target interface*, not to reach around.

#### Over-adaptation — no real mismatch

Which of these is *not* a job for Adapter?

> "The new payment gateway is faster — we want to switch all payments to it."

That's just a refactor. If both gateways already implement `PaymentGateway`, no Adapter needed. The trigger for Adapter is "*interfaces don't match*", not "*we want to switch*."

Adapter rule of thumb:

| Situation | Adapter? |
|---|---|
| Same interface, want to swap | No (refactor / DI) |
| Different interfaces, both fixed | **Yes — this is Adapter** |
| Different interfaces, one is mine | Just edit my side |
| Same interface, want extra behaviour | Decorator |

---

### 5.9 Production conventions

#### 1. Translate exceptions, not just methods

A leaky exception type is just as bad as a leaky method. If your adapter lets `razorpay.errors.SignatureVerificationError` propagate, callers now `except razorpay.errors.SignatureVerificationError` — and you've leaked Razorpay into the rest of the codebase.

**Bad — method names translated, exceptions NOT:**

```python
# payments/razorpay_adapter.py
class RazorpayAdapter(PaymentGateway):
    def pay(self, amount, currency):
        order  = self._client.order.create({"amount": int(amount * 100), "currency": "INR"})
        return self._client.payment.capture(order["id"])
        # ← no try/except. If Razorpay raises, the exception flies up unchanged.

# checkout/views.py — caller is forced to know Razorpay exists
import razorpay.errors                                         # ❌ leaked

def checkout(request):
    try:
        gateway.pay(amount, "INR")
    except razorpay.errors.SignatureVerificationError:          # ❌
        return JsonResponse({"error": "auth"}, status=401)
    except razorpay.errors.BadRequestError:                     # ❌
        return JsonResponse({"error": "bad request"}, status=400)
```

The same `except` blocks now appear in `billing.py`, `webhooks.py`, `subscriptions.py`. Razorpay's exception classes are part of your codebase's contract.

**Good — map vendor exceptions to your own at the adapter boundary:**

```python
class PaymentError(Exception): ...
class AuthFailed(PaymentError): ...
class InsufficientFunds(PaymentError): ...

class RazorpayAdapter(PaymentGateway):
    def pay(self, amount, currency):
        try:
            ...
        except razorpay.errors.SignatureVerificationError as e:
            raise AuthFailed(str(e)) from e
        except razorpay.errors.BadRequestError as e:
            raise InsufficientFunds(str(e)) from e
        except razorpay.errors.RazorpayError as e:
            raise PaymentError(str(e)) from e
```

Callers only `except PaymentError`. Vendor doesn't leak. `raise X from e` preserves the original cause for debugging.

#### 2. Pair Adapter with Factory — transparent vendor selection

A real checkout doesn't hard-code which gateway to use. A factory reads config and hands out the right object — sometimes a native `PaymentGateway`, sometimes an Adapter — *transparently*:

```python
class PaymentGatewayFactory:
    @staticmethod
    def create(kind: str) -> PaymentGateway:
        if   kind == "stripe":   return StripeGateway()              # native impl
        elif kind == "razorpay": return RazorpayAdapter(KEY, SECRET) # Adapter around SDK
        elif kind == "paypal":   return PayPalGateway()              # native impl
        raise ValueError(kind)

# Caller never knows which ones are adapters — that's the point.
gateway = PaymentGatewayFactory.create(settings.payment_provider)
gateway.pay(499.0, "INR")
```

This is the canonical "two patterns playing together" that interviewers love to drill on: **Adapter** makes the foreign SDK look native, **Factory** picks which one to hand back. Today's call uses Stripe natively; tomorrow's a Razorpay adapter; the caller never knows.

---

### 5.10 When Adapter earns its keep

| ✅ Use Adapter when | ❌ Skip Adapter when |
|---|---|
| Two interfaces *must* work together but don't match | You control both interfaces — just change one |
| You can't (or don't want to) modify either side | The mismatch is one method renaming — a free function will do |
| You want to **contain** a third-party dependency in one file | The "Adapter" is just relaying every call unchanged — you've built a useless wrapper |
| You're plugging multiple vendors behind one in-house interface (payment gateways, auth providers, analytics) | The thing you're wrapping is already trivial to use directly |

---

## Compare — Adapter vs the rest of the structural family

In interviews the trap is that all four structural patterns look *structurally* identical — one class holds another and forwards calls. The pattern names refer to **why** the wrapping exists, not how it's coded.

| Pattern | Intent (one sentence) | Wrapped's interface | Wrapper's interface |
|---|---|---|---|
| **Adapter** | Make an existing object usable where a *different* interface is expected | Old / incompatible | The Target interface (different from the wrapped one) |
| **Decorator** | Add behaviour (logging, caching, auth) *around* an object without changing it | Some interface X | Same interface X, plus extra behaviour |
| **Proxy** | Stand in for an object — control access, lazy-load, or remote-call it | Some interface X | Same interface X (transparent stand-in) |
| **Facade** | Hide a complex subsystem behind one simple front-door API | Many objects with many interfaces | A small, simpler new interface |

**The litmus test — one question to disambiguate them:**

- **Does the wrapper change the interface?** → *Adapter* (yes, to a different one) or *Facade* (yes, to a simpler one).
- **Does the wrapper keep the same interface?** → *Decorator* (yes, to add behaviour) or *Proxy* (yes, to control access).

In interviews, lead with the intent (*"I'd use Adapter here because their interface doesn't match ours"*) — never with the code structure (*"it's a class that holds another class"*). Every structural pattern looks like that.

---

## Cross-family — Factory vs Adapter vs Strategy

The previous table compared Adapter against the rest of the structural family. But the interview follow-up is usually cross-family: *"Why not Factory? Why not Strategy?"*

Boil each pattern down to **one question**:

| Pattern | Family | The one question it answers | Example |
|---|---|---|---|
| **Factory** | Creational | **WHAT** to create? | "Stripe or Razorpay or PayPal?" → pick a concrete `PaymentGateway` |
| **Adapter** | Structural | **HOW to make it compatible** with my interface? | "Razorpay speaks `create_order`; I want `pay()`" → translate calls |
| **Strategy** | Behavioural | **HOW** to do the same job in different ways? | "Sort by price vs by rating vs by date" → swap the sorting algorithm |

The same domain can need all three, and they don't compete — they compose.

**File export — all three at once:**

- **Factory** — "Which exporter object should I hand back?" → `ExporterFactory.create("pdf") → PDFExporter()`
- **Adapter** — "Our `Exporter` wants `export(rows)`; ReportLab wants `build([Paragraph, Table, ...])`." → `PDFExporter(Exporter) wraps reportlab.platypus`
- **Strategy** — "Should the exporter sort by date or by amount before writing?" → `exporter.set_sort_strategy(SortByDate())`

**Interview heuristic:**
- If the question starts with *"which class do I make?"* → Factory.
- If it starts with *"how do I make these two talk?"* → Adapter.
- If it starts with *"how do I let the user swap the algorithm?"* → Strategy.

Different questions, different patterns, different families — even when the supporting cast (interface + concrete classes) looks the same on paper.

---

## Summary mindmap

### 🧬 Prototype — *creational* — "clone, don't construct"

- **Use when:** construction is expensive & you'll need many similar objects
- **Core API:** `clone()` on every prototype-able class
- **Python tools:** `copy.copy` (shallow) · `copy.deepcopy` (deep) · `__copy__` / `__deepcopy__` dunders
- **Variations:** Shallow vs Deep · Prototype Registry (clone by name) · Singleton∩Prototype guard
- **Skip when:** simple `@dataclass` (use `dataclasses.replace`) · constructor is fast · object holds OS resources
- **#1 bug:** shallow copy shares mutable inner state → one clone's edit pollutes the others

### 🔌 Adapter — *structural* — "wrap incompatible interfaces"

- **Use when:** two interfaces must work together but don't match; you can't change either
- **Three roles:** Target (interface client expects) · Adaptee (existing object) · Adapter (implements Target, holds Adaptee)
- **Variations:** Object Adapter (composition — idiomatic) vs Class Adapter (multiple inheritance — rarely worth it) · Two-Way Adapter
- **Real-world:** `StringIO` / `BytesIO` · Django auth backends · SQLAlchemy dialects · payment gateway wrappers · cloud storage abstractions
- **Skip when:** you control both interfaces · the mismatch is one rename (just rename it)
- **#1 bug:** leaking the Adaptee (public `self.client` field) — callers reach past the wrapper

### 🎯 Structural cheat — "which wrapper pattern?"

- Interface changes → **Adapter** (translate) or **Facade** (simplify many → one)
- Interface stays the same → **Decorator** (add behaviour) or **Proxy** (control access)

---

## Interview cheat sheet

**If asked "when would you use Prototype?":** lead with the cost equation — *expensive constructor + many similar instances needed*. Mention `copy.deepcopy` and the shallow-vs-deep trap. Bonus points: mention that `dataclasses.replace` is often what you actually want in Python.

**If asked "when would you use Adapter?":** lead with the mismatch — *two interfaces, neither under your control*. Mention composition (object adapter) over inheritance. Bonus points: name a real-world example (`StringIO`, Django auth backend, payment gateway wrapper).

**If asked "Adapter vs Decorator vs Proxy vs Facade":** don't talk about code — talk about *intent*. All four wrap. The pattern name says *why*.

**If asked "why not Factory / Strategy here?":** boil each to its one question (WHAT to create / HOW to do same job differently / HOW to make compatible) and show which one matches the scenario's verb.

---

## Code companions

All 12 files in [`code/`](./code/) are self-contained and runnable with no dependencies — just `python3 <file>`.

| File | What it demonstrates |
|---|---|
| [`01_basic_clone.py`](./code/01_basic_clone.py) | The minimal Prototype — `clone()` method + `copy.deepcopy` |
| [`02_copy_module_explained.py`](./code/02_copy_module_explained.py) | Shallow vs deep copy, the #1 Prototype bug, the `__deepcopy__` performance lever |
| [`03_prototype_registry.py`](./code/03_prototype_registry.py) | Clone-by-name registry — the IDE "new from template" pattern |
| [`04_dataclass_replace_alternative.py`](./code/04_dataclass_replace_alternative.py) | When `dataclasses.replace()` is the right tool, and the decision rule |
| [`05_basic_object_adapter.py`](./code/05_basic_object_adapter.py) | The minimal Object Adapter — Target / Adaptee / Adapter spelled out |
| [`06_payment_gateway_adapter.py`](./code/06_payment_gateway_adapter.py) | Razorpay adapter — method rename + unit convert + return-shape translate. UML-friendly for PyCharm |
| [`07_class_vs_object_adapter.py`](./code/07_class_vs_object_adapter.py) | Object Adapter vs Class Adapter — and why the class flavour leaks the Adaptee |
| [`08_third_party_sdk_adapter.py`](./code/08_third_party_sdk_adapter.py) | Two competing analytics SDKs hidden behind one `Analytics` interface — swap vendors by changing one line |
| [`09_adapter_with_factory.py`](./code/09_adapter_with_factory.py) | Adapter + Factory composed. Also production-grade exception translation at the adapter boundary |
| [`10_proto_pitfalls_reset_and_singleton.py`](./code/10_proto_pitfalls_reset_and_singleton.py) | Two pitfalls textbooks skip — runtime state leaking through `clone()` and `copy.deepcopy` breaking a Singleton's invariant |
| [`11_deepcopy_override_recipes.py`](./code/11_deepcopy_override_recipes.py) | Four real-world recipes for `__deepcopy__`: share read-only state, reset runtime state, replace non-copyable members, invalidate caches |
| [`12_django_payments_adapter_refactor.py`](./code/12_django_payments_adapter_refactor.py) | Refactoring an actual Django `payments/views.py` that hardcodes `razorpay.Client(...)` at module level into a `PaymentGateway` interface + adapters. Includes a unit test the original code couldn't have written |

### Viewing the UML diagram in PyCharm

`06_payment_gateway_adapter.py` is deliberately structured for PyCharm's UML class-diagram view:

1. Open the file in PyCharm.
2. Right-click the file in the Project tree → **Diagrams** → **Show Diagram…** → **Python Class Diagram**.
3. PyCharm renders `PaymentGateway` as the abstract Target, with `StripeGateway`, `PayPalGateway`, and `RazorpayAdapter` all pointing up to it via "implements" edges. `RazorpayAdapter` also has a composition arrow to `RazorpayClient`.

---

## Further reading

### Prototype

- 📖 **[`copy` — Python docs](https://docs.python.org/3/library/copy.html)** — read this once. Specifically the section on `__copy__` and `__deepcopy__` hooks.
- 🎨 **[Refactoring.Guru — Prototype](https://refactoring.guru/design-patterns/prototype)** — clean diagrams & the canonical GoF version.
- 🧰 **[`dataclasses.replace`](https://docs.python.org/3/library/dataclasses.html#dataclasses.replace)** — the "Prototype I actually need 80% of the time."

### Adapter & structural family

- 🎨 **[Refactoring.Guru — Adapter](https://refactoring.guru/design-patterns/adapter)** — diagrams for Object vs Class Adapter.
- 📁 **[`io` — `StringIO` & `BytesIO`](https://docs.python.org/3/library/io.html)** — real Adapter you'll use weekly.
- 👋 **[Django Auth Backends](https://docs.djangoproject.com/en/stable/topics/auth/customizing/#writing-an-authentication-backend)** — production example of Adapter.
- 📚 **[Design Patterns (Gamma et al., 1994), Ch. 3 (Creational) & Ch. 4 (Structural)](https://archive.org/details/designpatternsel00gamm)** — the original. Skim — don't memorise.

**Honest advice:** for both patterns, do *one* Refactoring.Guru pass and one read of the relevant Python stdlib module. Skip GoF chapters unless you've already written the pattern in real code — the book makes more sense after that, not before.

---

## After this class

- **Next class** (LLD-19): **Strategy & Observer** — your first behavioural patterns.
- **Class after** (LLD-20): **Decorator & UML Diagrams** — rest of the structural family hands off into a deep-dive on UML.

---

*LLD-18: Prototype & Adapter · Academy Feb 26 — Python Backend LLD Batch*
