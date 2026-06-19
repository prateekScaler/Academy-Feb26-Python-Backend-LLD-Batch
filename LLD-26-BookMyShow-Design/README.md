# LLD-26 — BookMyShow: Design (Part 1)

> Pick seats for a show and pay — the way real ticketing works. The same playbook as Tic-Tac-Toe and Parking Lot — **align → clarify → requirements → derive entities → class diagram → schema → trade-offs** — on a problem whose star entity is the **per-show seat** and whose one unbreakable rule is **no two users get a ticket for the same seat**. **Design today, code in LLD-27.** Drawing the class diagram and designing the REST API are the homework.

**How to use this class:** open `index.html` in a browser for the interactive page (use-case diagram, click-to-reveal FRs, decision quizzes, class & ER diagrams). This README is the full content in prose.

**Companion homework (GitHub Discussions):**
- [#22 — design the REST API endpoints](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/22)
- [#23 — submit your class diagram](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/23) (see the [Class Diagram Tools Guide](CLASS-DIAGRAM-TOOLS-GUIDE.md))

---

## Step 0 — Overview: get on the same page

Before any requirement, say the system back in one or two sentences so you and the interviewer picture the same thing — exactly how we opened Tic-Tac-Toe and Parking Lot.

**The one-liner:** *"A user finds a movie, opens a show, sees its seat map, picks a few seats and pays — and the one rule that must never break is that no two users end up with a ticket for the same seat."*

A good overview names three things:
- **The actor & goal** — a user wants to watch a movie, so they pick seats for a show and pay.
- **The core noun** — what the design rotates around. Parking had the *spot*; here it's the **seat of a show**.
- **The twist** — the new thing this class adds: **concurrency**. Many users want the same seat at once, and only one may get it.

## Step 1 — Clarify

**Align first**, then the scope questions — each answer becomes an FR:

| Lens | The question |
|---|---|
| Unit | Book a whole show, or individual **seats**? · Are seats **typed** (GOLD / DIAMOND / PLATINUM) and priced differently? |
| State | Is availability **per show** (a seat booked at 7pm is free at 10pm)? |
| Hold | When a user **selects** seats, do we hold them — and for how long? What if they don't pay in time? |
| Race | What stops **two users booking the same seat** at the same instant? |
| Money | Can the **pricing scheme** change (weekend surge, offers)? |

**Feature sweep (park these):** recommendations, food combos, surge pricing, refunds, loyalty points, multiple gateways. **Defaults:** typed seats priced per type · per-show availability · a short hold that expires · no double-booking (hard invariant) · pricing a swappable Strategy · in-memory · many concurrent users per show is the named NFR.

### Who touches the system — actors before entities

Each actor's use cases become **API endpoints** in LLD-27:
- **Customer** — search / filter movies · see the seat map · select & hold seats · pay · view / cancel a booking
- **Admin / Theatre** — manage cities / cinemas / screens · schedule movies & shows · set pricing
- **System** — releases *expired* seat holds so abandoned carts free up

The **use-case diagram** draws WHO can do WHAT before any class; every oval is one use case, and each becomes a REST endpoint.

**Pre-work — design the REST API:** turn each use-case oval into a `METHOD /path` endpoint, and sketch the request/response + status codes for 2–3 — what does *"seat already taken"* or *"cancel after cutoff"* return? Submit to [Discussion #22](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/22).

## Step 2 — From a blank prompt to the MVP

### The art of it — generate the list, don't memorise it

- **Follow one actor end-to-end:** *browse → open a show → see the seat map → pick seats → hold → pay → booked.* Every step that *could differ* is a requirement.
- **Probe a few lenses:** inputs (what's bookable?), resource (seats — typed? per-show?), money (price — by type? scheme changes?), failure (taken? unpaid?), scale (how many at once?).
- **Draw the MVP line:** "does removing this change the core entities, relationships, or the hard invariant?" If no → park it.
- **Cap it at ~8–10.** More than that and you're designing features, not the core.

### Two kinds of FR — structural vs behavioural

Sort each requirement into one of two buckets, because each feeds a different part of the design:

| | 🏟️ Structural — the nouns (what *exists*) | ⚡ Behavioural — the verbs (what *happens*) |
|---|---|---|
| Describes | the static shape: things & relationships | actions & rules over time |
| **Feeds →** | the **entities & class diagram** | the **APIs, sequence & state diagrams** |

Read the structural FRs to draw **boxes**, the behavioural FRs to draw **arrows**.

### Picture it first — two diagrams that line up with the two kinds of FR

- **What exists: the seat map (structural).** A `SCREEN` with rows of typed seats — GOLD / DIAMOND / PLATINUM (colour), in a fixed grid per screen, each carrying a status *tracked per show* (a seat BOOKED for the 6pm show is AVAILABLE for the 9pm). Statuses: AVAILABLE / LOCKED (being paid for) / BOOKED.
- **What happens: the user journey (behavioural).** `Find (search & filter) → Pick a Show → Select Seats → Pay → Ticket Booked`. The invariant lives on the whole flow: *one show-seat → exactly one ticket, never two users.* How we enforce it is a design concern, not a requirement.

### The MVP requirements (each opens with the 💡 intuition — how you'd arrive at it)

**🏟️ Structural — the nouns:**

1. **FR-1** — *💡 Where does a user begin? They pick a city, so the model nests downward.* The system spans multiple **cities**; each city has multiple **cinemas**; each cinema has multiple **screens**.
2. **FR-2** — *💡 Seats aren't uniform, they're tiered → a fixed set → an enum.* A screen has many **seats**; every seat has a **type** — GOLD, DIAMOND, or PLATINUM.
3. **FR-3** — *💡 The same movie runs at 3, 6, 9pm; what you book is a show, not the movie.* A cinema plays many **movies**; a movie runs in many **shows** (a show = a movie on a screen at a start time, with language & duration).
4. **FR-4** — *💡 Where does "booked" live? Not on the seat — it depends on the show.* The **same physical seat** can be available for one show and booked for another, so each **(seat in a show)** carries its own **status** (AVAILABLE / LOCKED / BOOKED) and **price**.
5. **FR-5** — *💡 Price isn't one number — several knobs that change independently → a strategy.* A ticket's **price** depends on seat type, day of week, time of day, movie, and screen.

**⚡ Behavioural — the verbs:**

6. **FR-6** — *💡 Before booking, the user must find the show — read-side verbs.* A user can **search** a movie by name and **filter** by location, cinema, language, rating, category.
7. **FR-7** — *💡 You can't pick what you can't see.* A user can see the **seat availability** of a show.
8. **FR-8** — *💡 What survives a booking is a Ticket — user + show-seats + payment.* A user **books** seats into a **ticket** and **pays** via UPI / Credit Card / Netbanking, optionally applying a **coupon / promo code**.
9. **FR-9** — *💡 The one rule that must never break — state it as an invariant; how to enforce it is later.* No two users can ever hold a ticket for the **same show-seat** — one seat, one owner.
10. **FR-10** — *💡 Real systems have a point of no return.* A user can **cancel or update** a booking, but **not after the cutoff** — 1 hour before the show starts.

### Two valid scopes — confirm the altitude with your interviewer

Both are correct — ask which the interviewer wants:
- **A · Full real-world (what we use here):** cities → cinemas → screens → shows → per-show seats, plus search & filter across a catalogue. Richer; best when they want the *whole product*.
- **B · Lean single-cinema:** drop the city / cinema / search layer. Just Movie · Screen · typed Seat · Show · per-show seat state · Booking · Payment — best when they want *depth on seat state & concurrency*, not breadth.

Either way the heart is identical: the per-show seat + "one seat, one ticket." The full scope just stacks the geography and discovery layer on top.

### Non-functional requirements (the "non-FRs")

FRs say *what*; NFRs say *how well* — qualities, not features. They rarely add classes.
- **Highly concurrent** — many users hit the same show at once. For requirements we commit only to the invariant (FR-9); *how* we lock seats is a design concern.
- **Responsive reads** — the seat map is read far more than written; reads stay cheap.
- **Config, not code** — prices and seat layout live as data; a new pricing rule is one new strategy.
- **Extensible payments** — a new payment mode plugs in without touching the booking flow.

## Step 3 — Entities: derive them round by round

Same drill as Tic-Tac-Toe & Parking — read each FR, ask *"what are the core nouns?"*, and the obvious classes & enums fall out. The one subtle entity we arrive at in a **second round**.

**🎯 Round 1 — the obvious nouns:**
- **FR-1 donates:** `City` · `Cinema` · `Screen` — three classes in a composition chain.
- **FR-2 donates:** `Seat` (a value — number + type) · `SeatType` **enum** (a fixed set → enum, not a string).
- **FR-3 donates:** `Movie` · `Show` (the thing you book — not the movie).
- **FR-5 donates:** `PricingStrategy` — the open variable (several independent knobs → a Strategy).
- **FR-8 donates:** `User` · `Ticket` (the durable record) · `Payment` · `PaymentMode` enum · `TicketStatus` enum.

**🧠 Round 2 — the subtle one (think harder).** FR-4 said availability is *per-show* — that doesn't hand you a noun. Seat A1 is free for the 6pm show but booked for the 9pm. So where do that per-show **status** AND **price** live?

> **Decision:** *its own class — `ShowSeat` = (seat × show), carrying status + price.* A boolean on `Seat` is wrong (the seat is shared across shows); a bare `{seat → status}` map on `Show` has nowhere clean for the per-seat price; it can't live on `Ticket` because the status must exist *before* any ticket does. `SeatStatus` (AVAILABLE / LOCKED / BOOKED) is the enum it carries — `LOCKED` is the third state a bool can't hold.

**Why `ShowSeat` earns its own class — the heuristic:**
- A pairing earns a class when the pairing itself **carries data** — seat alone has a type, show alone has a time, seat × show has *status + price*, brand-new data belonging to neither parent.
- It has a **lifecycle** — AVAILABLE → LOCKED → BOOKED; a plain map value can't own that transition cleanly.
- It has **identity** — a `Ticket` points at specific `ShowSeat`s (a foreign key), not at "seat 12 of show 5" reconstructed every time.
- **Contrast Parking:** a `Spot`'s status lived ON the spot — no second dimension. Here the *show* is that second dimension, pushing the pairing into its own object. Same three-way test, different answer because the FR changed.
- **When NOT to:** if a seat had only a free/taken bool and no per-show price, a map on `Show` would do — it's the *price* + the *lock lifecycle* that tip it over.

**And the record?** The durable one is the `Ticket` (user + show-seats + payment + status). The transient "hold" isn't a separate entity here — it's just the `LOCKED` status on the `ShowSeat` while a user pays.

### Everything we derived

| Entity | Kind | From |
|---|---|---|
| `City` · `Cinema` · `Screen` | classes | FR-1 — the composition chain |
| `Seat` | value | FR-2 — physical seat (number + type) |
| `SeatType` | enum | FR-2 — GOLD / DIAMOND / PLATINUM |
| `Movie` · `Show` | classes | FR-3 — the thing you book is the show |
| **`ShowSeat`** | class | **FR-4 (round 2) — per-show seat: status + price** |
| `SeatStatus` | enum | FR-4 — AVAILABLE / LOCKED / BOOKED |
| `PricingStrategy` | strategy | FR-5 — the open variable |
| `User` · `Ticket` · `Payment` | classes | FR-8 — user, durable record, money |
| `PaymentMode` · `TicketStatus` | enums | FR-8/10 |

## Step 4 — The class diagram

Built on the canonical BookMyShow model — `City → Cinema → Screen → Seat`, and the star: **ShowSeat** (the seat × show pairing). Every box traces to an FR; every diamond answers the lifetime question.

- **Composition chain ◆** — `City ◆ Cinema ◆ Screen ◆ Seat` (created together, die together).
- **Aggregation ◇** — `Movie ◇ Show` (a show borrows a movie).
- **`Show ◆ ShowSeat`** — a show owns its per-show seats (composition); `ShowSeat ⇢ Seat` references the physical seat.
- **`User ◆ Ticket ◆ Payment`** — a user holds tickets; a ticket has exactly one payment; `Ticket ⇢ Show` and `Ticket ⇢ ShowSeat[]`.
- **Enums:** `SeatType` (GOLD/DIAMOND/PLATINUM), `SeatStatus` (AVAILABLE/LOCKED/BOOKED), `PaymentMode` (UPI/CREDIT_CARD/NETBANKING), `TicketStatus` (BOOKED/CONFIRMED/CANCELLED).

**Homework:** draw it from the FRs — mark composition ◆ (`City ◆ Cinema ◆ Screen ◆ Seat`; `Show ◆ ShowSeat`; `User ◆ Ticket ◆ Payment`) vs aggregation ◇ (`Movie ◇ Show`), and the multiplicities (a show has many ShowSeats; a ticket holds 1+ ShowSeats; a ticket has exactly one payment). Submit → [Discussion #23](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/23) (tools: [Class Diagram Tools Guide](CLASS-DIAGRAM-TOOLS-GUIDE.md)).

## Step 4b — Classes → schema: the "class or table?" question

"Should `ShowSeat` be a class, or just a join table for the many-to-many between Show and Seat?" — the answer is **both, at two layers**, and that's not a cop-out:

- A class diagram and a schema are the **same model** — objects in memory vs rows on disk.
- **Show ↔ Seat is many-to-many** — one show has many seats; one seat appears in many shows.
- A *plain* M:N with no extra data → no class needed; the DB gets a bare **join table** of two FKs.
- But this pairing **carries its own data** (status + price). That tips it over: in OOP it's an **association class** (`ShowSeat` is a real class), and in the DB it's an **associative table** `show_seat(show_id, seat_id, status, price)`. Same entity, two layers.

**The rule:** a many-to-many *with attributes* ⇒ promote the relationship to a first-class thing — a class in code, a table-with-columns in the DB.

### First, derive the relationships — where does each FK go?

The rule that keeps firing: **the FK lives on the "many" side**, and an **M:N with its own data becomes a table**.
- A city has many cinemas (1:N) → FK `cinema.city_id` (on the many side). Same for `screen.cinema_id`, `seat.screen_id`.
- `Show ↔ Seat` is **many-to-many** → becomes the `show_seat` associative table holding `show_id` + `seat_id` **plus** its own `status` & `price`.
- A ticket has many show_seats but each show_seat is sold once → 1:N → FK `show_seat.ticket_id` (nullable until booked).
- `Ticket ↔ Payment` is 1:1 → FK `payment.ticket_id` + `UNIQUE(ticket_id)`.

### Deriving the schema — the rote rules

- **Each class → a table**; each field → a column.
- **1:N → a foreign key on the many side** (`cinema.city_id`, `screen.cinema_id`, `seat.screen_id`, `show.movie_id`, `ticket.user_id`).
- **M:N → an associative table**; M:N *with data* → that table carries the extra columns (the association class) — that's `show_seat`.
- **Enum →** `VARCHAR` + `CHECK (... IN (...))` (or a small lookup table).
- **An invariant → a constraint.** No-double-book (FR-9) = `UNIQUE(show_id, seat_id)` on `show_seat`; pay-once = `UNIQUE(ticket_id)` on `payment`. The DB enforces what application code would otherwise race on.

The ER diagram falls out: the geography 1:N chains are plain FKs; only `show ↔ seat` is M:N, and because the pairing carries status + price it resolves into the `show_seat` table (the ShowSeat class), not a bare join.

## Step 5 — The booking flow & concurrency (a peek)

The booking flow is a **hold** that becomes a booking or expires (`HOLD → pay → CONFIRM`), and the one invariant is **one show-seat → one ticket**.

**The danger, in one line:** two requests both read seat A1 as free, both write "booked" → two tickets for one seat. The fix is always the same idea — make "check it's free *and* take it" a single, un-interruptible step. *How* you do that is the choice:

- **1 · Lock in the code** — a mutex around the seat update; one thread at a time. Simple, but one server only. *(Python `threading.Lock`)*
- **2 · Pessimistic DB lock** — `SELECT … FOR UPDATE` locks the seat row until commit; the second request waits. *(Vlad Mihalcea)*
- **3 · Optimistic concurrency** — `UPDATE … WHERE status='AVAILABLE'` (or a version column), check rows-affected; the loser retries. Scales when conflicts are rare.
- **4 · DB constraint / Redis lock** — let the DB refuse the 2nd booking (`UNIQUE(show_id, seat_id)`), or a Redis lock with a TTL across many services. *(Redis Redlock)*
- **5 · Reserve-then-pay (a hold)** — mark the seats `LOCKED` for a few minutes while the user pays (the `HOLD → pay → CONFIRM` flow); unpaid holds expire and free up. What BookMyShow actually does — on top of one of the locks above.

**Your turn — think about it:** which would *you* pick for BookMyShow, and why? It depends on scale — one server → a code lock; one database → a row lock or `UNIQUE` constraint; many servers → optimistic updates or a distributed lock, usually behind a hold. **We compare all of them and build the winner live in LLD-27.**

## Step 6 — Trade-offs to say out loud

The design-level forks today (the *concurrency* trade-offs — lock granularity, holds & TTLs, oversell — come in LLD-27):
- **ShowSeat rows: when?** Pre-generate every `ShowSeat` when a show is created (simple reads, more rows) vs create on first touch (lean, more logic).
- **Pricing: object or data?** A `PricingStrategy` object vs rules-as-data in a table — depends how often the rules change.
- **Search & filter at scale.** Name/location/language filters need indexes — or a search service. Reads dwarf writes; optimise the read path.
- **Cancellation & cutoff.** A cancelled `ShowSeat` returns to `AVAILABLE`; refunds run through `Payment`; the 1-hour cutoff guards the booking lifecycle.

## Further reading — how the real systems do it

The "two people, one seat" problem is the canonical **write-skew / phantom** race; every booking system solves it with *hold + atomic check-and-set*:
- [How to do distributed locking](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html) — Martin Kleppmann (the Redlock critique).
- [Distributed Locks with Redis (Redlock)](https://redis.io/docs/latest/develop/use/patterns/distributed-locks/) — Redis docs.
- [PostgreSQL: Explicit Locking](https://www.postgresql.org/docs/current/explicit-locking.html) — `SELECT … FOR UPDATE`.
- [Designing Data-Intensive Applications, Ch. 7](https://dataintensive.net/) — write skew & phantoms (the two-people-one-seat textbook example).
- [Stripe: Idempotency](https://stripe.com/blog/idempotency) — "pay exactly once" under retries.

## Next

**LLD-27 — BookMyShow: Code.** Build the model live, then make "two users, one seat" *impossible* — compare the locking styles above and implement one, with a demo where two threads race for the same seat and exactly one wins. Draw the class & schema diagrams before then.
