# LLD-31 — Unit Testing: Why, pytest & Best Practices

> **Module 4 kickoff — Advanced Software Engineering.** Tests are not about proving code works today; they **keep it working tomorrow**. We write a first real pytest suite — on the Splitwise / ParkingLot / TicTacToe code you already built — and end with a look over the fence: what testing becomes when the output is **non-deterministic** (the **evals** paradigm, previewed today, deep-dived alongside mocking).

**How to use this class:** open `index.html` for the interactive page (module map, the bug story, the testing pyramid, pytest fundamentals, AAA/FIRST, parametrize, fixtures, error & float testing, testing time, the evals teaser, decision quizzes). This README is the same content in prose. Every example lives in [`code/`](code/README.md) — runnable with plain `python3` (no installs) *or* `pytest`, 43 tests, all green.

---

## Module 4 — the road ahead (10 sessions)

| # | Session | Takeaway |
|---|---------|----------|
| **1** | **Unit Testing & Best Practices** *(today)* | pytest suites: AAA, naming, parametrize, fixtures, raises — on code you own |
| 2 | Mocking & Web/API tests | Fake the slow & flaky (payments, email, **LLM calls**); DRF `APIClient` |
| ★ | *Evals — testing non-deterministic (LLM) outputs* | **The new paradigm**: grade → threshold → pass rate. Teaser today (§ Beyond asserts); deep-dive rides with the mocking session |
| 3 | Authentication-1: AuthN vs AuthZ, tokens, bcrypt | Password storage done right |
| 4 | Authentication-2: JWT, OAuth 2 | Stateless tokens; the OAuth dance |
| 5 | Authentication-3: build the User Service | Apply it |
| 6 | Authentication-4: implement OAuth 2 | Login-with-Google, end to end |
| 7 | Email Service — intro to Message Queues | Async work: producers, consumers, retries |
| 8 | Cloud-native patterns *(adapted for Python)* | Config, discovery, resilience |
| 9 | Logging & Monitoring | Observability |
| 10 | Containerization | Docker |

---

## Step 0 — Why tests exist (a story you already know)

In LLD-29 we fixed the **penny problem**: money in integer paise + `divmod`, so ₹100 / 3 sums back to exactly ₹100. Three months later a teammate "simplifies" it to `round(total / n, 2)`. **Nothing crashes** — but ₹100 split three ways is now 3 × ₹33.33 = **₹99.99**. A paisa evaporates from every odd split until finance notices in week three.

- One test — `assert sum(shares) == total` — turns that PR **red in seconds**, before review.
- That's the real job of a suite: **regression protection**, and a **safety net for refactoring** (your LLD moves — extract a Strategy, split a God class — are only safe under a guarding suite).
- The later a bug is caught, the more it costs: seconds (editor) → minutes (CI) → hours (review) → weeks + trust (production).
- *"Legacy code is simply code without tests."* — Michael Feathers.

## Step 1 — The testing pyramid

- **Unit** — one function/class, in memory, milliseconds. Most tests live here. *(Today.)*
- **Integration** — endpoint → service → test DB together (DRF `APIClient`). Slower, fewer. *(Next class.)*
- **E2E** — the whole deployed system. Keep only a handful.

## Step 2 — pytest in ten minutes

- **Discovery by naming:** files `test_*.py`, functions `test_*`. No registration, no base classes.
- **Plain `assert`** — pytest's introspection prints both sides on failure (`assert 9999 == 10000`).
- **Daily flags:** `-v` (names), `-k expr` (focus), `-x` (stop at first failure), `--lf` (re-run failures).
- `unittest` exists (classes, `assertEqual`); pytest runs it too — but new Python code defaults to pytest.

## Step 3 — Anatomy of a good test

- **AAA** — Arrange / Act / Assert, readable top-to-bottom as a sentence.
- **The name states the behaviour** — `test_full_lot_returns_none_not_an_exception` failing tells you what broke without opening the file.
- **One behaviour per test**; assert *what* is promised, not *how* it's implemented.
- **FIRST**: Fast · Independent · Repeatable · Self-validating · Timely.

## Step 4 — parametrize: one test, a table of edge cases

One decorated test runs each row independently; failures name their exact case. Rows come from **boundaries**: 0 · 1 · typical · where behaviour changes · extreme. For the split: remainder 0 / 1 / n−1, `n = 1`, `total = 0`, `total < n`. For the winner check: all 8 lines *plus* the no-winner cases.

## Step 5 — Fixtures: Arrange once, reuse everywhere

`@pytest.fixture` + ask-by-parameter-name = dependency injection for tests. Fresh per test by default (Independence, mechanised); `yield`-style fixtures run teardown even on failure; shared ones live in `conftest.py`.

## Step 6 — Testing errors, and the float trap

- **Rule violation → raises** — test with `pytest.raises`, assert on the error object, and check nothing half-applied.
- **Expected outcome → value** — the full lot returns `None` (the LLD-24 line, now in tests).
- `0.1 + 0.2 != 0.3` — floats can't do equality. `pytest.approx` for genuinely continuous values; **money = integer paise**, exact equality, no epsilon.

## Step 7 — Testing time: inject the clock

`datetime.now()` in the code under test = untestable + flaky-at-midnight. Depend on a **Clock**; tests pass a **FakeClock** (freeze any instant, `advance()` instead of `sleep()`). Same move for randomness: inject `random.Random(seed)`.

## Step 8 — Beyond asserts: the evals teaser

When the backend calls an LLM there is **no single right answer** — equality dies. The assert evolves:

| | Classic test | Eval |
|---|---|---|
| Output | deterministic | stochastic |
| Check | `actual == expected` | `grade(actual) ≥ threshold` (rubric / judge) |
| Verdict | one run | **pass rate** over N runs |
| Regression | golden values | golden *set* + minimum scores over time |

The grader itself gets ordinary unit tests — your deterministic skills supervise the new layer. Full session rides with mocking (mock the LLM in unit tests; eval the real one on a golden set). Taste it now: `code/07_beyond_asserts_evals_teaser.py`.

---

## Homework

1. Convert your **LLD-29 Splitwise engine**'s assert blocks into a real pytest suite — start with conservation.
2. **Parametrize** the split strategies over the boundary table (remainders 0/1/n−1, n=1, total=0, total<n).
3. One `pytest.raises` test for a rule violation + one *value* test for an expected outcome.
4. Extract repeated Arranges into **fixtures** (`fresh_group`, `group_with_debts`).
5. *Stretch:* your LLD-25 ParkingLot — full-lot path and freed-spot-reuse path.

**Next class — Mocking & Web/API tests:** test doubles, `monkeypatch`, DRF `APIClient`, and the promised **evals deep-dive**.
