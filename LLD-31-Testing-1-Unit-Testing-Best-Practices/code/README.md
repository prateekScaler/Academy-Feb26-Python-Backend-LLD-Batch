# LLD-31 · code/ — runnable examples

Every file runs **two ways** (both verified green, 43 tests total):

```bash
# no install needed — a tiny fallback runner is built into each file
python3 01_the_bug_a_test_catches.py

# or the real thing, if you have it
pip install pytest
pytest -v 01_the_bug_a_test_catches.py     # or:  pytest -q 0*.py
```

Each file starts with a short "run-anywhere shim" — **skip reading it**; it only
exists so `python3 file.py` works on machines without pytest. The lesson code
is everything below it.

| File | What it teaches |
|---|---|
| `01_the_bug_a_test_catches.py` | The motivating story — a "harmless" float refactor silently loses a paisa (LLD-29's penny problem); a **conservation test** catches it forever. Why tests exist: *regression*. |
| `02_first_tests_aaa.py` | Test anatomy: **Arrange–Act–Assert**, the name states the behaviour, one behaviour per test. A mini `ExpenseGroup` under test + an anti-example. |
| `03_parametrize_edge_cases.py` | `@pytest.mark.parametrize` — one test, a **table of boundary cases** (remainders, n=1, total=0, total<n) + the LLD-23 winner-check across all 8 lines. |
| `04_fixtures_parking.py` | **Fixtures**: extract the shared Arrange (`empty_lot`, `full_lot`), yield-style teardown, and test independence. Full lot returns `None` — a value, not an exception (LLD-24). |
| `05_exceptions_and_floats.py` | `pytest.raises` for rule violations (overdraw), asserting on the error object, error paths that don't half-apply. Plus the float trap: `0.1+0.2 != 0.3`, `pytest.approx`, and why money = integer paise. |
| `06_testing_time.py` | Untestable `datetime.now()` → **inject a Clock** (LLD-30 pattern). `FakeClock` freeze + `advance()` = time travel; token-expiry leeway; seeded randomness. |
| `07_beyond_asserts_evals_teaser.py` | The paradigm shift: when output is **non-deterministic** (LLMs), equality dies. **Grade against a rubric**, threshold the score, assert the **pass rate** over many runs. Evals get a full session later this module. |
