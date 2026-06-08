# LLD-21 — Types of LLD Interviews & How to Approach Them

> The methodology class. Closes Module 3 by turning SOLID, the GoF patterns, and UML from LLD-13 to LLD-20 into a 90-minute interview playbook.

This file is **the class, in text**. Print it, glance at it before every LLD interview, paste it next to your IDE during practice. The `index.html` is the slideshow version; this is the same content as a working reference.

---

## 1. Indian tech tiers — who interviews how

The same job title gets interviewed three completely different ways.

| Tier | Who | Style | Time | What they ask | Prep |
|---|---|---|---|---|---|
| **Tier 1 — Traditional IT** | TCS, Infosys, Wipro, Cognizant, Accenture, Capgemini, HCL | Theory-heavy verbal Q&A. Almost no coding. | 30–45 min | "Explain SOLID", "Singleton vs Factory", "abstract class vs interface", "thread-safe Singleton", "what are decorators / GIL / magic methods" | Memorise GoF names + 2 examples each, SOLID with examples, Python internals (decorators, GIL, magic methods) |
| **Tier 2 — Product MNCs** | Google, Microsoft, Amazon, Flipkart, PhonePe, Uber, Ola, Paytm | Design process on whiteboard / doc. Pseudo-code or partial real code. | 45–60 min | "Design Zoomcar / Library / Movie booking" — wants requirements, class diagram, APIs, deep-dive on schema or concurrency | The 7-step playbook below, 10+ problems end-to-end |
| **Tier 3 — Modern startups** | Swiggy, Zomato, Cred, Razorpay, Zepto, Meesho, ShareChat, Dream11 | Machine-coding round. Working code in IDE, runnable demo, sometimes tests. | 90–120 min | "Build Splitwise / Snake-and-Ladder" — wants a working demo more than a perfect design | 90-minute timed mocks, `python main.py` habit, dataclasses + Enums + comprehensions |

---

## 2. Six concrete formats

Within those tiers, the actual format varies. Misreading the format costs you the loop.

1. **Machine coding (90 min)** — sit-down + IDE + ship a working solution. Splitwise / Parking Lot / Tic-Tac-Toe / BookMyShow / ride-sharing / in-memory cache. Judged on: working demo + clean class design + you can extend it live.
2. **Design discussion (45–60 min)** — whiteboard / Google Doc. UML class diagram + API list + trade-offs. No working code. Judged on: clean class diagram, sound APIs, SOLID/pattern awareness.
3. **Take-home (24–72 hours)** — implement at home, submit a repo with tests + README + design notes. Stripe / GitLab / remote-first. Judged on: code quality, test coverage, design choices in README, no shortcuts.
4. **System + LLD hybrid (60 min)** — half HLD (services, DBs, scale), half LLD (one component drawn in classes). FAANG senior+, Atlassian, Uber. Judged on: switching altitude on demand.
5. **Code review (45–60 min)** — given a PR-shaped file, find bugs / smells / SOLID violations and suggest fixes. Stripe, Atlassian, Twilio. Judged on: what you notice + how you frame it + the fix you propose.
6. **Live design talk (30 min)** — no whiteboard, just talk. "Walk me through how you'd design X." Recruiter pre-screens. Judged on: structured thinking without visuals.

---

## 3. The 7-step playbook (memorise this)

| #  | Time     | Step                         | What you do                                                |
|----|----------|------------------------------|------------------------------------------------------------|
| 1  | 0–5      | **Clarify**                  | Confirm what the product is. Ask 3–5 scope / scale / out-of-scope questions. |
| 2  | 5–10     | **Requirements**             | FR + NFR. Cap at 4–5 FR and 1–2 NFR. Pin to the board.    |
| 3  | 10–18    | **Entities & relationships** | Nouns → classes. Verbs → methods. Sketch UML.             |
| 4  | 18–25    | **APIs**                     | Method signatures only. No bodies yet.                    |
| 5  | 25–65    | **Code (happy path first)**  | Simplest case end-to-end. Then add the edges you agreed.  |
| 6  | 65–80    | **Demo**                     | Run it live. Walk one happy path, one edge case.          |
| 7  | 80–90    | **Trade-offs**               | Persistence + concurrency + extension. "If I had 10 more…" |

