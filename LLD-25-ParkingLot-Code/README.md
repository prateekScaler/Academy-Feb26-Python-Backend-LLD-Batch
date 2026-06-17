# LLD-25 — Parking Lot: Code (Part 2)

> Steps 4–7 of the playbook. From your LLD-24 diagrams to a running lot: reference class diagram → API signatures with "why not the alternative" → live build → **the engine mapped onto the backend stack from Module 1** (layers, REST, schema) → the two questions every parking interview ends on (two gates at once; what survives a restart).

**Quick start:**
- `python3 code/01_parking_lot.py` — single-file version; seven demos assert green
- `cd code/parkinglot && python3 main.py` — the layered package; every FR asserted
- `cd code/parkinglot && python3 main.py play` — interactive booth (simulated clock)
- Open `index.html` in a browser for the interactive class page (diagrams, sequence + state machine, quizzes)

---

## Class flow

| Phase | What happens |
|---|---|
| Diagram review | Compare homework submissions; settle the reference diagram (every box traces to an FR; every diamond answers the lifetime question; the two «ABC» boxes are the zero-edit plug-in points; the enums box carries the vehicle→size mapping) |
| APIs | `park(vehicle, now) → Ticket \| None` (the flip vs TTT), `pay()` + `exit_lot()` as two methods (two real-world events; the in-between state is what the gate checks), accept ids not objects, `pick(floors, v)` (narrow parameter = enforced ISP), `fee(size, seconds)` (bill the resource you occupied, not the vehicle), `Spot.can_fit` (the invariant lives where its facts live) |
| Patterns & edges | Two independent Strategies; policy as data (`SPOT_SIZE_FOR`, the tiered `RATES` table); two record entities; the edge-case table incl. unpaid exit, double pay, OUT_OF_ORDER |
| Structure | The folder tree IS the layered architecture: this is the *API-flavoured* round that earns `repositories/`. `cli.py`→controller, `service.py`→service, `repositories/`→storage seam, `models/`+enums+config→domain. The one real upgrade over the single file: the bare `_active`/`_payments` dicts become injected repository classes (`exists()` is the pay-once guard as a query). `console.py` carried in byte-for-byte from TTT |
| Live build | Five stages, leaves first: enums/mapping/errors/Vehicle/Spot → Floor/Ticket/Payment → both strategies → ParkingLot → demos |
| Flow (sequence + lifecycle) | The *dynamic* view. Sequence diagram of `park()` (lifelines, activation bars, `«create»` for the Ticket's birth, `alt` for lot-full); the seven-step recipe to derive one; **finding the lifecycle two ways** — memory lifecycle read off the diamonds (composition = born-with-the-whole, no `«create»`; records get born/retired in-flow), and state lifecycle as a state machine. The payoff: **Ticket's ISSUED→PAID→EXITED machine and the three exceptions are the same picture** — exit-before-pay/pay-twice/touch-a-gone-ticket are the three illegal transitions |
| **From engine to backend** | The Module-1 reconnect: controller/service/repository/domain layers (ParkingLot *is* the service; the repositories ARE the seam from the Structure section); actor use cases → REST endpoints; the DTO rule (transport shapes stay off class diagrams); validate-per-layer quiz; the schema — where `UNIQUE(ticket_id)` enforces pay-once in the database; count() ids vs UUIDs |
| Trade-offs | Concurrency: the `pick()` → `occupy()` check-then-act race, fixed with one lock **per floor** + re-check + retry; persistence: replay open tickets to rebuild occupancy (ids, not refs, make it possible); extensions table → BookMyShow's hold-with-TTL is next |

## The implementation — `code/01_parking_lot.py`

Runnable with plain `python3`; seven demos, all assert green.

Every line traces to an LLD-24 decision:

| Code | LLD-24 decision |
|---|---|
| `VehicleType` + `SpotSize` + `SpotStatus` enums | FR-2/6 — three named sets; OUT_OF_ORDER is the third state a bool can't hold |
| `SPOT_SIZE_FOR = {BIKE: SMALL, CAR: MEDIUM, TRUCK: LARGE}` | FR-2 — policy as data; scooters/buses/cross-parking are dict edits |
| `Spot(spot_id, size, status)` + `is_free()`/`can_fit(v)`/`occupy()`/`free()` | FR-2/6 — the Cell analogue: two facts + the rules relating them |
| `Floor(number, spots)` + `free_spots`/`free_count` | FR-1 + FR-7 — identity + its own queries |
| `Ticket` + frozen `Payment` (ids, not live refs) | FR-3/9 — two records that outlive the stay; money doesn't mutate |
| `park() → Ticket \| None` | FR-4 — full lot is expected flow; the exception criterion flip |
| `pay()` → `AlreadyPaidError`; `exit_lot()` → `UnpaidExitError`/`InvalidTicketError` | FR-9 — contract violations DO raise |
| `amount_due()` | the booth display — a pure read |
| `ParkingStrategy` (FirstFit / LeastCrowded) | FR-8 — placement open variable |
| `PricingStrategy` (TieredHourly: first hour + per-extra-hour per size, ceil, 1h min / WeekendFlat) | FR-5 + FR-8 — bills the spot size; independent axis |
| `now: float` parameters everywhere | clock injection — demos assert exact fees without sleeping |

## Files

| File | What |
|---|---|
| `index.html` | The class page: reference diagram (SVG), APIs + why-not collapsibles, edge table, folder structure, staged build (code sliced verbatim from the .py), **sequence diagram + lifecycle/state-machine**, captured run, backend mapping, trade-offs |
| `code/01_parking_lot.py` | Complete working lot in ONE file (read top to bottom) — all demos assert green |
| `code/parkinglot/` | **The same engine, organised into a layered package tree** — `enums.py` / `exceptions.py` / `config.py` / `models/` (domain) / `strategies/` / `repositories/` (the storage seam) / `service.py` / `console.py` / `cli.py` / `main.py`. Run `cd code/parkinglot && python3 main.py` (acceptance asserts) or `python3 main.py play` (interactive booth, simulated clock) |

## Next

**BookMyShow (design + code):** a parking lot where every car wants the same spot at the same second — the reservation hold (SeatLock + TTL) graduates from a table row to the main character.
