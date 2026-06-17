# LLD-25 — Parking Lot: Code (Part 2)

> Steps 4–7 of the playbook. From [LLD-24's diagrams](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/tree/main/LLD-24-ParkingLot-Design) to a running lot: reference class diagram → APIs → live build → **the engine mapped onto the backend stack from Module 1** (layers, REST, schema) → trade-offs. Where Tic-Tac-Toe was a CLI toy, a parking lot is a *system* — so this is the round that earns `repositories/` and a database schema.

**Quick start:**
- `python3 code/01_parking_lot.py` — single-file version; seven demos assert green
- `cd code/parkinglot && python3 main.py` — the layered package; every FR asserted
- `cd code/parkinglot && python3 main.py play` — interactive booth (simulated clock)
- Open `index.html` in a browser for the interactive class page (diagrams, sequence + state machine, quizzes)

---

## Step 4 — The reference class diagram

**Read it off the diamonds, don't invent it.** Every box traces to an FR; every diamond answers the lifetime question (*can the part outlive the whole, or be shared?*).

- **Game-analogue orchestrator:** `ParkingLot` holds `floors`, the two strategies, and the two record stores.
- **Composition chain ◆** — `ParkingLot ◆ Floor ◆ Spot`: created together, destroyed together; nothing escapes its owner.
- **Aggregation ◇** — `ParkingLot ◇ ParkingStrategy`, `ParkingLot ◇ PricingStrategy`: the lot *borrows* both; they're stateless and shareable across many lots. The two «abstract» boxes are the **zero-edit plug-in points** (`NearestToExit`, `WeekdayPeak` dock below them).
- **Realisation ▷** — `FirstFit`/`LeastCrowded ▷ ParkingStrategy`, `TieredHourly`/`WeekendFlat ▷ PricingStrategy`.
- **Dependencies ⇢** — the lot *creates* tickets (holds them in `_active`); a `Payment` *pays for* exactly one `Ticket` (1:1); a `Ticket` *records* a `Vehicle`; `Spot` uses the enums.
- **The enums box is the LLD-24 punchline** — `SPOT_SIZE_FOR` (vehicle→size) is *one dict*, so cross-parking policy never touches a class.

**"ids, not live refs — outlives the stay":** a `Ticket` stores the spot's *id* (`"F1-M0"`), not a live `Spot` object. A ticket is a *record* — billed, audited, and possibly sitting in a database long after the car has driven off and the in-memory `Spot` is gone. A live reference would pin memory and break the instant you serialise or restart. Records point by id, exactly like a database **foreign key**.

### Derive the methods from the FRs — "whose job is it?"

The diagram shows the *fields* first; the methods come from reading each FR as a verb:

| Method | Lives on | Why |
|---|---|---|
| `fee(...)` | **PricingStrategy** | FR-8 — the pricing scheme changes independently → it's the open variable → a Strategy |
| `can_fit(...)` | **Spot** | FR-2/4 — the rule needs the spot's *size* AND *status*; both live on Spot, so the rule does too (no feature envy) |
| `pick(...)` | **ParkingStrategy** | FR-3/8 — placement is a *cross-floor* policy that changes → a Strategy, not a method on Floor |

**And what arguments?** The signature is half the design:

- `pick(floors, vehicle)` — exactly the candidate floors + the vehicle (to size against). **Not** the whole `ParkingLot` (Interface Segregation — give it the narrowest input it can't misuse).
- `fee(size, seconds)` — bill the **resource you occupied** (the spot's size), not the vehicle; and take the **raw unit** (seconds), letting the pricing rule own the rounding. *Why seconds, not hours?* "Hours" pre-bakes a rounding decision that belongs to the strategy; different schemes round differently (`TieredHourly` rounds up, a per-minute scheme wouldn't); and `now - entry_time` is already seconds. Push precise data inward — the same instinct as injecting the clock.

## Step 5 — APIs

### The nine functional requirements

1. One or more **floors**, each a fixed set of **spots**.
2. Every spot has a **size** (S/M/L); every vehicle type maps to one spot size (bike→S, car→M, truck→L).
3. A vehicle entering is assigned a free spot; the driver gets a **ticket** (vehicle, spot, entry time).
4. No suitable spot free → the vehicle is **turned away**.
5. A leaving vehicle pays a **fee** from duration and spot size.
6. The moment a vehicle leaves, its spot is **free**.
7. The lot can **report** free spots per size, per floor and in total.
8. The **assignment policy** and the **pricing scheme** change independently.
9. A ticket is **paid exactly once, before exit**; the gate opens only for a paid ticket (cash/card/UPI).

### Method signatures — and why not the alternative

- `park(vehicle, now) → Ticket | None` — **a full lot is an *expected outcome*, not a contract violation** (the LLD-24 flip): return a value, not an exception. The `Ticket | None` type forces every caller to handle "full".
- `pay()` and `exit_lot()` as **two methods**, not `pay_and_exit()` — they're two real events with a meaningful in-between state (*paid but not yet exited*) that the gate checks before lifting the barrier. Fusing them hides that state and blocks "pay online, drive out later".
- **Accept ids, not objects** — `pay(ticket_id, …)`, not `pay(ticket, …)`; the caller (a controller, later) holds a string from the wire, not a live object.
- `now: float` everywhere — the clock is **injected** so tests assert exact fees ("park at 0, exit at 2h → ₹180") without sleeping.

### The REST API (turning use cases into endpoints)

Conventions: resources are nouns, the HTTP method is the verb; `GET` never mutates; every contract violation maps to one status code; the **server owns the clock** (`now` is never sent by the client).

| Method & path | Does | Request | Success | Errors |
|---|---|---|---|---|
| `POST /tickets` | issue a ticket on entry | `{vehicle: {plate, type}}` | `201` · the ticket | `200 {ticket: null}` when full |
| `GET /tickets/{id}/due` | amount owed so far | — | `200 {amount}` | `404` unknown ticket |
| `POST /tickets/{id}/payments` | pay (exactly once) | `{method}` | `201` · the payment | `404` unknown · `409` already paid |
| `POST /tickets/{id}/exit` | leave; the gate opens | — | `200` · the closed ticket | `402` unpaid · `404` unknown/used |
| `GET /availability` | free spots (filterable) | `?size=&floor=` | `200` · counts | — |
| `PATCH /spots/{id}` | admin: set a spot's status | `{status}` | `200` · the spot | `404` unknown spot |

Key calls explained: **exit is a state transition** (`POST …/exit`), *not* `DELETE` — the ticket is kept for audit. A **full lot** returns a normal `200 {ticket: null}` (or `409`) — it's expected, not a 5xx. **Pay-twice → 409**, **exit-before-pay → 402**, **availability** filters go in the query string (not the path).

### Design decisions interviewers probe

- **`status: SpotStatus` enum, not `occupied: bool`** — there's a *third* state, `OUT_OF_ORDER` (oil spill, broken sensor), a bool can't hold. Use an enum even at two states (the `GameStatus` lesson).
- **ID generation** — auto-increment `T-0001` is readable and fine for one in-memory lot; switch to UUID/hybrid once there are distributed gates. Pros/cons:
  - *Auto-increment* — ✅ short, readable, sortable · ❌ needs a lock, breaks across gates, leaks your volume.
  - *UUID* — ✅ globally unique, distributed-safe, hides volume · ❌ long, not time-sortable.
  - *Timestamp* — ✅ sortable · ❌ collides within a tick, clock-skew issues.
  - *Hybrid* `TKT-{ts}-{short-uuid}` — readable + sortable + collision-safe; the usual production compromise.
- **`repo.find(id)` returns `None`, doesn't raise** — absence is data; the *service* decides when "missing" is a violation.
- **`pay()`/`exit_lot()` granularity** — two methods for the two events and the paid-but-parked state between them.

## Step 6 — Patterns & edge cases

- **Two independent Strategies from minute one** — `ParkingStrategy` (FirstFit / LeastCrowded) and `PricingStrategy` (TieredHourly / WeekendFlat); they vary independently, which is exactly why they're two objects, not one "ConfigStrategy".
- **Policy as data** — `SPOT_SIZE_FOR` (vehicle→size) and the tiered `RATES` table; new vehicle types or rates are data edits.
- **Two record entities** — `Ticket` (the visit) and `Payment` (frozen — money doesn't mutate).

| Edge case | What we do |
|---|---|
| Move on a full lot | `park()` returns `None`; the gate display says "FULL" (not an exception) |
| Exit before paying | `exit_lot()` raises `UnpaidExitError` |
| Paying twice | `pay()` raises `AlreadyPaidError` |
| Unknown / reused ticket | `InvalidTicketError` |
| 20-minute stay | billed the 1-hour minimum; hours round UP |
| Spot marked `OUT_OF_ORDER` | never allocated; excluded from free counts |
| Vehicle exits (paid) | spot free *immediately* for the next `park()` |
| Size matching | a truck never lands in a bike spot — `can_fit` guards even a buggy strategy |

## The folder tree IS the layered architecture

```
parkinglot/
├── enums.py · exceptions.py · config.py   # vocabulary + policy-as-data
├── models/        ── DOMAIN ──   vehicle · spot · floor · ticket · payment
├── strategies/    ── the 2 open variables ──   parking · pricing
├── repositories/  ── REPOSITORY (storage seam) ──   ticket · payment
├── service.py     ── SERVICE ──   ParkingLot (rules + orchestration)
├── console.py     # the ask toolkit, carried byte-for-byte from TTT
├── cli.py         ── CONTROLLER ──   parse → call service → format
└── main.py        # entry — acceptance asserts · `play`
```

The folders **are** the backend layers, named in advance: `cli.py` → controller, `service.py` → service, `repositories/` → storage seam, `models/` + enums + config → domain.

### The one real upgrade over the single file: dicts become repositories

A repository is a small object whose only job is *"where the data lives"* — `save` · `find` · `exists` · `delete`, and nothing else knows whether a dict, a file, or a database sits underneath.

- **Tic-Tac-Toe had none** — a game is played and thrown away; no data outlives the call.
- **A parking lot is a system** — tickets and payments are looked up, billed, audited, and must survive a restart. The moment data outlives a single call, you have *storage* — and storage deserves its own object.

The bare `_active`/`_payments` dicts inside the service become injected repository objects, so the **pay-once guard becomes a query**: `ticket_id in self._payments` → `self.payments.exists(ticket_id)` — the service can't tell a dict from a `SELECT 1 … WHERE ticket_id = ?`. In a DB that invariant is a `UNIQUE(ticket_id)` constraint.

**How to design a repository:**
- **One per aggregate root** — `TicketRepository`, `PaymentRepository`; not one giant DAO.
- **A tiny, intention-revealing contract** — `save(entity)` · `find(id) → entity | None` · `exists(id) → bool` · `delete(id)` · `next_id()`.
- **Speak the domain, not the database** — methods take/return domain objects (`Ticket`), never rows or SQL; the repo translates.
- **Absence is data, not an error** — `find()` returns `None`; the service decides when missing is a violation.
- **No business logic inside** — it stores and retrieves; rules (pay-once, fees) live in the service.
- **Injected, not `new`-ed inside** — a fake in-memory repo for tests, a DB-backed one for prod, service unchanged.

## The live build — five stages, leaves first

1. **Vocabulary** — enums, `SPOT_SIZE_FOR`, the three exceptions, `Vehicle` (frozen), `Spot` (two facts + `can_fit`).
2. **Records & containers** — `Floor` (identity + free-counts), `Ticket`, `Payment` (frozen). Records store *ids*, not live objects.
3. **The two open variables** — `ParkingStrategy` (FirstFit / LeastCrowded) and `PricingStrategy` (TieredHourly / WeekendFlat); each new policy is one class.
4. **The orchestrator** — `ParkingLot.park / pay / exit_lot / amount_due / available / per_floor`. Each command is *guard → act → record*.
5. **Demos** — every FR driven: happy path, lot-full → `None`, the contract violations, `OUT_OF_ORDER`, per-floor availability, strategy swap, pricing swap.

## The dynamic view — sequence diagram & lifecycle

A class diagram is a photo (who exists); a **sequence diagram** is the film (who calls whom, in order).

- **`park()` collaboration:** Driver → Gate → `lot:ParkingLot` → `strategy.pick(floors, vehicle)` → `spot.occupy()` → `«create» Ticket` → `tickets.save()` → return the ticket. An `alt` fragment covers *lot full → None*.
- **Deriving one:** pick one use case → list participants left-to-right → walk the verbs as messages → mark activation bars → draw the returns that carry something → `«create»` births a lifeline, `✗` ends one → branches become `alt`/`opt`/`loop` fragments.

**Finding the lifecycle, two ways:**
- **Memory lifecycle** (read off the diamonds): composition parts are born with the whole (no `«create»`); the records are the interesting ones — `Ticket` is `«create»`d at `park()` and retired at `exit()`; injected strategies/repositories predate the use case.
- **State lifecycle** (a state machine): `Ticket` walks **ISSUED → PAID → EXITED**.

**The payoff:** the state machine and the three exceptions are the *same picture* — exit-before-pay, pay-twice, and touching a gone ticket are the **three illegal transitions** (`UnpaidExitError`, `AlreadyPaidError`, `InvalidTicketError`). When asked "what can go wrong?", you read off the arrows your diagram *doesn't* have.

## From engine to backend (Module 1 reconnects)

- **Controller** (`cli.py` analogue) — parse input, call the service, format the result, map exceptions to status codes (unpaid→402, unknown→404, double-pay→409).
- **Service** — the `ParkingLot` class: business rules + orchestration; no HTTP, no SQL.
- **Repository** — the storage seam; in-memory dicts today, a DB tomorrow, service untouched.
- **Domain** — Spot, Floor, Ticket, Payment, enums; pure objects, testable with zero setup.

### The schema falls out of the class diagram

Each class becomes a **table**; each composition diamond and each "id, not a live ref" becomes a **foreign key**.

| On the class diagram | In the schema |
|---|---|
| Each class (Floor, Spot, Ticket, Payment) | a table; attributes → columns |
| Composition ◆ (Lot ◆ Floor ◆ Spot) | FK + `ON DELETE CASCADE` (the part dies with its owner) |
| "ids, not live refs" (`Ticket.spot_id`) | that field *is* the FK column |
| enums (SpotSize, SpotStatus, …) | `VARCHAR` + `CHECK (... IN (…))` |
| pay-once (FR-9) | `UNIQUE(ticket_id)` on `payment` — the DB enforces what `exists()` did in memory |
| Strategies | **not persisted** — behaviour chosen at config |
| Vehicle (frozen) | embedded as `vehicle_plate` + `vehicle_type` on `ticket` |

Cardinalities: `floor ↔ spot` is **1:N** (the FK `floor_id` lives on the *many* side, `spot`); `ticket ↔ payment` is **1:0..1**, enforced by `UNIQUE(ticket_id)`.

## Step 7 — Trade-offs

- **Concurrency (two gates).** Two gates calling `park()` at the same instant hit a `pick()` → `occupy()` **check-then-act** race for the last spot. The fix: one lock **per floor** + re-check the spot under the lock + retry the next candidate — not one lock around the whole lot. (We set concurrency aside in the MVP and go deep on it in the **BookMyShow** case study, where the seat race is the main event.)
- **Persistence.** Replay the open tickets to rebuild occupancy on restart — possible *only because* records store ids, not live refs.
- **Connect-Four-style reuse** and **BookMyShow's hold-with-TTL** (the reservation `SeatLock`) are the natural next steps.

## The implementation — `code/01_parking_lot.py`

Runnable with plain `python3`; seven demos, all assert green. Every line traces to an LLD-24 decision:

| Code | LLD-24 decision |
|---|---|
| `VehicleType` + `SpotSize` + `SpotStatus` enums | FR-2/6 — three named sets; `OUT_OF_ORDER` is the third state a bool can't hold |
| `SPOT_SIZE_FOR = {BIKE: SMALL, CAR: MEDIUM, TRUCK: LARGE}` | FR-2 — policy as data; scooters/buses/cross-parking are dict edits |
| `Spot(spot_id, size, status)` + `is_free()`/`can_fit(v)`/`occupy()`/`free()` | FR-2/6 — the Cell analogue: two facts + the rules relating them |
| `Floor(number, spots)` + `free_spots`/`free_count` | FR-1 + FR-7 — identity + its own queries |
| `Ticket` + frozen `Payment` (ids, not live refs) | FR-3/9 — two records that outlive the stay; money doesn't mutate |
| `park() → Ticket \| None` | FR-4 — full lot is expected flow; the exception-criterion flip |
| `pay()` → `AlreadyPaidError`; `exit_lot()` → `UnpaidExitError`/`InvalidTicketError` | FR-9 — contract violations DO raise |
| `ParkingStrategy` (FirstFit / LeastCrowded) | FR-8 — placement open variable |
| `PricingStrategy` (TieredHourly / WeekendFlat) | FR-5 + FR-8 — bills the spot size; independent axis |
| `now: float` parameters everywhere | clock injection — demos assert exact fees without sleeping |

## Files

| File | What |
|---|---|
| `index.html` | The interactive class page — reference diagram (skeleton → derive methods → complete), API & design quizzes + API doc, structure, staged build, sequence diagram + lifecycle/state-machine, backend mapping, schema-from-the-diagram quizzes, trade-offs |
| `code/01_parking_lot.py` | Complete working lot in ONE file (read top to bottom) — all demos assert green |
| `code/parkinglot/` | **The same engine, organised into the layered tree** — `enums.py` / `exceptions.py` / `config.py` / `models/` (domain) / `strategies/` / `repositories/` (the storage seam) / `service.py` / `console.py` / `cli.py` / `main.py`. Run `cd code/parkinglot && python3 main.py` (acceptance asserts) or `python3 main.py play` (interactive booth, simulated clock) |

## Next

**BookMyShow (design + code):** a parking lot where every car wants the same spot at the same second — the reservation hold (SeatLock + TTL) graduates from a table row to the main character, and concurrency becomes the headline.
