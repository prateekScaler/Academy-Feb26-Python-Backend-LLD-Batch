# django_demo — runnable DRF `@pytest.mark.django_db` tests

A **self-contained** Django + DRF project (one app, in-memory SQLite) so the Part 3
web/API examples actually run. Unlike the rest of `code/` (pure stdlib + pytest),
these need Django:

```bash
pip install django djangorestframework pytest-django
cd django_demo
pytest -v          # 6 tests, all green
```

`pytest.ini` points `DJANGO_SETTINGS_MODULE` at `demoproj.settings`, so `pytest`
picks everything up — no `manage.py`, no server, no external DB.

## What's here

| File | Role |
|---|---|
| `demoproj/settings.py` · `urls.py` | Minimal project: DRF + one app, `:memory:` SQLite, a router for `/api/events/` and `/api/checkout/`. |
| `demoapp/models.py` | `Event(title, owner→User)` and `Order(cart_id, amount, receipt, status)`. |
| `demoapp/views.py` | `EventViewSet` guarded by `IsAuthenticated` + an **`IsOwner`** object permission (`obj.owner_id == request.user.id`); `perform_create` sets `owner = request.user`. A `checkout` view that calls the **gateway boundary**. |
| `demoapp/gateways.py` | `stripe_gateway` — the real (raising) boundary that tests `patch`. |
| `test_events_api.py` | The **contract + authorization** tests: create → 201 & persisted & owner set; anonymous → 401/403; owner deletes → 204; **non-owner → 403** (row survives). |
| `test_checkout_api.py` | **Part 2 meets Part 3:** drive `/api/checkout/` with `APIClient` but `@patch("demoapp.views.stripe_gateway")` — assert 201, `charge` called once (spy), the `Order` persisted as `PAID`; and that a failed charge leaves no order. |

## The two things to notice

- **`@pytest.mark.django_db`** — pytest-django gives each marked test a throwaway
  database, rolled back afterwards. The `client` (`APIClient`) and `django_user_model`
  fixtures come from pytest-django too.
- **Patch where it's looked up** — `checkout` does `from demoapp.gateways import stripe_gateway`,
  so the view holds its own reference; the test patches `demoapp.views.stripe_gateway`
  (not `demoapp.gateways.stripe_gateway`).