The first three steps look slow. They're what makes the last four fast.

### Step 1 — Clarify (5 min)

**1a. Overview alignment first.** Confirm what the product does before any scope question.

```
Interviewer: "Design Zoomcar."

❌ Bad:  "Sure, let me start with a User class…"
         [assumes it's like Uber; 40 min in realises Zoomcar is
          self-drive rentals, not ride-hailing]

✅ Good: "Quick check — Zoomcar is the self-drive car-rental platform
          where users book by the hour/day, right?"
          "Got it. Consumer side (booking) or admin (inventory)?"
```

If you don't know the product, **say so**:
```
"I haven't used Dunzo — could you give me a one-line description?"
```
Asking is a strength signal. Pretending costs you the round.

**1b. Then the three-category sweep.**

| Category | Examples |
|---|---|
| **Scope**         | "Single group or many?" "Partial payments or full only?" "Currency conversion in scope?" |
| **Scale**         | "In-memory or persistent?" "Single-threaded or concurrent?" "How many users / orders?" |
| **Out-of-scope**  | "Auth / login needed?" "UI or just the engine?" "Invoices or just totals?" |

**Four worked examples — wrong vs right.**

| Domain | ❌ Wrong | ✅ Right |
|---|---|---|
| **Splitwise** | Assume equal split only. Refactor at minute 40 when interviewer mentions percent. | "Just equal split, or also percent / share / exact-rupee?" Then settlements? Currency? Pin scope on the board. |
| **BookMyShow** | Jump straight to seats. Freeze when asked "what if two people pick the same seat?" | "Multi-user concurrent booking — how do we handle the seat-lock race?" Lock TTL? Async payment? Multi-show-per-screen? |
| **Uber matching** | "Nearest driver wins" → haversine loop. Scope explodes when interviewer asks about surge / Pool / decline. | "One driver or batched pool? Auto + sedan or single category? Driver-decline re-match? Surge in scope?" |
| **Zoomcar** | Assume ride-hailing like Uber. Build a User-requests-Driver model. | Confirm Zoomcar is self-drive *rental*. Pin "consumer first, admin later". |

**The pattern:** wrong version codes from a default assumption. Right version asks **one question about the open variable** — the place the design is most likely to differ from your first guess.

### Step 2 — Requirements (5 min)

**The 5–6-requirements cap (golden rule).**
- Functional requirements: cap at **4–5**
- Non-functional: cap at **1–2**
- Nice-to-haves: park them in a "future scope" list — mention out loud, do NOT implement
- Working code for 4 features > half-broken code for 15
- Interviewer would rather see one Strategy slot in cleanly than watch you ship nothing because you took on the full PRD

**Worked example — "Design Spotify (single user, in-memory):"**

| Functional (what)                                  | Non-functional (how)                                     |
|----------------------------------------------------|----------------------------------------------------------|
| Stream a song — play / pause / seek                | In-memory catalogue — no DB                              |
| Build a playlist; play in order or shuffle         | Single user — no concurrent listeners                    |
| Search by title / artist / album                   | Catalogue size: ~10,000 songs                            |
| Like a song (add to "Liked Songs")                 | Audio decoding out of scope — `play()` just prints       |
| Track recent listening history                     | Extensible: new shuffle / smart-playlist rule = one class |

When the interviewer says "catalogue is 10K songs", **pin the number on the board** and design accordingly: linear scan is fine; no sharding, no Redis cache, no inverted index needed. Over-engineering for scale you don't have loses time AND credibility.

### Step 3 — Entities & relationships (8 min)

Two reliable ways to find entities. Pick by problem shape.

**Approach A — Noun identification** (business-domain problems: library, parking, e-commerce, food delivery, Splitwise)
- Circle the **nouns** in the requirements → classes
- Underline the **verbs** → methods
- Splitwise example: User, Group, Expense, Payment, Split, Balance, Currency / add_user, add_expense, split, settle, get_balance, simplify

**Approach B — Visualization** (games, simulations, real-time: chess, snake-and-ladder, tic-tac-toe, elevator scheduler)
- Picture gameplay for 20 seconds → visible pieces are entities, actions are methods
- Snake-and-Ladder: Board, Player, Dice, Snake, Ladder, Game
- Elevator: picture lobby with 2 cars on 4 floors + 3 pending requests → Elevator, Floor, Request, Direction (enum), Scheduler

