# LLD-28 — Splitwise: Design (Part 1)

> The same playbook once more — align → clarify → the requirements → split strategies → the balance graph → trade-offs — on a problem whose star is **how an expense is split** (the open variable: equal / exact / percent) and whose headline is the **balance graph**: keeping "who owes whom" consistent and settling everyone with the **fewest payments**. **Design today, code in LLD-29.** Drawing the class diagram and designing the REST APIs are homework — we've opened GitHub Discussions for both.

**How to use this class:** open `index.html` in a browser for the interactive page (concurrency warm-up, use-case diagram, click-to-reveal FRs, decision quizzes, the split-strategy and balance-graph walkthroughs). This README is the same content in prose.

---

## Warm-up — concurrency recap (from BookMyShow)

Last class we cracked concurrency on BookMyShow; today's Splitwise hits the very same races — the balance graph is a shared read-modify-write resource, and settle-up is a reserve-then-confirm flow. The throughline: **a shared mutable resource under concurrent writers needs a guard.**

- **Lost update** — two transactions read a value, each modifies and writes it back, and one write clobbers the other. Fix with an atomic `UPDATE x = x + n` or a lock held across the read+write.
- **Optimistic vs pessimistic** — *optimistic* (a version column; `UPDATE … WHERE version = v`; retry if 0 rows changed) shines under **low contention**; *pessimistic* (lock the row up front with `SELECT … FOR UPDATE`) wins under **high contention**, where optimistic retries thrash.
- **How optimistic detects a conflict** — a value that changes on every write: a `version` column is cleanest, but the old field values, an `updated_at` timestamp, or a row hash all work. There's no single "must-have version column."
- **Retry vs surface** — a pure contention conflict is transient: retry a bounded number of times with backoff. A conflict that reflects a real state change is a business outcome: catch it and return a clean error.
- **Soft lock vs DB lock** — a *hold* (reserve a resource for minutes while a user pays) is a **business reservation**: a `status = HELD` field + an `expires_at`. A DB lock has **no timer of its own** — it lives only inside an open transaction and releases when that transaction commits/rolls back. "Hold a DB lock for 10 minutes" means "keep a transaction open for 10 minutes," which ties up a connection (and many databases will kill it). Release a hold by **lazy expiry on read** (`now > expires_at`) backed by a TTL and a cheap sweep — the sweep bounds staleness, not correctness.
- **The anomaly zoo (DDIA Ch. 7)** — dirty read, lost update, read skew (non-repeatable), write skew, and phantom.

## Step 0 — Overview: get on the same page

**The one-liner:** *"Friends share expenses — Ananya pays ₹1200 for dinner for four; Splitwise records who owes whom, and lets everyone settle up with the fewest payments."*

A good overview names three things:
- **The actor & goal** — a user adds a shared expense and later wants to know *who owes whom* and to *settle up*.
- **The core noun** — BookMyShow had the *seat of a show*; here it's the **expense and its splits**.
- **The twist** — an expense can split **many ways** (equally / exact / percentage), and *"who owes whom"* is a **running balance** that must stay consistent and **add up to zero** across everyone.

## Step 1 — Clarify

| Lens | The question | Our default |
|---|---|---|
| Unit | What do we split over? | Per **expense**; participants are a subset of users (optionally a **group**) |
| Split type | How can an expense divide? | **Equal / exact / percent** |
| Payer | Who fronts the money? | "Who paid what" — one or many payers |
| Balance | What do we track? | A **running net** — who owes whom |
| Settle | How do debts clear? | A **payment** that reduces a balance |
| Simplify | The headline goal | Settle the group with the **minimum number of payments** |

**Feature sweep (park these):** multi-currency, recurring expenses, receipts, comments, notifications.

**Actors → the use-case diagram** (each oval becomes a REST endpoint — your pre-work): **User** (create a group, add an expense, view balances, settle up) and **System** (simplify debts).

## Step 2 — Requirements: generate the FRs through questions

Walk one journey — sign up → join or create a group → add an expense → see what you owe → settle up — and ask a question at each step. Every answer is an FR.

**The people**
- A user's profile contains at least a **name** and **phone number**.
- Users can participate in **expenses with other users** — a group is optional.
- Users can participate in **groups**.

