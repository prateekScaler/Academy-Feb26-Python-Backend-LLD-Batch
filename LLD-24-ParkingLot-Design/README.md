# LLD-24 — Parking Lot: Design (Part 1)

> The most-asked machine-coding problem, run through the same playbook as Tic-Tac-Toe: **align → actors → FR sentences → derive every class from its requirement → ownership.** Two Strategies appear from minute one, one decision *flips* versus TTT (when is failure an exception?), and concurrency stops being theoretical. **Design today, code in LLD-25.** Drawing the class diagram is the homework — [Discussion #21](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/21); the REST-API design is [Discussion #20](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/20).

---

## Recap — what carries over from TTT

- **The three-way test** (class / field / enum) — run it on every noun; answers differ per problem.
- **The lifetime question** ("can the part outlive the whole, or be shared?") — decides every diamond.
- **The open variable** — whatever the interviewer will ask to swap is a Strategy today. TTT had one; count the parking lot's.
- **The record entity** — TTT's `moves` list bought undo + save/replay; the parking analogues are the **Ticket** and the **Payment** (fee, audit and persistence all read from them).

## Step 1 — Clarify

**Align first:** *"Multi-floor lot, vehicles in and out, pay by time at exit — same page?"* Then the scope questions; each answer becomes an FR:

1. Which vehicle types? Bike / car / truck?
2. Are spots sized per type? Can a bike take a car spot?
3. Floors — one or many?
4. Pricing — hourly? per type? can the scheme change?
5. What happens when the lot is FULL?
6. How does the driver pay — and when?
7. One entry gate or several? (the concurrency question)

**Feature sweep** (offer, then park in future scope): monthly passes, valet, reservations (a hold with a TTL — BookMyShow's seat lock), EV charging, display boards.

**Defaults:** vehicles bike/car/truck and spots small/medium/large — *two separate enums* related by one mapping (bike→small, car→medium, truck→large), so "can a bike take a car spot?" is a policy change in a dict, never a code change; multiple floors with fixed spot mixes; tiered hourly pricing per spot size (first hour, then per extra hour: 50/80, 80/100, 100/120), swappable; full lot → turned away; pay at exit, exactly once (cash/card/UPI); ONE gate for the MVP (multiple gates = the named Step-7 headline).

**Actors** (each use case becomes an LLD-25 API endpoint): **Customer** — get ticket, check due, pay, exit · **Attendant/gate** — check free spots, issue tickets, collect payment, verify paid before lifting the barrier · **Admin** — CRUD on lots/floors/spots, mark a spot *out of order*, swap strategies.

## Step 2 — Functional requirements (complete sentences)

1. The parking lot has one or more floors, and each floor has a fixed set of parking spots.
2. Every spot has a size — small, medium, or large — and every vehicle type maps to exactly one spot size it can use (bike→small, car→medium, truck→large).
3. A vehicle entering the lot is assigned a free spot of its size, and the driver receives a ticket recording the vehicle, the spot, and the entry time.
4. If no suitable spot is free, the vehicle is turned away at the gate.
5. A vehicle leaving the lot surrenders its ticket and pays a fee computed from the parked duration and the size of the spot it occupied.
6. The moment a vehicle leaves, its spot becomes free for the next vehicle.
7. The lot can report the number of free spots per size — per floor and in total.
8. The spot-assignment policy and the pricing scheme can each change independently of everything else.
9. A ticket is paid exactly once, before exit — the gate opens only for a paid ticket. Payment can be cash, card, or UPI.

**NFRs:** in-memory; one gate thread for the MVP; rates, layout and the vehicle→size mapping as configuration in one place; a new policy or scheme is one new class, never an edit.

## Step 3 — Entities: every FR donates something

| Entity | Kind | From | One-line why |
|---|---|---|---|
| `ParkingLot` | class | FR-1/3/4/6 | Orchestrator: park / pay / exit / availability; owns floors, borrows strategies |
| `Floor` | class | FR-1 + FR-7 | Identity (number) + its own queries (`free_count`) — **unlike TTT's rows**, which stayed bare lists because nothing addressed them by name |
| `Spot` | class | FR-2/6 | **The Cell analogue:** two facts (size, status) + the rules relating them (`is_free`, `can_fit(vehicle)`) |
| `VehicleType` / `SpotSize` / `SpotStatus` | enums | FR-2/6 | Three small named sets. `SpotStatus` has the third state — **OUT_OF_ORDER** — that `occupied: bool` can't hold (the GameStatus lesson again: count the real states before reaching for a bool) |
| `SPOT_SIZE_FOR` | mapping | FR-2 | vehicle→size as **policy as data** — don't fuse two concepts because they correlate; cross-parking rules and new vehicle types (scooter, bus) are dict edits |
| `Vehicle` | frozen dataclass | FR-2 | Plate + type travel together; no behaviour |
| `Ticket` | dataclass | FR-3/5 | The event record — fee, audit, persistence all read from it; stores spot *id*, not a live ref (tickets outlive sessions) |
| `Payment` / `PaymentMethod` | dataclass + enum | FR-9 | The second record — one per ticket; method is data, not subclasses (they don't *behave* differently in our scope) |
| `ParkingStrategy` | ABC | FR-8 | `FirstFit` (minimise walking) / `LeastCrowded` (spread congestion) — placement is a cross-floor decision, so it can't live on `Floor` |
| `PricingStrategy` | ABC | FR-5 + FR-8 | `TieredHourly` / `WeekendFlat` — **bills the spot size, not the vehicle** (you pay for the resource you occupied); varies independently of placement |
| `park() → Ticket \| None` | signature | FR-4 | **The flip vs TTT:** a full lot is an *expected outcome*, not a contract violation — no exception |
| `InvalidTicketError` / `AlreadyPaidError` / `UnpaidExitError` | exceptions | FR-9 | Bad ticket, double payment, unpaid exit — contract violations DO raise; FR-4's criterion, other side |

**The exception criterion (FR-4's real lesson):** whose fault is it? TTT's illegal move broke the rules of the conversation → raise. A full lot on a Tuesday is nobody's mistake → `Ticket | None`. The reference design from the Aug-25 batch raises `NoSpotAvailableException` here — defensible! — but state your criterion either way.

**Ownership:** Lot ◆ Floor ◆ Spot (a composition chain — nothing escapes its owner); Lot ◇ both strategies (stateless, one instance can serve 50 lots); Ticket–Vehicle/Spot and Payment–Ticket are plain associations (records store ids and outlive the visit; the pay-once rule makes Payment–Ticket exactly 1:1).

### Where today stops — on purpose

Full cast of classes, each traced to its FR, ownership answered. **Deferred to LLD-25:** the reference class diagram, API signatures with why-not-the-alternative, the full implementation, and the engine→backend mapping (layers, REST, schema).

---

## Same framework, different building

- **Library system:** `issue/return ≈ park/unpark`, BookLoan ≈ Ticket, fine ≈ fee (`FinePolicy` = the PricingStrategy seat). The flip: a book *leaves* the building — the shelf slot usually isn't modelled at all. Run the three-way test before copying a design.
- **BookMyShow seats:** Seat ≈ Spot (typed), Booking ≈ Ticket. The difference is *contention* — 400 people want seat J-12 at 7pm, so the core entity becomes the **SeatLock (hold + TTL)**, which parking only meets in its reservations extension. Two gates racing for the last spot is the same problem at 1% of the traffic.

## Pre-work for LLD-25

1. **Draw the class diagram** from the design board — arrows, diamonds, multiplicities; mark where `NearestToExit` and a new pricing scheme plug in. (Submission discussion goes up before LLD-25 — draft in [`DISCUSSION_DRAFT.md`](DISCUSSION_DRAFT.md).)
2. **Think about — two gates:** both call `park()` at the same instant for the last medium spot. What exactly goes wrong, line by line? What's the *smallest* thing you'd lock, and why is "the whole lot" the wrong answer?
3. **Think about — monthly passes:** a pass-holder drives in, no per-visit payment. What changes — `Ticket`, `PricingStrategy`, or something new? Run the three-way test on "pass".

## Files

| File | What |
|---|---|
| `index.html` | Interactive class: recap, clarify + actors, FR walk with decision quizzes, ownership reveals, design board, siblings, pre-work |
| `DISCUSSION_DRAFT.md` | The diagram-submission discussion, ready to post when the class ships |
