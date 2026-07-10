# LLD-32 — Mocking & Web/API Tests

> **Module 4, session 2 — and we finish session 1's toolkit first.** Last class reached AAA & FIRST; today we complete the unit-testing tools (**parametrize, fixtures, errors & floats, testing time**), then move up a layer: **faking the awkward dependencies** (mocking), **testing the web endpoint** (DRF), and the **evals** deep-dive. The through-line: "inject the clock", "fake the gateway", "mock the LLM" are all the same move — a **test double**.

**How to use this class:** open `index.html` for the interactive page (recap of the fundamentals, the mocking toolkit, DRF API tests, the evals deep-dive, decision quizzes). This README is the same content in prose. Runnable examples live in [`code/`](code/README.md) — pure pytest, 21 tests green + a 10-stub homework.

---

## Part 1 — Finishing the unit-testing toolkit (from LLD-31)

### Step 4 · parametrize — one test, a table of cases
Turn a copy-pasted test into a **table**, filled from the **boundaries**: `0 · 1 · typical · the value where behaviour changes · the extreme`. pytest runs each row independently and names it, so a failure points at the exact case. Bugs cluster at the **cutoffs** (the `≥`-vs-`>` decisions) — test the cutoff *and* a neighbour on each side; values deep inside a band add rows, not information.

### Step 5 · fixtures — Arrange once
`@pytest.fixture` + ask-by-parameter-name = dependency injection for tests. Fresh per test by default (Independence, mechanised); fixtures compose; shared ones live in `conftest.py`.

### Step 6 · errors & the float trap
Rule violation → **raises** (test with `pytest.raises`, assert on the error object, check nothing half-applied). Expected outcome → **value** (a full lot returns `None`). Floats can't do equality (`0.1 + 0.2 != 0.3`): `pytest.approx` for continuous values, **integer paise** for money (exact, no epsilon).

### Step 7 · testing time — inject the clock
Code that calls `datetime.now()` is untestable and flaky-at-midnight. Depend on a **Clock**; a test passes a **FakeClock** frozen at any instant. **That FakeClock is a test double** — the doorway to Part 2.

---

## Part 2 — Mocking

### Why fake a dependency
Some collaborators can't run in a fast, repeatable unit test: **slow** (an 800ms gateway round-trip), **paid/risky** (real money, real emails), **flaky** (the network), **non-deterministic** (an LLM, the clock, `random`). The fix is a **test double** — a fast, free, predictable stand-in. Mock across **boundaries** (I/O, services, time, randomness); use the real thing for pure logic.

### Five kinds of double
- **Dummy** — filler, never used. **Stub** — canned answers (`return_value`). **Spy** — a stub that records calls. **Mock** — pre-set expectations it verifies. **Fake** — a real, lightweight implementation (in-memory dict for a DB).
- Python's `unittest.mock.Mock` can be stub/spy/mock in one. A **Fake** you write, because it holds state. Rule of thumb: **fake what you store into, mock what you just poke.**

### Three ways to slot a double in (prefer the earliest)
1. **Dependency injection** — the code takes its collaborator as a parameter; a test passes a different one. Cleanest, and improves the design.
2. **monkeypatch** (pytest fixture) — no seam? Swap an attribute / env var / function for one test; **auto-undone** afterwards.
3. **`unittest.mock`** — `Mock()` with `.return_value` (stub) and `.side_effect` (raise / sequence); `patch` swaps a name as a decorator or `with`-block.

### Where to patch — the #1 gotcha
**Patch the name where it is looked up, not where it is defined.** If `billing.py` does `from rates import get_rate`, patch `billing.get_rate` (its own copy), not `rates.get_rate`. If it does `import rates` and calls `rates.get_rate()`, patch `rates.get_rate`.

### Spying — assert the interaction
Some behaviour has no return value: `assert_called_once_with` pins count + args; `assert_not_called` guards the sad path (no receipt email when the charge fails). **Don't over-mock** — mocking everything couples the test to *how* the code is built, so a harmless refactor breaks a green test. Assert outcomes (via a fake) where you can.

---

## Part 3 — Web/API tests (DRF)

An **integration** test drives a real request through your view to a real (test) DB:
- `pytest-django` gives a **throwaway test database** (`@pytest.mark.django_db`), rolled back per test.
- DRF's **`APIClient`** makes real in-process requests — full middleware → view → serializer → ORM, no server, no network.
- Assert the **contract** (status code, response body) *and* the **side effect** (a row landed).
- `client.force_authenticate(user)` skips the login dance so the test stays focused on *its* behaviour.
- **Mocking meets the web:** when an endpoint calls something external mid-request (gateway, email, LLM), `patch` that call *inside* the API test — real request + real DB + mocked boundary.
- **Runnable version:** [`code/django_demo/`](code/django_demo/README.md) is a self-contained Django+DRF project with these exact `@pytest.mark.django_db` + `APIClient` tests (event CRUD, owner-only 403, and a checkout endpoint whose gateway is `patch`ed), all green.

---

## Part 4 — Evals (the deep-dive)

When the backend calls an LLM, `assert actual == expected` dies — two runs give two good-but-different answers. Two layers:
- **Layer A — unit tests, LLM mocked.** The code *around* the model (prompt building, parsing, fallbacks) is deterministic; mock the model and test it fast and free.
- **Layer B — the eval.** Score outputs against a **rubric** (0..1), over a **golden set** of inputs, and assert the **pass rate** — not any single string. One sloppy answer doesn't fail the build; a *degraded model* does.

| | Classic test | Eval |
|---|---|---|
| Output | deterministic | stochastic |
| Check | `actual == expected` | `grade(actual) ≥ threshold` (rubric / LLM-as-judge) |
| Verdict | one run | **pass rate** over a golden set |
| When it runs | every commit | nightly / pre-release |

**LLM-as-judge:** for rubric items a keyword check can't score (tone, relevance), ask another model to grade — a softer gate you spot-check against human labels. The grader is code, so it gets ordinary unit tests.

---

## Homework

1. **Warm-up: [`code/08_homework.py`](code/08_homework.py)** — a refund service + summarizer are written for you; 10 `pytest.skip` stubs across injection, monkeypatch, `Mock`, `patch.object`, spying and evals. Turn them all green.
2. Pick a service in **your Module-1 Django project** that calls something external and write an **`APIClient`** test that `patch`es the external call.
3. Add a **spy** test (no double-charge) and a **negative** test (`assert_not_called`) for a failure path.
4. *Stretch:* wrap an LLM/AI call behind a function, unit-test it with a **mocked** model, and sketch a 5-input **golden set** + rubric.

**Next class — Authentication-1:** AuthN vs AuthZ, tokens, and bcrypt password storage.
