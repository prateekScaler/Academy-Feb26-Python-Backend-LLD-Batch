# LLD-29 — Splitwise: Code (Part 2)

> The design from LLD-28, **built**. We derive every class, then write the engine: the **SplitStrategy** family (with the penny fix), the **BalanceSheet** that nets who-owes-whom as expenses land, and the **debt-simplification** algorithm that settles a group in the fewest payments. One single-file engine and one layered package — both assert green.

**How to use this class:** open `index.html` for the interactive page (FR-by-FR derivation, the class diagram, the code walked through, decision quizzes). This README is the same content in prose.

---

## The two shapes

```
code/01_splitwise.py        — the whole engine in one file (all demos assert green)

splitwise/                  — the layered package (folders = design layers)
├─ money.py · enums.py · exceptions.py   # vocabulary (paise, SplitType, errors)
├─ models/        ── DOMAIN ──   user · group · split · expense · payment
├─ strategies/    ── OPEN VARIABLE ──   equal · exact · percent
├─ balance_sheet.py     # the running net: who owes whom
├─ debt_simplifier.py   # settle in the fewest payments (greedy net-and-match)
├─ service.py     ── ORCHESTRATOR ──   ExpenseService
└─ main.py        # runnable demos
```

## Run it

```bash
cd code
python3 01_splitwise.py        # single-file engine
python3 -m splitwise.main      # layered package
```

Both run the same six demos:

```
1) Penny problem  — ₹100 split equally 3 ways  → [₹33.34, ₹33.33, ₹33.33]
2) Add expense    — B/C/D each owe A ₹300.00 · A net ₹900.00
3) Opposite debts net out  — B owes A ₹20.00
4) Debt simplification     — C→A ₹1750.00, B→A ₹250.00   (3 edges → 2 payments)
5) Exact & percent splits validate
6) Only the creator edits members
All demos green ✅
```

## Money is integer paise (not floats)

Computers store decimals in binary, so most money values (0.1, 0.20, 0.33) are tiny approximations — invisible per value, but they accumulate and break "do the splits sum to the total?" checks (`0.1 + 0.2 → 0.30000000000000004`). So every amount is an **integer count of paise** (₹33.34 = `3334`); arithmetic stays exact, division uses `divmod` (the leftover is the penny rule), and we format to "₹x.xx" only at display.

## Deriving the classes (FR by FR)

The design class left the model as homework; here we settle the modelling forks:

- **Who paid what** → `paid_by` as a `{user: paise}` map (one payer = a map of size 1).
- **Who owes what** → the `Split` association class — one `(user, amount)` per participant.
- **Balances** → a stored running **`BalanceSheet`** (net per pair) rather than recomputing from all expenses each read (reads ≫ writes).
- **Objects → rows** → the maps can't be a DB column; they normalise into a **`UserExpense`** junction table (one `amount` + a `PAID`/`OWED` type).
- **Permissions** → `Group.created_by` for the MVP; when others may manage, the User–Group **many-to-many** already needs a `Membership` join, so the permission becomes a **`role`** on it (RBAC).

The class diagram is the **design** model (the `UserExpense` and `Membership` association classes + `BalanceSheet`/`DebtSimplifier` the service owns). The in-memory engine takes a lighter shape that maps onto it: `Split` + the `paid_by` map are `UserExpense` rows; the members list is `Membership` rows.

## Split strategies (the open variable)

One contract — `split(amount, participants, args) -> list[Split]`, where the shares **sum to the total** — with three implementations. A new way to split is one new class.

- **EqualSplit** — `base, remainder = divmod(amount, n)`; the first `remainder` participants each absorb one extra paisa, so ₹100/3 → `[3334, 3333, 3333]` = exactly ₹100.
- **ExactSplit** — the caller gives `{user: paise}`; **validate** they sum to the total, else `raise SplitError`.
- **PercentSplit** — the caller gives `{user: percent}`; validate they sum to 100, convert each to paise, and give the rounding remainder to the **last** participant.

## The BalanceSheet

A map of net debts: `balances[debtor][creditor] = paise`. Adding an expense calls `add_debt(ower, payer, share)` for each ower, which **first cancels any reverse debt** — so we never store both `a→b` and `b→a` (B owes A ₹50, then A owes B ₹30 → just **B owes A ₹20**). "What do I owe?" is then an O(1) read.

```python
def add_debt(self, debtor, creditor, amount):
    reverse = self.balances[creditor][debtor]   # owed the other way?
    if reverse >= amount:
        self.balances[creditor][debtor] = reverse - amount
    else:
        self.balances[debtor][creditor] += amount - reverse
    self._prune()
```

