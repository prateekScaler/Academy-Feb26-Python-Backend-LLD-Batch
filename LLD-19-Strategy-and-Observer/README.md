# LLD-19 — Strategy & Observer

*The first two behavioural patterns — how objects collaborate over time.*

> This README is the **full lesson in long form**. If you'd rather click through interactive quizzes, open [`index.html`](./index.html). If you want to run the patterns, the [`code/`](./code/) directory has 11 self-contained Python examples — each file is `python3`-runnable with no dependencies.

---

## Table of contents

1. [At a glance](#at-a-glance)
2. [Recap — Prototype Registry & Adapter variations](#recap--prototype-registry--adapter-variations) *(includes the two ideas we didn't get to in LLD-18 live)*
3. [Behavioural patterns — the third GoF family](#behavioural-patterns--the-third-gof-family)
4. [Part 1 — Strategy](#part-1--strategy)
   - 4.1 [The problem](#41-the-problem)
   - 4.2 [The pattern](#42-the-pattern)
   - 4.3 [Three wirings](#43-three-wirings)
   - 4.4 [Strategy in the wild](#44-strategy-in-the-wild)
   - 4.5 [Pitfalls](#45-pitfalls)
   - 4.6 [When Strategy earns its keep](#46-when-strategy-earns-its-keep)
5. [Part 2 — Observer](#part-2--observer)
   - 5.1 [The problem](#51-the-problem)
   - 5.2 [The pattern](#52-the-pattern)
   - 5.3 [Push vs Pull](#53-push-vs-pull)
   - 5.4 [Sync vs async](#54-sync-vs-async)
   - 5.5 [Observer in the wild](#55-observer-in-the-wild)
   - 5.6 [Pitfalls](#56-pitfalls)
   - 5.7 [When Observer earns its keep](#57-when-observer-earns-its-keep)
6. [Compare — Strategy vs State vs Command vs Observer](#compare--strategy-vs-state-vs-command-vs-observer)
7. [Summary mindmap](#summary-mindmap)
8. [Interview cheat sheet](#interview-cheat-sheet)
9. [Code companions](#code-companions)
10. [Further reading](#further-reading)

---

## At a glance

Today opens the **Behavioural** family — the third and largest GoF family. Where Creational asked *"how is the object made?"* and Structural asked *"how are objects composed?"*, Behavioural asks *"how do objects collaborate over time?"*

Two patterns today, both heavily used in real Django, web, and data code:

- **Strategy** — when the same job can be done several different ways, hand the caller a chosen algorithm *object* instead of a `string` telling them which branch to take. Replaces growing `if/elif` chains.
- **Observer** — when one object's state change must ripple to N listeners, neither side should know about the other. The Subject keeps a list; the Observer registers and receives.

Both are about **varying behaviour without conditional code** — Strategy varies *how to do something*; Observer varies *who reacts to something*.

```
The 23 GoF patterns — where we are after today

  Creational (5)                Structural (7)             Behavioural (11)
  All done ✓                    1 of 7 (Adapter) ✓          Starting today

  Singleton    ✓                Adapter         ✓           Strategy   ← today
  Builder      ✓                Decorator (next)            Observer   ← today
  Factory Method ✓              Facade                      Command
  Abstract Factory ✓            Proxy                       State
  Prototype    ✓                Bridge                      + 7 more
                                Composite
                                Flyweight
```

---

## Recap — Prototype Registry & Adapter variations

> Two ideas from LLD-18 we ran out of time for live. The questions below teach the missed pieces in their explanations, so you can carry both into today.

### Q1 — When is Prototype the right tool?

> *"Our ML service warms a 600 MB embedding model on startup (~4 s). At inference time we score 1,000 batches per minute. Each batch needs a small per-request scratchpad attached to the warm model."*

**Answer: Prototype + custom `__deepcopy__`.** Two clues both point there:

- "expensive once" + "1000 similar per minute" — the Prototype cost equation.
- "per-request scratchpad attached to warm model" — share the giant read-only model, isolate the small mutable state.

That's Recipe 1 from LLD-18's `code/11_deepcopy_override_recipes.py` — `__deepcopy__` that shares the big read-only field by reference and zeroes the per-clone mutable field.

### Q2 — A new vendor SDK shows up. Which is *not* a job for Adapter?

> A) Our codebase uses `storage.upload(path, data)`; new vendor SDK exposes `put_object(Bucket, Key, Body)`
> B) Our analytics calls `tracker.event(name, props)`; new SDK uses `client.track(event_name, properties=)`
> **C) Two of our in-house services both implement `UserService`; we want to switch from the legacy one to the new one**
> D) Auth code wants `backend.authenticate(request, creds)`; LDAP exposes `conn.simple_bind_s(dn, pwd)`

**Answer: C.** Adapter exists for *interface mismatch*. If both services already implement the same interface, swapping is just a dependency-injection refactor. A, B, D all have a "we want X, they speak Y" gap with one side outside our control.

### Q3 — We didn't get to: the Prototype Registry

> "Notion lets users insert 'Page templates' from a /command menu (Meeting Notes / Project Brief / Daily Standup … 20+ templates). Admins should add new templates without changing the insertion code. Which pattern fits?"

**Answer: a Prototype Registry** — a `dict[name, Prototype]`. Admins call `registry.register(...)`; insertion code calls `registry.get(name).clone()`.

```python
class PrototypeRegistry:
    def __init__(self):
        self._prototypes: dict[str, Prototype] = {}

    def register(self, name: str, proto: Prototype) -> None:
        self._prototypes[name] = proto

    def get(self, name: str) -> Prototype:
        return self._prototypes[name].clone()       # fresh clone every time

# one-time setup
registry = PrototypeRegistry()
registry.register("meeting-notes", PageTemplate(blocks=[...]))
registry.register("project-brief", PageTemplate(blocks=[...]))

# usage from the /command menu
new_page = registry.get("meeting-notes")            # <1 ms, fully independent clone
new_page.title = "2026-06-02 standup"
```

**Why this beats a Factory Method:**

- **Open for extension at runtime.** Admins add new templates by calling `register(...)`. With Factory Method you'd ship a code release.
- **Templates can be loaded from data.** Read 20 template JSON files from disk on startup, build a `PageTemplate` from each, register by name. No code per template.
- **Construction is paid once.** Heavy initialisation runs at registration time; `clone()` at insertion time is <1 ms.

**The same pattern under different names:** IDE "New file from template", game engine "spawn enemy by name", notification "fetch template by template_id" — all *are* a Prototype Registry.

**When is the registry overkill?** When construction is cheap (a few µs) AND the variants are all known at compile time. In that case a plain `if/elif` or a dict literal of factory functions is simpler:

```python
# Cheap + closed set — no registry needed
EMAIL_TEMPLATES = {
    "welcome":        lambda: EmailTemplate("Welcome!"),
    "reset_password": lambda: EmailTemplate("Reset link..."),
}
msg = EMAIL_TEMPLATES["welcome"]()
```

### Q4 — We didn't get to: Object Adapter vs Class Adapter

> "Which adapter flavour is idiomatic in Python, and why?"

**Answer: Object Adapter** (composition). The adapter *holds* the adaptee as a private field and delegates. The class adapter (multi-inheritance) **leaks** every public method of the wrapped SDK and pulls in MRO complexity:

| Object Adapter (composition) | Class Adapter (multi-inheritance) |
|---|---|
| Adapter HAS-A Adaptee instance | Adapter IS-A both Target and Adaptee |
| Only `pay()` is public; SDK sealed behind `_client` | Exposes `create_order`, `capture_payment`, `utility.verify_webhook_signature`, … |
| Works for any RazorpayClient subclass | Tied to one specific class |
| Composition over inheritance | Brittle MRO if RazorpayClient has its own bases |

The leak is the killer. With a class adapter, callers can `our_adapter.create_order(...)` and bypass your `pay()` — defeating the whole point of containing the vendor SDK. Object Adapter hides it cleanly.

### Q5 — We didn't get to: Two-Way Adapter

> "A currency-input form has a 'USD' field and an 'INR' field. Editing either one updates the other. Which variation fits?"

**Answer: a Two-Way Adapter** — one class that implements *both* interfaces, so calls flow in either direction:

```python
class USDINRPriceField:
    def __init__(self, rate: float):
        self._usd: float = 0.0
        self._rate = rate

    # direction 1: someone types USD → expose INR
    def set_usd(self, usd):  self._usd = usd
    def get_inr(self):       return self._usd * self._rate

    # direction 2: someone types INR → expose USD
    def set_inr(self, inr):  self._usd = inr / self._rate
    def get_usd(self):       return self._usd
```

Mostly a curiosity in Python — almost always the right answer is two one-way adapters, not one two-way. Use it when both sides genuinely drive (form fields, ORM bridge adapters). Naming this variant in an interview signals you've read the GoF chapter.

---

## Behavioural patterns — the third GoF family

| Family | Question it answers | What it rearranges | Example patterns |
|---|---|---|---|
| **Creational** | How is the object *made*? | The "`new`" expression | Singleton, Factory, Builder, Prototype |
| **Structural** | How are objects *composed*? | The "has-a" / "is-a" graph | Adapter, Decorator, Facade, Proxy |
| **Behavioural** | How do objects *collaborate*? | The flow of messages between objects | Strategy, Observer, Command, State, Iterator |

After today you'll have **all 5 creational**, **1 of 7 structural**, and **2 of 11 behavioural**. The behavioural family is the largest and the most interview-asked — because most LLD interview problems boil down to *"design how these objects interact."*

---

## Part 1 — Strategy

### 4.1 The problem

**Sneha is building a discount engine** for an e-commerce app. First version was simple:

```python
def calculate_discount(order, discount_type: str) -> float:
    if discount_type == "none":       return 0.0
    elif discount_type == "percentage": return order.total * 0.10
    elif discount_type == "flat":     return 50.0
```

Three months later the function has seventeen branches across `bulk`, `loyalty`, `coupon`, `first_time`, `festival`, …. Three things have gone wrong:

- **Open-Closed violation.** Every new discount type means editing this function — risking regressions in the other branches.
- **SRP violation.** The function knows about 11 domains: bulk pricing, loyalty tiers, coupon validation, first-time-buyer rules, festival promotions, …
- **Testability collapse.** Unit-testing one branch means setting up a full `order`, `user`, `coupon` object even when only one of the three is relevant.

**The shape:** the *same job* (compute a discount) has *many different algorithms*. Each algorithm has its own data needs, its own validation, and its own evolution timeline. They're being conflated.

### 4.2 The pattern

> *Define a family of algorithms behind a common interface. Hand the caller an algorithm **object** — not a **string** telling them which branch to take.*

Three roles:

```
   Context  ───holds───→  Strategy (interface)  ←─implements─  ConcreteStrategy
   (uses                     calculate(...)                    (one per algorithm)
    the                                                        e.g. LoyaltyDiscount,
    strategy)                                                  CouponDiscount, …
```

```python
from abc import ABC, abstractmethod

# 1. Common interface
class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, order, user) -> float: ...

# 2. One concrete class per algorithm
class NoDiscount(DiscountStrategy):
    def calculate(self, order, user): return 0.0

class FlatDiscount(DiscountStrategy):
    def __init__(self, amount: float): self.amount = amount
    def calculate(self, order, user): return self.amount

class LoyaltyDiscount(DiscountStrategy):
    TIER_RATE = {"silver": 0.05, "gold": 0.12, "platinum": 0.20}
    def calculate(self, order, user):
        return order.total * self.TIER_RATE.get(user.get_loyalty_tier(), 0)

class CouponDiscount(DiscountStrategy):
    def __init__(self, coupon): self.coupon = coupon
    def calculate(self, order, user):
        if self.coupon.expired(): return 0.0
        return order.total * self.coupon.value if self.coupon.type == "percent" else self.coupon.value

# 3. Context holds whichever strategy was chosen
class Checkout:
    def __init__(self, discount: DiscountStrategy):
        self._discount = discount
    def total_after_discount(self, order, user) -> float:
        return order.total - self._discount.calculate(order, user)

# usage
checkout = Checkout(discount=LoyaltyDiscount())
final = checkout.total_after_discount(order, user)
```

**Adding `FestivalDiscount` means writing one new class.** Nothing else in the codebase changes. The 17-branch original was the textbook OCP violation; Strategy is the textbook OCP fix.

### 4.3 Three wirings

"Hand the caller an algorithm object" leaves *when* open. Three timings, three idioms:

| Wiring | When you pick the strategy | Code shape | Use when… |
|---|---|---|---|
| **Constructor injection** | Once, at object creation | `Checkout(discount=Loyalty())` | Strategy is fixed for the object's lifetime |
| **Setter / property** | Any time after creation | `checkout.discount = Coupon(c)` | Strategy changes mid-flight (e.g. user adds a coupon) |
| **Per-call argument** | Every method call | `total(order, user, discount=Flat(50))` | Strategy is request-scoped, not object-scoped |

#### The Pythonic shortcut — Strategy as a callable

In Python a Strategy is often just a callable — no class required:

```python
# Strategy as a function — Pythonic when the algorithm has no state
def total(order, user, discount=lambda o, u: 0.0) -> float:
    return order.total - discount(order, user)

total(order, user, discount=lambda o, u: o.total * 0.10)   # 10% off

# Same idea as sorted(...)'s key= parameter:
sorted(items, key=lambda i: i.price)         # Strategy: price-key
sorted(items, key=lambda i: i.rating)        # Strategy: rating-key
sorted(items, key=operator.attrgetter("date"))  # Strategy: date-key
```

The stdlib uses Strategy everywhere — usually as plain callables: `sorted(key=)`, `min(key=)`, `max(key=)`, `filter(predicate, ...)`, `functools.reduce(op, ...)`, `heapq.nlargest(n, key=)`. Each one accepts a strategy object (function) parameterising the algorithm. **When asked "give a Strategy example you've used", these are all valid answers.**

### 4.4 Strategy in the wild

- **🧠 ML training loops — swap optimizers.** PyTorch's `torch.optim` ships SGD, Adam, AdamW, RMSprop — all implementing the same `step()`/`zero_grad()` interface. Researchers swap optimizers by changing one line; the training loop never knows.

- **📚 Compression libraries — gzip vs brotli vs zstd.** HTTP servers accept a list of compression algorithms — each a Strategy implementing `compress(bytes) → bytes`. The same response goes through whichever algorithm matches the client's `Accept-Encoding`.

- **🎵 Spotify's "shuffle" — pick a queueing algorithm.** Random shuffle, smart shuffle (interleaves new + familiar), DJ mode (transition-aware). The player holds whichever one is active.

- **🛒 E-commerce checkout — pricing rules per region.** Amazon/Flipkart pricing differs by country. A `PricingStrategy` per region keeps the checkout code clean — `checkout.set_pricing(IndiaPricing())` at session start.

### 4.5 Pitfalls

#### Over-strategising — YAGNI

**Bad candidate:** *"Add 1 to a number — abstracted behind an `IncrementStrategy` so we can later 'swap' the increment algorithm."* Classic over-engineering. Strategy earns its keep when (i) there's a real family of algorithms with meaningful differences, AND (ii) adding new variants is plausible in the foreseeable future. "We might want to vary `x + 1` later" is not a real reason.

**Rule:** introduce Strategy when you have 2-3 actual variants in hand, not in case you might.

#### Leaking the Context's internals

```python
class PricingStrategy(ABC):
    @abstractmethod
    def price(self, checkout) -> float: ...      # ← takes the whole Checkout

class RegularPricing(PricingStrategy):
    def price(self, checkout):
        return checkout.cart.total + checkout.shipping.cost - checkout.applied_coupon.value
```

The Strategy now *knows* the Checkout has a `cart`, a `shipping`, an `applied_coupon`. Rename any of those on Checkout and **every** Strategy breaks — even ones that didn't need those fields.

```python
# Better
class PricingStrategy(ABC):
    @abstractmethod
    def price(self, subtotal: float, shipping: float, coupon_value: float) -> float: ...
        # Strategy declares EXACTLY what it consumes — no hidden coupling
```

Pass primitives or small DTOs. Strategy's value is decoupling — don't undo it by reaching back into the Context.

### 4.6 When Strategy earns its keep

| ✅ Use Strategy when | ❌ Skip Strategy when |
|---|---|
| You have an `if/elif` chain over a "mode" parameter that's grown past 3 branches | Two short branches — an `if/else` is clearer than a class hierarchy |
| Each branch has its own dependencies (different DB tables, different external calls) | The "variants" are all the same algorithm with different constants — pass a parameter instead |
| You expect new variants to be added by future-you or other teams | The variant is determined globally and never changes — a config flag works |
| You want each algorithm testable in isolation | You're inventing variants that don't exist yet (YAGNI) |

---

## Part 2 — Observer

### 5.1 The problem

**Aryan is wiring up order processing.** When an order moves to `PAID`, four things must happen:

1. Send a confirmation email to the customer
2. Notify the warehouse to start fulfilment
3. Update the analytics service with the conversion
4. Award loyalty points to the customer's account

First draft hardcodes all four. Six months later the list has grown to nine downstream effects (fraud check, inventory decrement, partner commissions, …) and the Order class has become a directory of every other team's code. Three things have gone wrong:

- **SRP violation.** Order knows about email, warehouse, analytics, loyalty, fraud, inventory, …
- **Tight coupling.** Changing the analytics service signature requires editing `Order`. Adding a new effect means a code review on Order.
- **Testing nightmare.** Unit-testing `mark_paid()` requires mocking all four (later nine) services.

**The shape:** Order's only real job is to manage its own state. But it's accumulating *everyone else's reactions* to its state changes. The right people to know "Order became PAID" are the listeners — not Order itself.

### 5.2 The pattern

> *The Subject keeps a list of Observers. When its state changes, it loops through the list and notifies each. Neither side knows the other's identity beyond the agreed interface.*

```
Subject ────notify────→ Observer (interface) ←─implements─ ConcreteObservers
(holds                    update(event)                    EmailObserver,
 the list,                                                 WarehouseObserver,
 emits)                                                    AnalyticsObserver, …
```

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

# Frozen event = clean push interface
@dataclass(frozen=True)
class OrderPaidEvent:
    order_id: str
    customer_id: str
    total: float

# 1. Observer interface
class OrderObserver(ABC):
    @abstractmethod
    def on_paid(self, event: OrderPaidEvent) -> None: ...

# 2. Concrete observers — each with one job
class EmailObserver(OrderObserver):
    def on_paid(self, event):
        email_service.send_confirmation(event.customer_id, event.order_id)

class WarehouseObserver(OrderObserver):
    def on_paid(self, event):
        warehouse_service.queue_fulfilment(event.order_id)

class AnalyticsObserver(OrderObserver):
    def on_paid(self, event):
        analytics.track_conversion(event.order_id, event.total)

# 3. Subject maintains the list
class Order:
    def __init__(self):
        self._observers: list[OrderObserver] = []

    def subscribe(self, observer):    self._observers.append(observer)
    def unsubscribe(self, observer):  self._observers.remove(observer)

    def mark_paid(self):
        self.status = "PAID"
        self.save()
        event = OrderPaidEvent(order_id=self.id, customer_id=self.customer_id, total=self.total)
        for obs in self._observers:           # notify — Order doesn't know WHO
            obs.on_paid(event)

# wire up reactions at startup
order = Order()
order.subscribe(EmailObserver())
order.subscribe(WarehouseObserver())
order.subscribe(AnalyticsObserver())
# Adding a new effect = .subscribe(NewObserver()) — Order untouched

order.mark_paid()    # all three observers fire
```

### 5.3 Push vs Pull

Two conventions for what the Subject puts in the `update(...)` call:

|  | Push | Pull |
|---|---|---|
| What gets passed | Data the Observer needs: `obs.on_paid(self.total, self.customer)` | Just the Subject: `obs.on_paid(self)` — Observer reaches back |
| Subject knows… | What each Observer cares about | Nothing — passes itself |
| Observer knows… | Nothing about the Subject's internals | Subject's full API |
| When push wins | Stable event shape, many observers | — |
| When pull wins | — | Observers need different subsets of state |

**A cleaner push variant:** define a small *event object* that captures everything observers might need (as in the `OrderPaidEvent` above). Observers get a frozen, well-typed event — not the full mutable Subject. This is the shape Django Signals, Kafka events, and AWS SNS messages all share.

### 5.4 Sync vs async

Out of the box, `self._observers` + `for` means observers run **synchronously, in registration order, in the publisher's thread**. That's often *not* what you want for an HTTP request handler:

- Slow observers block the response (email service times out → user's confirmation page hangs).
- An exception in observer #2 means observers #3, #4, … never run.

Three production shapes for "decouple the publisher from observer execution":

#### Best-effort sync — trap each observer's exception

```python
def notify(self, event):
    for obs in self._observers:
        try:
            obs.on_paid(event)
        except Exception as e:
            log.exception("observer %s failed: %s", obs, e)
```

Cheap, but slow observers still block.

#### Fire-and-forget — enqueue, let workers consume

Publisher writes the event to a queue (Redis Streams, Kafka, RabbitMQ, Celery broker). Observers are workers that pull from the queue. Publisher returns immediately.

```python
def mark_paid(self):
    self.status = "PAID"
    self.save()
    bus.publish("order.paid", OrderPaidEvent(...))   # < 1 ms
    # Workers pick it up, run observer logic in their own process
```

Used in any non-trivial Django app via Celery.

#### async/await — concurrent observers in one event loop

```python
await asyncio.gather(*[obs.on_paid(event) for obs in obs_list],
                     return_exceptions=True)
```

Runs all observers concurrently — the publisher waits for the slowest, but doesn't sum their times. See `code/10_async_observer.py` for a runnable demo (sequential: ~650 ms, concurrent: ~300 ms with the same handlers).

### 5.5 Observer in the wild

- **👋 Django Signals.** `post_save`, `pre_delete`, `user_logged_in`. Connect a handler — Django invokes it whenever the matching event fires, in any view. The `@receiver(post_save, sender=Order)` decorator is sugar over `post_save.connect(handler, sender=Order)` — a registration call. **Sender = Subject. Receiver = Observer.** See `code/09_django_signals_style.py` for a from-scratch implementation.

- **🖲 Browser events / Node's EventEmitter / Python's `asyncio.Event`.** `button.addEventListener("click", handler)`, `emitter.on("event", handler)`, `websocket.onmessage = handler` — all literal Observer.

- **🔌 Spreadsheet recalculation.** When you edit cell `A1` in Excel/Sheets, every formula referencing `A1` recomputes. Each formula cell subscribed to `A1`; `A1` publishes its change. Reactive frameworks (React, Vue, MobX) generalise this idea to whole UIs.

- **⚡ Pub/sub message brokers — Kafka, Redis Streams, AWS SNS.** Distributed Observer. Publishers post to a topic; subscribers consume. The broker is the infrastructure-level "Subject's list of observers" — durable, retryable, cross-process. Same pattern, different scale.

### 5.6 Pitfalls

#### Memory leak — observers never unsubscribed

A web app creates and destroys 10,000 `Cart` objects per minute. Each Cart subscribes to `PriceFeed` for live pricing. After an hour, memory usage has climbed 4 GB. Why?

`subject.subscribe(observer)` adds a **strong reference** to the Subject's observer list. If the Observer is supposed to be short-lived but the Subject keeps it referenced, GC can never collect it — and every event the Subject fires keeps calling the dead observer.

**Two fixes:**

1. **Always pair `subscribe`/`unsubscribe`.** Most natural in a context manager: `with feed.subscription(cart): ...`
2. **Hold observers in a `WeakSet`.** Python's `weakref.WeakSet` lets GC collect the observer as soon as the application drops its last strong reference.

```python
import weakref

class PriceFeed:
    def __init__(self):
        self._observers = weakref.WeakSet()    # GC can reclaim
    def subscribe(self, observer):
        self._observers.add(observer)          # weak ref
    def notify(self, event):
        for obs in self._observers:            # dead ones already gone
            obs.on_price(event)
```

Django Signals uses weak references by default for this exact reason. Runnable demo in `code/08_observer_memory_leak_fix.py`.

#### Notification storms / cycles

Observer A reacts to Order events by updating Inventory. Inventory has its own observers, one of which updates Pricing. Pricing's observers include the Order display. Press "Pay" — a notification storm or cycle hangs the system.

**Three guards:**

- **Keep observers *passive*.** Reactions should not fire new events on the same Subject. If they must, route through a queue.
- **Make events immutable.** Frozen dataclass / namedtuple. Observers can't tamper with the event in-flight.
- **Bound the propagation depth.** If you find yourself debugging "why did the price update three times after one Pay click", you have a notification storm — identify the cycle.

### 5.7 When Observer earns its keep

| ✅ Use Observer when | ❌ Skip Observer when |
|---|---|
| One state change has multiple, unrelated downstream effects | There's only one downstream reaction, and it always runs — just call it directly |
| Those effects should be add/removable without touching the Subject | Subject's events must be reliably consumed even on crash — use a durable broker (Kafka), not in-process Observer |
| The Subject shouldn't know which subsystems care about its events | You need ordered, guaranteed delivery across machines — same answer (broker) |
| You want each effect testable in isolation | Reactions need to know about each other (step 3 needs step 2's result) — that's Chain of Responsibility / a workflow, not Observer |

---

## Compare — Strategy vs State vs Command vs Observer

All four behavioural patterns "encapsulate a unit of work." The pattern name says which unit and who triggers it.

| Pattern | What's encapsulated | Who triggers execution | Example |
|---|---|---|---|
| **Strategy** | An *algorithm* (one method) | The Context, when it needs the algorithm | "Pay using THIS pricing rule" |
| **Observer** | A *reaction to an event* | The Subject, when its state changes | "When Order becomes PAID, email + warehouse + analytics react" |
| **Command** | An *action to perform* (queued, undoable, replayable) | The invoker, when the user clicks / a queue fires | "On Ctrl+Z, undo the last Command" |
| **State** | A *set of allowed transitions* bound to an object's current mode | The Context, when an event hits | "In DRAFT state, only `.submit()` is allowed; in REVIEW, only `.approve()`" |

### Strategy vs State — the subtle one

Both wrap "what to do next" behind a class. The difference is whether the choice is *external* or *internal*:

- **Strategy** — the *caller* picks. You set `checkout.discount = Loyalty()` from outside; the Checkout uses whatever's set.
- **State** — the *object* picks (transitions itself). A `Document` in `DraftState` calls `.submit()`, which transitions to `ReviewState`. The next call's allowed actions depend on the new state.

If you can swap the strategy from outside at any time without breaking invariants — it's Strategy. If swapping is only legal after specific transitions — it's State. Runnable side-by-side in `code/05_strategy_vs_state.py`.

### Cross-family check

> *"I want to vary something at runtime."* — vary **what**?

- Vary **which concrete class to instantiate** → **Factory**
- Vary **how interfaces fit together** → **Adapter**
- Vary **which algorithm to use for one job** → **Strategy**
- Vary **who reacts to one event** → **Observer**

---

## Summary mindmap

### 🎮 Strategy — *behavioural* — "swap the algorithm"

- **Use when:** an `if/elif` over "mode" has grown past 3 branches; each branch has its own dependencies
- **Three roles:** Context (holds strategy) · Strategy (interface) · ConcreteStrategy (one per algorithm)
- **Three wirings:** constructor · setter · per-call argument
- **Python shortcut:** a function is often Strategy enough — `sorted(key=)`, `filter(pred, ...)`
- **Real-world:** PyTorch optimizers · HTTP compression · pricing rules · sort comparators
- **Skip when:** two short branches; variants are just different constants; over-engineered "in case we need it"
- **#1 bug:** Strategy reaches back into the Context's internals — coupling restored. Pass only what each strategy consumes.

### 📢 Observer — *behavioural* — "publish change, observers react"

- **Use when:** one state change must trigger multiple unrelated downstream effects
- **Two roles:** Subject (holds observer list, emits events) · Observer (registers a callback)
- **Push vs Pull:** push an immutable event object (cleanest) vs pull from the Subject
- **Sync vs async:** in-process best-effort sync · fire-and-forget via queue · async/await gather
- **Real-world:** Django Signals · browser events · spreadsheet recalc · Kafka / Redis Streams / SNS
- **Skip when:** one fixed reaction (just call it) · need durable delivery (use a broker)
- **#1 bug:** memory leak — subscribers never unsubscribe; Subject's strong refs keep them alive. Fix: `WeakSet` or paired subscribe/unsubscribe.

### 🎯 Cross-family cheat — "vary what?"

- Vary **which class** → Factory
- Vary **which interface** fits with another → Adapter
- Vary **how to do one job** → **Strategy**
- Vary **who reacts to one event** → **Observer**

---

## Interview cheat sheet

**If asked "when would you use Strategy?":** lead with the OCP win — a growing `if/elif` over a "mode" parameter, each branch with different dependencies. Mention `sorted`'s `key=` as the everyday Python example. Bonus: name the three wirings (constructor / setter / per-call).

**If asked "when would you use Observer?":** lead with decoupling one publisher from N unrelated reactions. Name Django Signals as a built-in example. Bonus: distinguish sync (in-process, blocks) from async (broker / queue) — and call out the memory-leak trap with `WeakSet`.

**If asked "Strategy vs State?":** who picks — caller picks → Strategy; object transitions itself → State.

**If asked "Observer vs pub/sub broker?":** same pattern, different scale. In-process & in-memory → Observer. Cross-process / durable → broker.

---

## Code companions

All 10 files in [`code/`](./code/) are self-contained and runnable with no dependencies — just `python3 <file>`.

| File | What it demonstrates |
|---|---|
| [`01_basic_strategy.py`](./code/01_basic_strategy.py) | The minimal Strategy pattern — Context / Strategy / ConcreteStrategy for Sneha's discount engine |
| [`02_sort_strategy_python_native.py`](./code/02_sort_strategy_python_native.py) | Strategy in Pythonic form — same problem solved with formal classes vs plain callables (`sorted(key=)`) |
| [`03_payment_pricing_strategy.py`](./code/03_payment_pricing_strategy.py) | Three wirings side-by-side — constructor / setter / per-call. UML-friendly for PyCharm |
| [`04_strategy_with_factory.py`](./code/04_strategy_with_factory.py) | Strategy + Factory composed — Factory picks the Strategy by config string |
| [`05_strategy_vs_state.py`](./code/05_strategy_vs_state.py) | Strategy vs State — same domain shown both ways, with the "who picks?" mnemonic |
| [`06_basic_observer.py`](./code/06_basic_observer.py) | The minimal Observer — Aryan's order processing with 4 reactions decoupled |
| [`07_pubsub_topics.py`](./code/07_pubsub_topics.py) | Topic-based pub/sub — one EventBus dispatches to handlers by topic name |
| [`08_observer_memory_leak_fix.py`](./code/08_observer_memory_leak_fix.py) | The classic Observer leak demonstrated with weakref, then fixed with `WeakSet` |
| [`09_django_signals_style.py`](./code/09_django_signals_style.py) | Django-Signals API built from scratch — `@receiver` decorator, sender filtering, weak refs |
| [`10_async_observer.py`](./code/10_async_observer.py) | `asyncio.gather` for concurrent observer notification — sequential ~650 ms vs concurrent ~300 ms |
| [`11_stdlib_strategy_survey.py`](./code/11_stdlib_strategy_survey.py) | Six stdlib Strategies in one file with realistic output — `sorted` / `min`/`max` / `filter` / `reduce` / `heapq.nlargest` / `operator.itemgetter`/`attrgetter`. Each section names which part is the fixed algorithm vs the swappable strategy parameter |

### Viewing the UML diagram in PyCharm

`03_payment_pricing_strategy.py` is structured for PyCharm's UML class-diagram view:

1. Open the file in PyCharm.
2. Right-click → **Diagrams** → **Show Diagram…** → **Python Class Diagram**.
3. PyCharm renders `PricingStrategy` as the abstract root, with `RegularPricing`/`FestivalPricing`/`StudentPricing` implementing it, and `Checkout`/`CheckoutSwappable`/`CheckoutPerCall` all composing it.

---

## Further reading

### Strategy

- 🎨 **[Refactoring.Guru — Strategy](https://refactoring.guru/design-patterns/strategy)** — clean diagrams, the canonical GoF version.
- 📝 **[`sorted(key=)` — Python docs](https://docs.python.org/3/library/functions.html#sorted)** — the simplest, most-used Strategy in the Python ecosystem.
- 🧠 **[PyTorch `torch.optim`](https://pytorch.org/docs/stable/optim.html)** — production-grade Strategy: SGD / Adam / AdamW / RMSprop, swappable in one line.

### Observer

- 🎨 **[Refactoring.Guru — Observer](https://refactoring.guru/design-patterns/observer)** — walks the pattern with diagrams in multiple languages.
- 👋 **[Django Signals](https://docs.djangoproject.com/en/stable/topics/signals/)** — production Observer. Read this carefully — `post_save`, `pre_delete`, custom signals.
- 🧷 **[Python `weakref`](https://docs.python.org/3/library/weakref.html)** — `WeakSet`, `WeakKeyDictionary` — the fix for the Observer memory leak.
- 📚 **[GoF — *Design Patterns* (1994)](https://www.oreilly.com/library/view/design-patterns-elements/0201633612/)** — Strategy & Observer both in Chapter 5. Skim only after you've written each in real code.

**Honest advice:** for both patterns, do *one* Refactoring.Guru pass and one read of the relevant stdlib / framework module (`sorted` / Django Signals). Skip GoF chapters until you've written each pattern at least once — the book makes more sense after that, not before.

---

## After this class

- **Next class** (LLD-20): **Decorator & UML Diagrams** — the rest of the structural family hands off into a deep-dive on UML.
- **After that**: the LLD-interview series — Types of LLD problems, then design + code TicTacToe, Parking Lot, BookMyShow, Splitwise, Google Calendar.

---

*LLD-19: Strategy & Observer · Academy Feb 26 — Python Backend LLD Batch*