Most problems use one cleanly. Some hybrids (Parking Lot): Vehicle / Spot / Ticket from nouns, Floor from visualization.

**Then draw the relationships** (UML arrows from LLD-20):
- `◆—` Composition: parts die with the whole (Order ◆— OrderLine)
- `◇—` Aggregation: parts outlive the whole (Team ◇— Player)
- `——` Association: knows-about, no ownership (Doctor —— Patient)
- `——▷` Inheritance: is-a (SavingsAccount ——▷ BankAccount)
- `- - ▷` Realisation: implements abstract (`<<abstract>>` / `<<ABC>>` / `<<Protocol>>`)

### Step 4 — APIs (7 min)

Method signatures only. **No method bodies.** This is where you commit to the contract: parameter types, return type, which class owns the method. Catch design holes before bodies bake them in.

```python
from abc import ABC, abstractmethod

class User:
    def __init__(self, user_id: str, name: str): ...

class Group:
    def add_user(self, user: User) -> None: ...
    def add_expense(self, expense: Expense) -> None: ...
    def balances(self) -> dict[User, float]: ...
    def simplified_payments(self) -> list[tuple[User, User, float]]: ...

class Expense:
    def __init__(self, payer: User, amount: float, split: SplitStrategy): ...
    def shares(self) -> dict[User, float]: ...

class SplitStrategy(ABC):
    @abstractmethod
    def split(self, amount: float, members: list[User]) -> dict[User, float]: ...

class EqualSplit(SplitStrategy): ...
class PercentSplit(SplitStrategy): ...
class ShareSplit(SplitStrategy): ...
```

**Strategy pattern already shows up** — `SplitStrategy` ABC with three implementations. Patterns are tools you reach for in Step 3–4 when you spot the shape, not slogans you announce. Senior candidates introduce patterns silently in code and only name them when asked or when justifying a trade-off.

### Step 5 — Code happy path first (40 min)

Two rules:
- **Happy path first.** One group, two users, equal split, one expense — end-to-end. Then add edges.
- **Print as you go.** Every class gets a tiny `main()` that exercises it. If interviewer asks "does this work?" you run it in 3 seconds.

If you said "in-memory, single-threaded" in Step 2, don't widen scope mid-flight. Build the features you agreed to.

### Step 6 — Demo (15 min)

Run your code in front of the interviewer. Walk one happy path. Walk one edge case. **If it crashes, narrate and fix on screen** — that's a strength signal, not a weakness. Interviewers love watching you debug calmly. The candidate who says "ah, I forgot to seed the user list — one sec" is rated higher than one who never runs the code.

### Step 7 — Trade-offs (10 min)

The last 10 minutes turn a "yes" into a "strong yes". Have these three lined up:

- **Persistence** — "Right now it's in-memory dicts. To persist I'd add a Repository per aggregate (`GroupRepository`, `UserRepository`) and keep domain classes ignorant of storage."
- **Concurrency** — "Assumed single-threaded. To support concurrent writes, lock per group, or per-user queues. The GIL only makes individual bytecodes atomic, not multi-step attribute reads."
- **Extension** — "If I had 10 more minutes I'd add the payment-graph simplification algorithm." OR "A new split type is one new `SplitStrategy` class — zero changes elsewhere. That's the OCP win."