In this class it lives **in memory** (a nested dict). Persisted, it's a `balances(from_user, to_user, amount)` table — or skip storing it and **recompute from `user_expense`** (the store-vs-recompute trade-off), with `user_expense` as the source of truth.

## Debt simplification (fewest payments)

The balance graph is a tangle of IOUs ("I owe you" debts = edges). Settling each edge is wasteful — debts cancel and chain. **Collapse everyone to a single net** (it sums to 0), then make the net-negative people pay the net-positive ones. Three ways to compute the payments:

- **Greedy net-and-match** *(recommended)* — repeatedly settle the biggest creditor against the biggest debtor; each payment zeroes someone, so it finishes in ≤ n−1 payments. `~O(n log n)` with heaps (the code re-sorts each round → `O(n²)`). This is literally **LeetCode 465 "Optimal Account Balancing"**, and in real life it's a trip treasurer squaring up or a bank netting payments.
- **Cycle-cancelling** — model debts as a directed graph; a cycle drops by its smallest edge, removing ≥1 edge. Minimises edges, not guaranteed the fewest transactions (the min-cost-flow / multilateral-netting idea).
- **Optimal (subset partition)** — find subsets that net to 0 (a zero-sum group of k needs k−1 payments). Exponential — the exact minimum is **NP-hard** (subset-sum flavour); only for tiny groups.

> **NP-hard**, simply: you can *check* an answer fast but *finding the best* seems to need ~all combinations (exponential). Like **Sudoku** — easy to check, hard to solve. Other examples: Travelling Salesman, Knapsack, Subset-Sum. So we ship a heuristic (greedy), not the exact optimum.

Worked example — A pays ₹3000 (A/B/C), B pays ₹1500 (B/C): nets **A +2000, B −250, C −1750** → **C→A ₹1750, B→A ₹250** (3 edges → 2 payments).

## Database: the schema, constraints & indexes

Persist the maps as the normalized **`UserExpense`** junction table — `(user_id, expense_id, amount, type ∈ {PAID, OWED})`, one row per relationship. Storing a map in a column breaks **1NF** (non-atomic, unindexable).

- **Constraints:** PK; FK with `ON DELETE CASCADE`; `CHECK (amount >= 0)`, `CHECK (percentage BETWEEN 0 AND 100)`; `NOT NULL`.
- **Indexes:** `(user_id, type)` for "total user X owes"; `(user_id, expense_id, type)` for "what does X owe on this expense" — and by the **leftmost-prefix** rule that one composite index also serves `user_id` and `user_id+expense_id` queries (like a phone book sorted by last-name, then first-name). For "everyone in expense 42" (filter on `expense_id` alone) add a separate `INDEX(expense_id)`.

**Normal forms:** **1NF** = atomic cells · **2NF** = no *partial* dependency on a composite key · **3NF** = no *transitive* dependency through another non-key column ("the key, the whole key, and nothing but the key").

## Permissions (RBAC)

Pin permissions to **roles**, not people. `Membership` carries a `role` (ADMIN / MEMBER); the service checks the role, not the identity — the creator is just the first ADMIN. Authorisation is a **server-side** check (a hidden UI button is cosmetic; the API is still callable), and reads are **filtered** to the caller's memberships so users never receive data from groups they're not in.

## Trade-offs & extensions

- **Integer paise, not floats** — exact arithmetic; the penny rule is a clean integer remainder.
- **Net edges vs full history** — the sheet keeps the net (cheap, self-cancelling); keep raw expenses for the audit trail.
- **Simplify lazily** — `simplify_group` runs on demand, scoped to one group's expenses.
- **Concurrency (callback to BookMyShow)** — two expenses on one group both read-modify-write the balance → the *lost update*; guard with a per-group lock / transaction.
- **New split = one new class** — a `SharesSplit` (2:1:1) is one more strategy.
- **Multiple payers** — `paid_by` is a `{user: paise}` map; `apply` splits each ower's debt across payers proportionally.

## Files

| File | What |
|---|---|
| `code/01_splitwise.py` | The whole engine in one file; six demos assert green. |
| `code/splitwise/` | The layered package (models / strategies / balance_sheet / debt_simplifier / service / main). |
| `index.html` | The interactive class page. |

## Homework & class discussions

- 📊 [#26 — Debt simplification](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/26): propose an algorithm for the fewest settle-up transactions (complexity + the NP-hard caveat).
- 🗃️ [#27 — Database models, constraints & indexes](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/27): the `UserExpense` schema with constraints, indexes, and 5 `EXPLAIN`'d queries.
- 📐 [#28 — Class diagram](https://github.com/prateekScaler/Academy-Feb26-Python-Backend-LLD-Batch/discussions/28): compare your diagram with the one built here.

## Next

**LLD-30 — Google Calendar: Design.** The next system in the playbook.
