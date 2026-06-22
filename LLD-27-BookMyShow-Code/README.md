# LLD-27 — BookMyShow: Code (Part 2)

> From [LLD-26's design](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/tree/main/LLD-26-BookMyShow-Design) to a running box-office — built on the model we derived there: `City → Cinema → Screen → Seat`, `Show → ShowSeat` (the per-show seat carrying status + price), `Ticket` + `Payment`. LLD-26 ended on a promise: *"there are several ways to keep two users off the same seat — we'll compare them and build the best."* **This class keeps that promise** — the concurrency approaches are the headline, and we prove the winner with a race that double-books under a naive locker and books exactly once under a lock.

**Quick start:**
- `python3 code/01_bookmyshow.py` — single-file version; all demos assert green (incl. the naive-vs-locked race)
- **`python3 code/02_concurrency_demo.py`** — the **concurrency tournament**: every approach over the *same* seat-stampede + a recommendation (add `optimistic` / `pessimistic` / … to watch one interleave live; `--racers 50` to crank contention)
- **`concurrency-visualizer.html`** — open in a browser: a **visual UI** of the same race (animated users, the seat, the lock queue) under each approach, plus an interactive **soft-lock + TTL-expiry** countdown
- `cd code/bookmyshow && python3 main.py` — the layered package; every FR asserted · `… play` for the interactive shell
- Open `index.html` in a browser for the interactive class page

**Homework & discussions:** [#22 REST API](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/22) · [#23 class diagram](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/23) · [#24 the cron seat-expiry problem](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/24) · read **DDIA Ch. 7 (Transactions)**.

---

## The model carried over from LLD-26

- **`Seat`** is the *physical* seat (GOLD / DIAMOND / PLATINUM), shared across every show.
- **`ShowSeat`** is the (seat × show) **association class** — where the *per-show* `status` (AVAILABLE / LOCKED / BOOKED) and `price` live. A `Show` owns a `{seat_id → ShowSeat}` map.
- **There is no `SeatLock` entity.** The "hold" is just `ShowSeat.status == LOCKED` plus a `locked_until` stamp. The durable record is the **`Ticket`** (user + show-seats + amount + status); `Payment` is one per ticket.
- The flow is **HOLD → pay → CONFIRM** (or the hold expires, lazily). `hold()` returns a transient `Hold` *receipt* — not stored anywhere; the source of truth is each ShowSeat's status.

## Step 4 — The complete class diagram (the LLD-26 homework, with methods)

In LLD-26 you drew the boxes; coding it fills in the methods. The whole model, with the methods the code gave each:

- **Composition chain ◆** — `City ◆ Cinema ◆ Screen ◆ Seat`; `Show ◆ ShowSeat`; `User ◆ Ticket ◆ Payment`.
- **Aggregation ◇** — `Show ◇ Movie` (a show borrows a movie).
- **Methods** — `City.add_cinema()` · `Cinema.add_screen()/add_show()` · `Show.show_seat(id)` · `ShowSeat.is_lock_expired(now)` · `Ticket.calculate_amount()/cancel()`.
- **Enums** — `SeatType` (GOLD/DIAMOND/PLATINUM), `SeatStatus` (AVAILABLE/LOCKED/BOOKED), `PaymentMode`, `TicketStatus`.

**How it's wired at runtime:** `BookingService` depends on *seams* — the injected `SeatLocker` (the concurrency approach) and the `PricingStrategy` are both swappable; the two repositories are the storage seam.

### Derive the methods — "whose job is it?"

| Method | Lives on | Why |
|---|---|---|
| `price(seat)` | **PricingStrategy** | the scheme changes independently → a Strategy |
| `is_lock_expired(now)` | **ShowSeat** | "has the hold lapsed?" needs only the seat's own `locked_until` |
| `guard(show)` | **SeatLocker** | the concurrency approach — swappable so we can compare |
| `hold / confirm / cancel / available_seats` | **BookingService** | orchestration under the locker's guard |

## Step 5 — The flow & APIs

The lifecycle is **HOLD → pay → CONFIRM**, with **cancel** before the cutoff. `now: float` is injected on every state-changing call, so the TTL, the cutoff and the race are testable without sleeping.

| Internal call | Returns / raises |
|---|---|
| `available_seats(show, now)` | `list[seat_id]` (expired holds count as available) |
| `hold(show, seat_ids, user, now)` | `Hold` · raises `SeatUnavailableError` |
| `amount_due(hold)` | `float` |
| `confirm(hold, mode, now)` | `Ticket` · raises `HoldExpiredError` |
| `cancel(show, ticket, now)` | `None` · raises `CutoffPassedError` |

### The REST API (the [#22](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/22) homework)

Resources are nouns, the method is the verb, `GET` never mutates, the server owns the clock, and a **hold is its own resource** (it has an id + `expires_at`).

| Method & path | Does | Success | Errors |
|---|---|---|---|
| `GET /cities/{id}/movies` | search / filter | `200` | `404` |
| `GET /shows/{id}/seats` | seat map | `200` | `404` |
| `POST /shows/{id}/holds` | hold seats | `201` hold + `expires_at` | **`409`** taken |
| `GET /holds/{id}/amount` | amount due | `200` | `410` expired |
| `POST /holds/{id}/payment` | pay → confirm | `201` ticket | **`410`** expired · `409` used |
| `POST /tickets/{id}/cancel` | cancel | `200` | **`409`** past cutoff |

The interesting failures: two users hold the same seat → **409 Conflict**; pay after the TTL → **410 Gone**; cancel inside the 1-hour cutoff → **409/422**.

## Step 6 — The concurrency design (the headline)

**The invariant:** a show-seat is `BOOKED` by **at most one** user.

**The race — check-then-act.** Two threads run `hold(["A3"])` at once: both read `AVAILABLE`, both write `LOCKED` → two holds, two tickets. The check and the act are two steps; a second thread slips in between. **The fix:** make check-and-set one atomic step — guard the show's seats with a lock, *check all AVAILABLE, then set them LOCKED* indivisibly. The demo proves it: the same race under a `NaiveLocker` makes **2 tickets**, under a `PerShowLock` makes **exactly 1**.

### The approaches — what happens in code, in the DB, and on the UI

| # | Approach | Code / DB | On the UI |
|---|---|---|---|
| 1 | **No lock** (the bug) | check-then-act; two `INSERT`s both succeed | both users see "Booked!", one later gets a refund email |
| 2 | **In-process lock** | `with show.lock:` — one thread at a time | a spinner while it waits, then "Booked" or "seat just taken" |
| 3 | **Pessimistic row lock** | `SELECT … FOR UPDATE` locks the row; others queue | same spinner; lasts longer on hot seats (queueing) |
| 4 | **Optimistic** | `UPDATE … WHERE status='AVAILABLE'` (or a version); 0 rows = lost | instant — optimistic select, then **rolls back** on conflict |
| 5 | **DB `UNIQUE`** | `UNIQUE(show_id, seat_id)` refuses the 2nd insert | the safety net — surfaces as "seat taken" |
| 6 | **Redis lock** | `SET lock NX EX 30` across services | works with no shared DB (microservices) |
| 7 | **Soft lock / hold** | `status=LOCKED, locked_until=now+300` — the reserve-then-pay; **sits on top of** a lock | the BookMyShow **countdown**: "reserved · 4:59 left", others grey out live |

**The verdict:** in-memory → the **per-show lock**. Distributed → a **`UNIQUE(show_id, seat_id)` constraint as the floor** (can't be raced), an **optimistic update** for throughput, and a **Redis lock + TTL** when there's no single DB. **Lock granularity:** per-show is the sweet spot — global serialises the site, per-seat risks deadlock.

### Optimistic vs Pessimistic — the intuition

The whole difference is one question: do you lock *before* you start, or just *check at the end*?

- **Pessimistic = "lock the door first."** You assume a clash, grab an exclusive lock up front and hold it while you work; others **wait** (`SELECT … FOR UPDATE`, a mutex). You pay the cost as *waiting*.
- **Optimistic = "act first, check at checkout."** You assume clashes are rare, don't lock, do the work on a snapshot, and at save-time check "did anything change?" — if so, **retry** (a `version` + compare-and-set). You pay the cost as *occasional wasted work*.

**When:** high contention (the one hot seat everyone wants) → **pessimistic** (optimistic thrashes with retries). Low contention (a rarely-touched row) → **optimistic** (no lock overhead).

### Why the UNIQUE constraint alone isn't enough

A `UNIQUE(show_id, seat_id)` only fires when you **create a duplicate row (an INSERT)**. But the **hold** is an *UPDATE* of an existing `show_seat` row's `status` to `LOCKED` — no new row, so the constraint never triggers, and two users can both flip the same row (a **lost update**). That's why you still need a lock (pessimistic) or a conditional update / version check (optimistic) to make the *hold* race-safe. The UNIQUE constraint guards the *final booking*, fires at the *last second*, and is *single-row*; the locks guard the *hold*, fail *early*, and give *multi-seat atomicity*. In production you use all three as layers.

### Demo it live — the tournament (`code/02_concurrency_demo.py`)

Each approach is real, runnable code over the *same* stampede; a forced interleave makes it deterministic.

```
python3 code/02_concurrency_demo.py                # the scoreboard — ALL approaches + recommendation
python3 code/02_concurrency_demo.py --racers 50    # crank up the contention
python3 code/02_concurrency_demo.py optimistic     # run ONE, with a live interleave trace
```

The scoreboard (6 users, one seat): naive → **6 tickets** (double-book); every other approach → **1 ticket**, 5 losers. Or open **`concurrency-visualizer.html`** for the animated version + the soft-lock countdown.

## The dynamic view — the `ShowSeat` state machine

- `AVAILABLE` → (`hold()`) **LOCKED** · `LOCKED` → (`confirm()` in time) **BOOKED** · `LOCKED` → (TTL lapses) **AVAILABLE** (lazily) · `BOOKED` → (`cancel()` before cutoff) **AVAILABLE**.
- The exceptions are the illegal moves: confirm-after-expiry → `HoldExpiredError`; the lost race → `SeatUnavailableError`.

## Transactions — DDIA, Chapter 7 (the theory underneath)

The seat race is literally DDIA's **write-skew** example. The through-line: weaker isolation is faster but leaks anomalies.

- **Atomicity ≠ Isolation.** Atomicity = all-or-nothing (abortability); Isolation = concurrency-safety. A transaction can be perfectly *atomic* and still *race* another — that's an isolation failure, not atomicity.
- **The anomaly ladder** (each as a T1/T2 interleave): dirty read → read skew → lost update → **write skew / phantom**.
- **Which level stops what:** Read Committed stops dirty reads; Snapshot Isolation adds read-skew; only **Serializable** stops write skew & phantoms — implemented as serial execution, **2PL (pessimistic)**, or **SSI (optimistic)** — the same two strategies as above.

## The folder tree IS the layered architecture

```
bookmyshow/
├── enums.py · exceptions.py · config.py   # vocabulary + policy-as-data (BASE_PRICE, TTLs)
├── models/        ── DOMAIN ──   seat · movie · screen · show_seat · show · user · ticket · payment · hold
├── strategies/    ── the open variables ──   pricing (FR-5) · locking (the SeatLocker — compare approaches)
├── repositories/  ── REPOSITORY (storage seam) ──   ticket · payment
├── service.py     ── SERVICE ──   BookingService (the concurrency invariant + orchestration)
├── console.py     # the ask toolkit · cli.py ── CONTROLLER ──   render → call service → format
└── main.py        # entry — `python3 main.py` (acceptance) · `python3 main.py play`
```

The folders **are** the backend layers; **the concurrency approach is a strategy** (`strategies/locking.py`), so the comparison is real code, not just prose. Repositories are the storage seam (`save/find/exists/next_id`, injected) — the pay-once guard becomes `payments.exists_for(ticket_id)`, which in a DB is a `UNIQUE(ticket_id)` constraint.

## From engine to backend — the schema falls out of the diagram

| On the class diagram | In the schema |
|---|---|
| Each class (Show, Seat, Ticket, Payment) | a table |
| Composition ◆ (Cinema ◆ Screen ◆ Seat) | FK + `ON DELETE CASCADE` |
| **`ShowSeat`** (the association class) | the **`show_seat(show_id, seat_id, status, price, ticket_id)` table** |
| no-double-book (FR-9) | `UNIQUE(show_id, seat_id)` on booked rows |
| pay-once (FR-8) | `UNIQUE(ticket_id)` on `payment` |
| the hold | `ShowSeat.status = LOCKED` + `locked_until`, **or** a Redis key whose TTL is the hold window |

## Step 7 — Trade-offs

- **Lock granularity** — per-show is the sweet spot; per-seat risks deadlock, global kills concurrency.
- **Freeing expired holds (the [#24](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/24) problem).** A coarse cron (every 10 min) lags correctness; a per-minute cron loads the DB. The fix: don't make the cron the source of truth — use **lazy on-read expiry** (the `locked_until` timestamp, evaluated when someone looks — what our `_free_expired` does) and/or a **Redis TTL** that self-expires. Keep at most a rare, *indexed* sweep (`WHERE status='LOCKED' AND locked_until < now()`) as a cosmetic backstop.
- **In-memory vs distributed** — the per-show lock is the teaching default; production leans on the `UNIQUE` floor + optimistic updates + a Redis lock.

## The implementation — `code/01_bookmyshow.py`

Runnable with plain `python3`; every line traces to an LLD-26 decision (typed seats → enums, `LOCKED` is the third state, `ShowSeat` carries status+price, `SeatLocker` is the pluggable concurrency approach, `now: float` everywhere). The layered package in `code/bookmyshow/` splits the same engine along its seams — and `service.py` is written as a clear three-step story (`hold → confirm → cancel`).

## Files

| File | What |
|---|---|
| `index.html` | The interactive class page — complete class diagram, REST APIs + quizzes, the concurrency approaches (code/DB/UI), optimistic-vs-pessimistic, the `ShowSeat` state machine, the DDIA Ch.7 transactions quiz + anomalies diagram, schema, trade-offs |
| `code/01_bookmyshow.py` | The whole box-office in ONE file — all demos assert green, incl. the naive-vs-locked race |
| `code/02_concurrency_demo.py` | The concurrency **tournament** — all 6 approaches over one stampede, runnable individually with a live trace, ending in a recommendation |
| `concurrency-visualizer.html` | The **visual UI** — animate the race under each approach, the one-click tournament scoreboard, and an interactive soft-lock + TTL-expiry countdown |
| `code/bookmyshow/` | The same engine, **layered** — enums / exceptions / config / models (incl. `show_seat`) / strategies (`pricing` + `locking`) / repositories / `service.py` / `cli.py` / `main.py` |

## Next

**Splitwise (design + code):** from one show's seat map to a graph of who-owes-whom — balances, simplification, and split strategies (equal / exact / percentage) become the open variable.