If asked "how do you scale to 1M users?" — show the path: identify the bottleneck (in-memory state can't survive crashes), name the first lever (persistence), name the second (partition by group_id). Don't punt with "rewrite in Go" or "add Kafka".

---

## 4. Seven mistakes that tank interviews

| # | Mistake | Symptom | Fix |
|---|---|---|---|
| 1 | Diving into code without clarifying | You rewrite the data model twice | Ask 3–5 questions. Write FRs/NFRs on the board. |
| 2 | Building all 47 features instead of MVP | Time runs out, nothing works end-to-end | Pick top 3 features in Step 1 *with the interviewer*. |
| 3 | Inheritance for everything | Six classes inheriting from one big base | Prefer composition. Reach for Strategy / Decorator before subclasses. |
| 4 | Pattern-shopping in minute 3 | "I'll use Factory + Strategy + Observer here" — before any design is on the board | Introduce patterns silently as code, name them when justifying a trade-off. Reach for any pattern only when you can name the open variable it solves. |
| 5 | Weak naming | `doStuff(x)`, `processData(things)`, `handle()`  | Verb + domain noun: `add_expense(expense)`. Interviewers read naming as proxy for thought. |
| 6 | Skipping the live demo | "Let me clean it up first" — never runs | Run it. If it crashes, narrate and fix. Live debugging is the highest signal you'll send. |
| 7 | No trade-offs at the end | "I'd add tests" and stop | Name 3 ready: persistence, concurrency, extension. |

---

## 5. Walk-through — Parking Lot in 90 minutes

A live application of the 7-step playbook. Full runnable code in [`code/01_parking_lot_walkthrough.py`](code/01_parking_lot_walkthrough.py).

| Wall clock | Step | What you do |
|---|---|---|
| 0:00–0:05 | Clarify | Vehicle types? Floors / slot sizes? Payment model? Persistence? Concurrent users? |
| 0:05–0:10 | Requirements | FR: park, unpark, available-slots, ticket. NFR: in-memory, 1 lot, single-threaded. |
| 0:10–0:18 | Entities | ParkingLot, Floor, Slot, Vehicle (+ VehicleType enum), Ticket, ParkingStrategy, PricingStrategy. |
| 0:18–0:25 | APIs | `park(vehicle) → Ticket \| None`, `unpark(ticket) → float`, `available_slots(VehicleType) → int`. |
| 0:25–1:05 | Code | Happy path: park 1 car, unpark, compute charge. Then: lot full, vehicle not found, swap strategy. |
| 1:05–1:20 | Demo | Park 3 cars across 2 floors, unpark middle one, verify slot is free. |
| 1:20–1:30 | Trade-offs | "Lock per floor for concurrency; SlotRepository for persistence; new ParkingStrategy class for EV slots." |

**Two Strategy patterns** ship the design: `ParkingStrategy` (where to put a car: FirstFit / LeastCrowded) and `PricingStrategy` (how to charge: FlatHourly / WeekendDiscount). Zero inheritance trees. Adding "reserved EV slots" = one new strategy class. That's what you say in Step 7.

```python
class ParkingStrategy(Protocol):
    def pick(self, floors: list[Floor], kind: VehicleType) -> tuple[Floor, Slot] | None: ...

class FirstFit:
    def pick(self, floors, kind):
        for f in floors:
            free = f.free_slots(kind)
            if free: return f, free[0]
        return None
```

You wrote 50 lines of working code in 7 minutes because Steps 1–4 already drew the map.

---

## 6. Design a Pen — warm-up exercise with 5 evolutions

Before reading: spend 10 minutes with the requirements. Write your clarifying Qs, entities, where `write()` lives, how you handle refilling. Then compare to ours.

**Requirements.** A pen writes. Types: Gel, Ball, Fountain, Marker, Throwaway. Ball/Gel have a refill (with a tip and ink). Fountain has an ink directly + a nib with radius. Refills have a radius. Each pen writes its own way; some pens write the same way. Every pen has a brand and name. Some are refillable; some aren't.

| # | Approach | SRP | OCP | LSP | Duplication | What gets fixed |
|---|---|:---:|:---:|:---:|---|---|
| **E1** | Single class + `PenType` enum + `if`-tree in `write()` | ❌ | ❌ | ❌ | Low | Nothing — the god class |
| **E2** | Subclass per type (`GelPen`, `FountainPen`, …) | ✅ | ✅ | ❌ | High | SRP / OCP fixed. But `FountainPen.change_refill()` doesn't exist or raises → LSP broken. |
| **E3** | + `WritingStrategy` for `write()` behaviour | ✅ | ✅ | ❌ | Low | Code duplication in `write()` gone. LSP still broken on refill. |
| **E4** | Abstract intermediates: `RefillablePen` vs `NonRefillablePen` | ✅ | ✅ | ✅ | Low | LSP fixed — `change_refill()` only exists where it makes sense. But behaviour is welded to position in the tree. |
| **E5** | `Protocol` for capability + Strategy | ✅ | ✅ | ✅ | Medium | Flat hierarchy. "Refillable" is a `typing.Protocol` capability, not a class. Callers ask for the protocol type; mypy enforces. |

E5 example:
```python
from typing import Protocol

class RefillablePen(Protocol):
    def change_refill(self, refill: Refill) -> None: ...
    def is_refillable(self) -> bool: ...

def refill_in_bulk(pens: list[RefillablePen], r: Refill) -> None:
    for p in pens: p.change_refill(r)
# mypy errors at the call site if you pass a FountainPen.
```

**Picking which evolution.** If interviewer says "we'll add 5 new pen types over the next year" → E5 (each new type is one new class, zero edits elsewhere). E1 turns every new type into an enum edit + `if` branch. E2 forces a specific inheritance shape that may not fit (battery-powered? bluetooth-enabled?).

---

## 7. Spot the pattern from UML — 6 signature shapes

In Tier-2 design discussions you'll be handed someone else's diagram and asked "which pattern is this?" Train on the SHAPE, not the names.

| # | Signature shape | Pattern | One-line discriminator |
|---|---|---|---|
| 1 | Context holds one reference to an abstract interface; N concrete impls of that interface | **Strategy** | One open variable plugged into a context. No fan-out, no wrapping. |
| 2 | A wrapper class both *implements* an interface AND *holds* an instance of the same interface (recursive self-reference) | **Decorator** | The "wraps" arrow loops back to the same interface. Stack to compose. |
| 3 | A subject keeps a *list* of references to an abstract type and a `notify()` that fans out | **Observer** | One subject, many independent reactions. Subject blind to the observers. |
| 4 | Abstract creator with abstract `create_product()`; concrete subclasses return different concrete products | **Factory Method** | Each subclass decides which product to create. Single create method (not a family). |
| 5 | Private constructor + static `_instance` of own type + static `get_instance()` | **Singleton** | One process-wide instance, the class controls it. |
| 6 | A class that *implements* one interface but *holds* an instance of a DIFFERENT type | **Adapter** | Interface implemented ≠ type held. That's the discriminator vs Decorator. |

**Sniff test rules** when an interviewer asks:
- Fan-out from one source → Observer
- Same interface stacked → Decorator
- Different interface translated → Adapter
- One open variable, no stacking, no fan-out → Strategy
- One create method, polymorphic by subclass → Factory Method
- Private ctor + static accessor → Singleton

---

## 8. Cheat sheet — pattern decision table

| Pattern | Where it shows up | Sample problems |
|---|---|---|
| **Strategy**  | Pluggable algorithm | Splitwise (split type), Parking Lot (placement / pricing), Cab matching |
| **Factory**   | Object creation by type | Vehicle factory, payment-gateway factory, notification channel |
| **Observer**  | One event, many reactions | Order placed, ride booked, message sent |
| **Singleton** | Process-wide single resource | Config, logger, connection pool (sparingly!) |
| **Builder**   | Many constructor args | HTTP request builder, query builder, pizza builder |
| **Decorator** | Wrap to add behaviour | Beverage add-ons, middleware, retry/cache/logging |
| **State**     | Object behaves differently by mode | Order (placed → paid → shipped), TCP connection |
| **Adapter**   | Translate one interface to another | Razorpay SDK → our PaymentGateway contract |

### Phrases that score points

| Phase | Phrase |
|---|---|
| Clarifying | "Before I start, can I confirm scope?" / "What's the expected scale?" / "Is X in scope or can we defer?" |
| Mid-coding | "I'm using Strategy here so X is easy to swap later." / "This is the happy path — I'll add edges next." / "Let me print this so we can watch it work." |
| Closing | "For persistence I'd add a Repository per aggregate." / "For concurrency I'd lock per group." / "With 10 more minutes I'd add Y." |

### Checklist — glance before every interview

**Before you type a single line of code**
- [ ] Asked 3+ clarifying questions
- [ ] FR + NFR written down
- [ ] Entity list with ownership relationships
- [ ] Method signatures for top 3 classes

**While coding**
- [ ] Happy path first
- [ ] Printing as I go so it's runnable
- [ ] Narrating choices ("I'm using Strategy here because…")

**Last 15 minutes**
- [ ] Ran the code on screen
- [ ] Named 3 trade-offs (persistence / concurrency / extension)
- [ ] Proposed what I'd build next with 10 more minutes

---

## 9. Code in this class — what to run

| File | What it shows |
|---|---|
| [`code/01_parking_lot_walkthrough.py`](code/01_parking_lot_walkthrough.py) | Parking Lot end-to-end on the clock — happy path + 3 edge cases + Step 7 trade-offs printed |
| [`code/02_seven_step_template.py`](code/02_seven_step_template.py) | Blank 7-step skeleton — copy this at the start of any LLD interview |
| [`code/03_splitwise_skeleton.py`](code/03_splitwise_skeleton.py) | Splitwise with `EqualSplit` / `PercentSplit` / `ShareSplit` strategies + balance computation demo |
| [`code/04_code_review_target.py`](code/04_code_review_target.py) | Deliberately-messy code for code-review-interview practice (10 smells documented at the bottom — don't peek until you've made your own list) |
| [`code/05_interview_clock.py`](code/05_interview_clock.py) | CLI that runs a 90-min clock and prompts you each phase — `python3 05_interview_clock.py 30` for fast practice, `--silent` to skip sleeps |

All files run with plain `python3` — no pip installs.

---

## 10. Resources

### LLD / OOD practice platforms (closest to "LeetCode for design")

- **Codemia.io** — 120+ problems with UML / class-structure explanations. Largest problem bank.
- **Coudo AI** — closest to submit-and-get-feedback. Draft class diagrams, AI reviews your machine-coding code, peer review layer.
- **CodeZym** — solutions-and-practice for OOD / machine-coding with a working judge.
- **GeekTrust** — FREE LeetCode-style for LLD. You build and submit, it evaluates.
- **kumaransg/LLD on GitHub** — curated real LLD questions asked at Flipkart, Navi, ClearTrip, Udaan. Good source of prompts.

### Schema / DB design practice

- **w3resource SQL DB design** — 100 problems covering 1NF → BCNF, junction tables, surrogate keys, anomalies. Most hands-on schema resource.
- **dbdiagram.io** — the tool to actually draw schemas while practicing. Pair with any LLD prompt.
- **InterviewQuery DB-design guide** — real scenarios with entities + trade-offs.

### References

- **Refactoring.Guru** — refactoring.guru/design-patterns. Cleanest single reference for GoF.
- **faif/python-patterns** — github.com/faif/python-patterns. Canonical Python implementations.
- **LeetCode Design** (Problem 146 onward) — LRU Cache, Snake game, Twitter feed, hit counter. All LLD-shaped.
- **Grokking the System Design Interview** — for the HLD half of system+LLD hybrid rounds.

---

## 11. Sanity-check questions for yourself before any LLD interview

If yes to all five, you've got the toolkit. The interview is now about discipline, not knowledge.

- Can I name 5 design patterns and where I'd reach for each in under 60 seconds?
- Can I draw the 6 UML relationship arrows (Inheritance / Realisation / Composition / Aggregation / Association / Dependency) without looking?
- Can I write a Strategy + Protocol/ABC skeleton in under 2 minutes?
- Do I have 3 trade-off bullets memorised (persistence, concurrency, extension)?
- Do I have 3 clarifying-question categories memorised (scope, scale, out-of-scope)?

---

## 12. Honest practice plan

Pick 5 problems: **Splitwise, Parking Lot, Tic-Tac-Toe, BookMyShow, in-memory cache.**

Do each one twice:
1. **Untimed** — teaches the design space.
2. **Strict 90-minute clock** — teaches the playbook.

Most candidates only do version 1. That's why they freeze. Cross-reference your attempts on Codemia / Coudo AI / CodeZym so someone (or AI) actually looks at the code.

---

## Where this class sits in the batch

Module 3 of the LLD batch:

- LLD-13 / 14 — SOLID
- LLD-15 — Singleton
- LLD-16 — Builder
- LLD-17 — Factory family
- LLD-18 — Prototype + Adapter
- LLD-19 — Strategy + Observer
- LLD-20 — Decorator + UML
- **LLD-21 — Types of LLD interviews + how to approach (you are here)**
- LLD-22 / 23 — Tic-Tac-Toe (first end-to-end LLD problem we code together)
- LLD-24+ — Parking Lot, BookMyShow, Splitwise, Google Calendar

Next class is this class applied to a real problem. Bring the playbook.
