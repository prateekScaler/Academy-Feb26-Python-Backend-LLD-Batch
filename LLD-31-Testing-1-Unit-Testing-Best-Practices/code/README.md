# LLD-31 · code/ — runnable examples

Pure **pytest** suites (44 tests, all green). One-time setup:

```bash
pip install pytest
```

Then run any file either way:

```bash
pytest -v 01_the_bug_a_test_catches.py     # the normal way
python3 01_the_bug_a_test_catches.py       # same thing — the file hands over to pytest
pytest -q 0*.py                            # the whole folder
```

## How do these tests "use" pytest when the word `pytest` never appears?

pytest is a **runner**, not a library you call — you don't invoke pytest, *pytest invokes you*:

- **Discovery by convention.** You run `pytest`, and it *imports your file and collects every function whose name starts with `test_`* — naming is the registration. (Note: auto-discovery looks for `test_*.py` files; our files are `01_*.py`, so we pass the filename explicitly.)
- **The bare `assert` is Python's own statement** — but pytest performs *assertion rewriting*: while importing your test file it rewrites the assert's bytecode so that on failure it can show both sides (`assert 9999 == 10000`) instead of a bare `AssertionError`.
- **You only import pytest for its extras**: `@pytest.mark.parametrize` (file 03), `@pytest.fixture` (file 04), `pytest.raises` / `pytest.approx` (file 05). Files 01, 02, 06, 07 need no import at all.
- This is the **Hollywood principle** — *"don't call us, we'll call you"* — the same inversion of control as Django calling your view function: you write plain functions to a naming convention, the framework finds and drives them.

| File | What it teaches |
|---|---|
| `01_the_bug_a_test_catches.py` | The motivating story — a "tidy" refactor reorders two discount lines and silently overcharges ₹5 on every order; one worked-example test catches it forever. Why tests exist: *regression*. |
| `02_first_tests_aaa.py` | Test anatomy: **Arrange–Act–Assert**, the name states the behaviour, one behaviour per test. A mini `ExpenseGroup` under test + an anti-example. |
| `03_parametrize_edge_cases.py` | `@pytest.mark.parametrize` — one test, a **table of boundary cases** (remainders, n=1, total=0, total<n) + the LLD-23 winner-check across all 8 lines. |
| `04_fixtures_parking.py` | **Fixtures**: extract the shared Arrange (`empty_lot`, `full_lot` — fixtures compose) and test independence. Full lot returns `None` — a value, not an exception (LLD-24). |
| `05_exceptions_and_floats.py` | `pytest.raises` for rule violations (overdraw), asserting on the error object, error paths that don't half-apply. Plus the float trap: `0.1+0.2 != 0.3`, `pytest.approx`, and why money = integer paise. |
| `06_testing_time.py` | Untestable `datetime.now()` → **inject a Clock** (LLD-30 pattern). `FakeClock` freeze + `advance()` = time travel; token-expiry leeway; seeded randomness. |
| `07_beyond_asserts_evals_teaser.py` | The paradigm shift: when output is **non-deterministic** (LLMs), equality dies. **Grade against a rubric**, threshold the score, assert the **pass rate** over many runs. Evals get a full session later this module. |
| `08_homework.py` | **HOMEWORK** — the code under test (a cinema backend: refund bands, GiftCard, ScreenSeats, matinee clock) is complete and correct; **you write the tests**. 12 `pytest.skip` stubs, one per lesson — delete each skip and turn it green. Starts `12 skipped`, ends all `PASSED`. |
