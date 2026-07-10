# LLD-32 · code/ — runnable examples

Pure **pytest** suites (21 tests green + a 10-stub homework). One-time setup:

```bash
pip install pytest
```

Then run any file either way:

```bash
pytest -v 01_why_mock.py            # the normal way
python3 01_why_mock.py              # same thing — it hands over to pytest
pytest -q 0*.py                     # the whole folder
```

The mocking tools here are **stdlib** — `unittest.mock` and pytest's built-in
`monkeypatch` — nothing to install beyond pytest itself. The one exception is
[`django_demo/`](django_demo/README.md), which needs Django + DRF + pytest-django
(its own README explains).

| File | What it teaches |
|---|---|
| `01_why_mock.py` | The awkward dependency (a payment gateway: slow, paid, flaky). Slot in a **test double** via dependency injection — the same move as LLD-31's Clock — and test with a hand-written fake. |
| `02_monkeypatch.py` | When you can't add a seam: pytest's `monkeypatch` swaps a function / env var / `random` for one test and **undoes it automatically**. |
| `03_mock_objects.py` | `unittest.mock.Mock` — attributes spring into being; `.return_value`, `.side_effect` (raise / sequence), and call assertions. |
| `04_where_to_patch.py` | `patch` as decorator + context manager, and the #1 gotcha: **patch where the name is looked up, not where it's defined** (shown with `patch.object`). |
| `05_spying_on_calls.py` | A Mock is a spy: `assert_called_once_with`, `call_count`, and the important negatives — `assert_not_called` (no email when the charge fails). |
| `06_fake_vs_mock.py` | Two doubles, two jobs: a **fake** in-memory repo (assert real stored state) vs a **mock** notifier (assert the interaction). When to reach for each. |
| `07_evals_golden_set.py` | The **evals** deep-dive: unit-test the code around the model with the LLM **mocked** (layer A), then **eval** quality on a golden set — rubric grade, an LLM-as-judge stub, and a **pass-rate** assertion (layer B). |
| `08_homework.py` | **HOMEWORK** — a refund service + summarizer are written for you; 10 `pytest.skip` stubs across injection, monkeypatch, Mock, `patch.object`, spying, and evals. Delete each skip and turn it green. |
| [`django_demo/`](django_demo/README.md) | **Runnable DRF web/API tests** &mdash; a self-contained Django project with `@pytest.mark.django_db` + `APIClient`: the event CRUD contract, the owner-only authorization rule (403 for non-owners), and a checkout endpoint whose Stripe call is `patch`ed. Needs `pip install django djangorestframework pytest-django`. |

> **The recap fundamentals** (parametrize / fixtures / raises+floats / testing time) from the first half of this class live in the previous folder — [`../LLD-31-Testing-1-Unit-Testing-Best-Practices/code/`](../../LLD-31-Testing-1-Unit-Testing-Best-Practices/code/) files `03`–`06`.
