# LLD-30 — Google Calendar: Design (Part 1)

> The same playbook on a **time-shaped** problem — overview → clarify → the FRs → the hard parts → trade-offs. The open variable is **recurrence** (one rule → many instances, with per-occurrence exceptions); the course's recurring shape is the **Attendee** association (event × user + RSVP); and the time twists are **time zones** (store UTC, render local, DST) and **free/busy** (interval overlap). **Design today; the class diagram is homework.**

**How to use this class:** open `index.html` for the interactive page (use-case diagram, click-to-reveal FRs, the recurrence / attendee / free-busy diagrams, the class diagram, decision quizzes). This README is the same content in prose.

## 📂 Everything in this folder

| Resource | What it is |
|---|---|
| **[`index.html`](index.html)** | The interactive **class-design** page — scenario intro with reveal-one-by-one design questions, click-to-reveal FRs, the *From-FRs-to-classes* derivation, the recurrence / attendee / time-zone / free-busy deep dives, the full **class diagram**, and decision quizzes. |
| **[`google-calendar-db-design.html`](google-calendar-db-design.html)** | The **database-design** companion — the *same* problem through **Minimal Modeling** (anchors → attributes-as-questions → links → SQL tables), with an **ER diagram**, the complete schema, and trade-off quizzes. Based on the [databasedesignbook.com tutorial](https://kb.databasedesignbook.com/posts/google-calendar/). The data-modelling lens to complement the class-design one. |
| **[`falsehoods-about-time.html`](falsehoods-about-time.html)** | A **True/False quiz** on *"Falsehoods programmers believe about time"* — 47 statements (real facts mixed with the classic falsehoods), each with the gotcha, the fix, and annotated Python. Based on [infiniteundo.com](https://infiniteundo.com/post/25326999628/falsehoods-programmers-believe-about-time). |
| **[`LLD-interview-prep.html`](LLD-interview-prep.html)** | An interactive **quick-revise handbook** — a time-boxed machine-coding speed playbook, a what-they-look-for checklist, **10 design patterns with generic UML diagrams**, LLD-concepts revision, and conceptual Q&A with reveal-on-demand hints. |
| **[`worksheets/`](worksheets/LLD_MASTER_INDEX.md)** | A **case-study worksheet library** — 20 LLD problems across 8 categories (games · booking · financial · e-commerce · social · content · physical · scheduling), each **fill-in-the-blanks** with reveal-on-click sample answers, plus a per-category guide. Start at [`LLD_MASTER_INDEX.md`](worksheets/LLD_MASTER_INDEX.md). |

**How to use:** open `index.html` for the interactive class page; the rest are companions and interview prep. A printable **PDF of the class notes** can be exported from `index.html` (Print → Save as PDF).

---

## Step 0 — Overview

**One-liner:** *"A user creates events on a calendar, invites others, sets some to repeat (every Monday), and the app shows everyone's schedule across time zones, flags conflicts, and reminds them."*

- **Actor & goal** — a user creates/edits events, invites attendees, views their schedule.
- **Core noun** — the **event**, a time block *(start, end)* on a **calendar**; its trickier cousin is the **recurring** event.
- **The twist** — **recurrence** (one rule, many instances, with exceptions), **time zones** (DST), and **free/busy** (overlap).

## Step 1 — Clarify

| Lens | The question | Default |
|---|---|---|
| Unit | What do we schedule? | An **event** (start, end) on a **calendar** |
| Recurrence | Repeating events? | **Yes** — daily/weekly/monthly + per-occurrence **exceptions** (the star) |
| Attendees | Invites & RSVP? | accept / decline / tentative |
| Time zones | Across zones? | store **UTC**; render local; DST-aware |
| Conflicts | Overlaps / free-busy? | warn on overlap; find a common slot |
| Reminders | Notify? | N minutes before |

**Park:** video links, attachments, rooms/resources, working hours. **Actors → use-case diagram** (each oval becomes a REST endpoint): User (create event, set recurrence, invite & RSVP, view, find a slot) and System (send reminders, expand recurrence).

## Step 2 — Requirements (through questions)

**Calendars & events**
- A user has one or more **calendars**.
- An **event** has a title, a **start** and **end** time, and an organizer; it lives on a calendar.

**Recurrence**
- An event can **repeat by a rule** (daily / weekly / monthly) until a date or for N occurrences.
- A single occurrence can be **edited or deleted** without changing the rest (an **exception / override**).

**Attendees**
- The organizer can **invite** users; each attendee can **RSVP** (accept / decline / tentative).

**Viewing & scheduling**
- A user can **view events by day / week / month**.
- A user can see **free/busy** and the system can **find a common free slot** across attendees.
- The app **warns on a conflict** — a new event overlapping an existing one.

**Reminders & time zones**
- An event can have **reminders** (notify N minutes before).
- Times are stored as absolute instants (**UTC**) and shown in the viewer's **time zone** (DST-aware).

The **nouns** become classes; the **verbs** become APIs.

## Step 3 — From FRs to classes

Nouns become classes, verbs become methods. Walk the FRs and settle each class + its attributes through choices and trade-offs **before** the deep dives:

- **Event** — `title`, `start`/`end` as absolute **instants** (store `end`, not duration — it handles all-day / multi-day; duration is derived), `organizer`, `calendar`, optional `recurrence`, `reminders[]`.
- **Calendar** — a user owns **many**; each event lives on **exactly one** (`User → Calendar → Event`, composition).
- **RecurrenceRule** — an event holds an **optional** `RecurrenceRule` (0..1), *not* columns-on-`Event` and *not* a `RecurringEvent` subclass; one-off events just leave it null. *How* it repeats is the open variable (deep dive next).
- **Attendee** — the `(event × user)` RSVP lives on an **association class** (full treatment in Step 5).
- **Reminder** — `Event ◆ Reminder(minutes_before, method)`, composition.
- **SchedulingService** — recurrence expansion and free/busy span many events, so they live in a **service**, not on `Event`.

Derived so far: **User · Calendar · Event · RecurrenceRule · Attendee · Reminder · SchedulingService** + enums **Freq**, **AttendeeStatus**. The four hard parts — recurrence expansion, the Attendee association, time zones, free/busy — come next.

## Step 4 — Recurrence (the open variable — deep dive)

A recurring event is a **rule** that *expands* into occurrences, plus a few **exceptions**. *How* it repeats is the **open variable** — a `RecurrenceRule` strategy (like Parking's pricing or Splitwise's split).

- **Store the rule, not the instances.** Keep one `RecurrenceRule` (FREQ / INTERVAL / BYDAY / UNTIL or COUNT) and expand it to concrete dates only for the window you're showing. Materialising every occurrence ("every weekday for a year" ≈ 260 rows) is wasteful and painful to edit.
- **Exceptions/overrides.** Moving just *next* Monday's 10:00 standup to 11:00 = keep the rule, remove that date (`EXDATE`), and add a one-off **override** event. The base rule stays intact for everyone else.
- **Expansion is a pure function:** `rule.occurrences(window) → [datetimes]`, minus exceptions, plus overrides.

## Step 5 — Attendees & RSVP (the recurring shape)

An event and its guests are a **many-to-many with data on the link**. RSVP is per *(event, user)* pair, so it can't sit on `User` or `Event` alone — the pairing earns its own class: **`Attendee(user, event, status)`**, an **association class**. You've met this shape all course: BookMyShow's `ShowSeat`, Splitwise's `Split` / `UserExpense`, the `Membership` join — and now `Attendee`.

## Step 6 — Time zones & DST

An event is a **single instant** in time; zones are a *display* concern. **Store UTC, render local** — convert to each viewer's zone (applying DST) only for display. A wall-clock string is ambiguous and breaks across DST; two copies drift. Subtle case: keep the organiser's zone on a *recurring* event so "every Monday 9am" survives daylight-saving shifts.

## Step 7 — Free/busy & conflicts

Both "am I double-booked?" and "when are we all free?" reduce to **interval overlap**. Two events `[s1, e1)` and `[s2, e2)` **conflict iff** `s1 < e2 AND s2 < e1` (touching is not a conflict with half-open intervals). To **find a common slot**: merge all attendees' busy intervals and look for a gap long enough.

## Step 8 — The class diagram

The assembled model (shown on the page): `User ◆ Calendar`, `Calendar ◆ Event`, the **`Event`–`Attendee`–`User` many-to-many** with RSVP on the `Attendee` join, `Event ◇ RecurrenceRule` (0..1, carrying its exceptions), `Event ◆ Reminder`, and a `SchedulingService` that expands recurrences and finds slots. Enums: `Freq` (DAILY/WEEKLY/MONTHLY) and `AttendeeStatus`.

**Homework:** draw it yourself *first* from the FRs, then compare; and design the **REST API** (one endpoint per use-case oval). A recurring instance is a *computed* value (expand the rule), not a stored row.

## Step 9 — Trade-offs

- **Rule vs materialised instances** — store the rule + exceptions, expand on read.
- **Store UTC, render local** — one instant; keep the zone for recurring events (DST).
- **RSVP on the join** — `Attendee(user, event, status)`, the association class.
- **Overlap is interval math** — `s1 < e2 AND s2 < e1`; find-a-slot = merge busy intervals, find the gap.
- **Reminders via a scheduler** — a due-time queue / cron fires them (same "don't trust the sweep for correctness" lesson as BookMyShow's holds).
- **Extensions** — rooms/resources, attachments, shared calendars — additive, not a rewrite.

## Homework

Draw the **class diagram**, design the **REST API** (one endpoint per use-case oval), and write the **recurrence-expansion** algorithm (rule + window → occurrences, minus exceptions). We build it in **LLD-31 — Google Calendar: Code**.