**The expense**
- To add an expense, specify **either the group or the other users** involved, plus **who paid what** and **who owes what**, plus a **description**.

**Seeing the money**
- A user can see their **total owed amount**.
- A user can see a **history of the expenses they're involved in**.
- A user can see a **history of the expenses in a group** they participate in.

**Who's allowed**
- Users **cannot query groups they're not a member of**.
- **Only the user who created a group** can add or remove its members.

**Settling up**
- A user can request a **personal settle-up**: a list of transactions that, once executed, leave *that user* owing and owed nothing (others need not be settled).
- A user can request a **group settle-up**: a list of transactions that leave **everyone in the group at net 0**, using only that group's expenses.

**Good to have**
- When settling a group, **minimise the number of transactions**.

Two lenses carry forward: the **nouns** become the classes; the **verbs** (add, view, settle, simplify) become the APIs.

## Step 3 — The class diagram (homework)

Straight from the requirements, design the class diagram — the classes, their relationships (composition / aggregation), and the multiplicities. **We derive the full model together in LLD-29**; for now, attempt it yourself and post it.

➡️ **[Discussion #28 — Design the class diagram from these requirements](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/28)**

## Step 4 — The split strategies (the open variable)

The contract: `split(amount, participants, args) -> list of (user, amount)`, where the shares **sum to the total**. A new way to split is **one new class** — the engine never changes.

- **EqualSplit** — `amount / n` each. **The penny problem:** ₹100 / 3 = ₹33.33 each → ₹99.99, a paisa vanishes. The sum-to-total invariant forces a deterministic rule for the leftover paisa (give it to the first participant(s); use integer paise, never floats).
- **ExactSplit** — the caller gives exact amounts; **validate they sum to the total**, else reject.
- **PercentSplit** — the caller gives percentages; **validate they sum to 100**, then `amount × pct`.

Same "open variable → Strategy" move as Parking's and BookMyShow's pricing.

## Step 5 — The balance graph & settle-up

**The invariant:** across everyone, the balances **sum to zero** — every rupee owed is owed *to* someone. Two representations:
- **Per-pair edges** — `{(debtor, creditor) → amount}`. Keeps the detail, but grows.
- **Per-user net** — each user's *(owed to them − they owe)*. Loses the detail, but it's exactly what you need to settle.

**Debt simplification** — settling every edge is wasteful; debts cancel. Warm-up: A owes B ₹100 and B owes C ₹100 → net it out → **A pays C ₹100** (one payment, not two). Designing the algorithm (greedy net-and-match? graph cycles? min-cost max-flow?), its complexity, and whether it's truly optimal (the exact minimum is **NP-hard**) is a problem worth chewing on:

➡️ **[Discussion #26 — Debt Simplification: settle a group in the fewest transactions](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/26)**

## Step 6 — Trade-offs to say out loud

- **Edges vs net balances.** Edges keep the audit trail; net is what you simplify. Real systems keep both.
- **The penny / rounding problem.** Equal splits don't divide evenly; use integer paise and a deterministic remainder rule.
- **Simplify on write vs on demand.** Simplify lazily, when someone hits "settle up," not after every expense.
- **Concurrency (callback to BookMyShow).** Two expenses added to the same group at once both read-modify-write the balance graph — the *lost update* again. Guard the group's balance update (a per-group lock / a transaction), exactly like the seat race.
- **Extensions.** Multi-currency, recurring expenses, multiple payers, a shares-based split — each is one new strategy or field, not an engine rewrite.

## Homework & class discussions

- 📊 **[#26 — Debt simplification](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/26):** propose an algorithm for the fewest settle-up transactions (complexity + the NP-hard caveat).
- 🗃️ **[#27 — Database models, constraints & indexes](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/27):** design the DDL — constraints, the `UserExpense` junction table, composite/unique indexes, and 5 optimized queries with `EXPLAIN`.
- 📐 **[#28 — Class diagram](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/28):** design the class diagram straight from the requirements and post it.

## Next

**LLD-29 — Splitwise: Code.** We derive the full class model and build it live — the `SplitStrategy` family (with the penny-rounding fix), the balance sheet that updates as expenses are added, settle-up, and the debt-simplification algorithm.
