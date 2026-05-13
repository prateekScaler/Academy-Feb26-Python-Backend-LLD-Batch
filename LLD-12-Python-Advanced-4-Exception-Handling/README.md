
# LLD-12: Python Advanced-4 — Exception Handling & Miscellaneous

> You learned try/except in Django. Now let's master it — custom exceptions, context managers, EAFP, i18n, and copy semantics.

---

## Recap — Django Exception Handling & Lambda/FP

> **Q1 (Django):** `MenuItem.objects.get(id=99999)` without try/except. What happens?

<details><summary>Answer</summary>

**`MenuItem.DoesNotExist`** exception crashes the request. Users see Django's ugly error page (in debug) or a 500 error (in production). Always use `try/except` or `get_object_or_404()`.

</details>

> **Q2 (Django):** In `try/except/else/finally` — when does `else` run?

<details><summary>Answer</summary>

**Only if `try` succeeded with NO exception.** Not after `except`. It's the "success path." Why not just put code after `try`? Because that runs even if `except` handled an error.

</details>

> **Q3 (Django):** What does `get_object_or_404(MenuItem, id=99)` do?

<details><summary>Answer</summary>

Returns the object if found, **automatically returns a 404 response** if `DoesNotExist`. It's a shortcut for the try/except/return-404 pattern.

</details>

> **Q4 (Decorators):** Why do we use `@functools.wraps(func)` in a decorator?

<details><summary>Answer</summary>

Without it, `my_view.__name__` shows `"wrapper"` instead of `"my_view"`. `@wraps(func)` preserves the original function's name, docstring, and metadata. Critical for debugging and introspection.

</details>

> **Q5 (Lambda):** What does `sorted(students, key=lambda s: s["gpa"], reverse=True)` return?

<details><summary>Answer</summary>

Students sorted by GPA **highest first** (descending). `key=lambda s: s["gpa"]` extracts the sort key, `reverse=True` reverses the order.

</details>

---

## Exception Hierarchy

```
BaseException
├── SystemExit               # sys.exit()
├── KeyboardInterrupt        # Ctrl+C
├── GeneratorExit
└── Exception                ← YOU catch THIS
    ├── ValueError
    ├── TypeError
    ├── KeyError
    ├── IndexError
    ├── AttributeError
    ├── FileNotFoundError
    ├── RuntimeError
    └── ... many more
```

### Why never write bare `except:`?

```python
# BAD: catches Ctrl+C and sys.exit()!
try:
    something()
except:          # bare except = catches BaseException
    pass         # user can NEVER stop the program!

# GOOD: catches errors, not system signals
try:
    something()
except Exception as e:
    log(e)
```

### Order matters: specific before general

```python
try:
    d = {"a": 1}
    val = d["b"]
except KeyError:            # specific — catches this
    print("Key not found")
except Exception:           # general — fallback
    print("Something else")
```

If you put `Exception` first, `KeyError` never runs.

---

## Custom Exceptions

### The Problem

```python
raise ValueError("Insufficient stock")    # can't distinguish
raise ValueError("Invalid email")          # from this one
```

### The Fix: Custom hierarchy with data

```python
class PaymentError(Exception):
    """Base for all payment errors."""
    pass

class InsufficientFundsError(PaymentError):
    def __init__(self, balance: float, amount: float):
        self.balance = balance
        self.amount = amount
        self.deficit = amount - balance
        super().__init__(f"Cannot pay ₹{amount}: only ₹{balance} available")

class PaymentGatewayError(PaymentError):
    def __init__(self, gateway: str, status_code: int):
        self.gateway = gateway
        self.status_code = status_code
        super().__init__(f"{gateway} returned {status_code}")
```

### Catching parent catches all children

```python
try:
    raise InsufficientFundsError(500, 1000)
except PaymentError as e:    # catches ANY payment error
    print(f"Payment failed: {e}")
    print(f"Deficit: ₹{e.deficit}")
```

### Best practices

1. Inherit from `Exception`, never `BaseException`
2. Create a base error per module (`PaymentError`, `AuthError`)
3. Store data as attributes (`balance`, `amount`, not just message strings)
4. Use hierarchy: `except PaymentError` catches all payment errors

---

## Context Managers — The `with` Statement

### Problem: forgetting to close resources

```python
# BAD: if process_data crashes, file never closes!
f = open("data.txt")
data = process_data(f.read())
f.close()                      # never reached on error

# GOOD: 'with' auto-closes even on exception
with open("data.txt") as f:
    data = process_data(f.read())
# f.close() called automatically
```

### How it works

```python
class ManagedFile:
    def __enter__(self):
        self.file = open(self.filename)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()         # ALWAYS runs
        return False              # don't suppress exceptions
```

### The easy way: @contextmanager

```python
from contextlib import contextmanager

@contextmanager
def timer(label):
    import time
    start = time.time()
    yield                         # ← the 'with' block runs here
    print(f"{label}: {time.time() - start:.4f}s")

with timer("computation"):
    total = sum(range(1_000_000))
```

### suppress() — ignore specific exceptions

```python
from contextlib import suppress

with suppress(FileNotFoundError):
    os.remove("/tmp/maybe_exists.txt")
# No crash if file doesn't exist
```

---

## Exception Chaining — `raise X from Y`

```python
# BAD: original cause is lost
try:
    raise ConnectionError("port 5432 refused")
except ConnectionError:
    raise UserNotFoundError("Could not find user")
    # original ConnectionError context is hidden!

# GOOD: chain preserves the cause
try:
    raise ConnectionError("port 5432 refused")
except ConnectionError as e:
    raise UserNotFoundError("Could not find user") from e
    # traceback shows BOTH errors
```

- `raise X from Y` — show both errors (most common)
- `raise X from None` — intentionally hide the original
- `raise` — re-raise current exception unchanged

---

## EAFP vs LBYL

| | LBYL (Look Before You Leap) | EAFP (Easier to Ask Forgiveness) |
|---|---|---|
| **Style** | Check first, then act | Just do it, handle errors |
| **Example** | `if "key" in d: val = d["key"]` | `try: val = d["key"] except KeyError: ...` |
| **Origin** | Java, C | **Python** (preferred) |
| **Race condition** | Yes (file can be deleted between check and open) | No |
| **Code** | More if-checks | More try/except |

```python
# LBYL: race condition!
if os.path.exists(filename):       # file could be deleted RIGHT HERE
    f = open(filename)

# EAFP: no race condition
try:
    f = open(filename)
except FileNotFoundError:
    handle_missing()
```

> Python favors EAFP because exceptions are cheap, duck typing works with it, and there are no race conditions.

---

## Django i18n in Exception Messages

```python
from django.utils.translation import gettext_lazy as _

class AppError(Exception):
    default_message = _("An error occurred")
    error_code = "GENERIC_ERROR"
    status_code = 500

    def __init__(self, message=None, **kwargs):
        self.message = message or self.default_message
        self.details = kwargs
        super().__init__(self.message)

    def to_dict(self):
        return {
            "error_code": self.error_code,
            "message": str(self.message),
            "details": self.details,
        }

class InsufficientStockError(AppError):
    default_message = _("Only %(available)s items in stock, %(requested)s requested")
    error_code = "INSUFFICIENT_STOCK"
    status_code = 400
```

### Django i18n setup

```bash
# settings.py
LANGUAGE_CODE = 'en'
USE_I18N = True
LOCALE_PATHS = [BASE_DIR / 'locale']
LANGUAGES = [('en', 'English'), ('hi', 'Hindi'), ('fr', 'French')]

# Generate translation files
python manage.py makemessages -l hi
# Edit locale/hi/LC_MESSAGES/django.po
python manage.py compilemessages
```

Django selects language from: Accept-Language header → session → cookie → `LANGUAGE_CODE` default.

---

## Copy Constructor — Shallow vs Deep Copy

Python doesn't have C++/Java-style copy constructors. It uses `copy.copy()` and `copy.deepcopy()`.

### Assignment is NOT copying

```python
original = [1, 2, [3, 4]]
alias = original              # SAME object, different name
alias.append(5)
print(original)               # [1, 2, [3, 4], 5] — MODIFIED!
```

### Shallow copy — new outer, shared inner

```python
import copy
original = [[1, 2], [3, 4]]
shallow = original.copy()     # or: list(original), original[:], copy.copy()

shallow[0].append(99)
print(original)               # [[1, 2, 99], [3, 4]] — inner list SHARED!
```

### Deep copy — completely independent

```python
original = [[1, 2], [3, 4]]
deep = copy.deepcopy(original)

deep[0].append(99)
print(original)               # [[1, 2], [3, 4]] — UNCHANGED!
```

### Summary

| Operation | Syntax | Outer list | Inner lists |
|---|---|---|---|
| Assignment | `b = a` | Same object | Same object |
| Shallow copy | `a.copy()`, `copy.copy(a)` | **New** object | **Shared** (same references) |
| Deep copy | `copy.deepcopy(a)` | **New** object | **New** objects (independent) |

> **Rule:** If your object has nested mutables (list of lists, object with list attributes), use `deepcopy`. Otherwise, shallow copy is fine.

### Custom `__copy__` and `__deepcopy__`

```python
class Config:
    def __copy__(self):
        new = Config.__new__(Config)
        new.settings = self.settings   # shared
        return new

    def __deepcopy__(self, memo):
        new = Config.__new__(Config)
        new.settings = copy.deepcopy(self.settings, memo)  # independent
        return new
```

---

## Best Practices

### DO

- Catch **specific** exceptions (`ValueError`, `KeyError`, `PaymentError`)
- **Log** exceptions (`logger.exception("msg")` includes traceback)
- Use **custom exceptions** for business logic (with data attributes)
- Keep try blocks **small and focused**
- Use `with` for resource cleanup (files, connections, locks)
- Prefer **EAFP** over LBYL in Python
- Use `raise X from Y` to chain exceptions

### DON'T

- `except:` (bare) — catches Ctrl+C!
- `except Exception: pass` — silently swallows errors
- Too-broad try blocks — hard to debug
- Exceptions for expected flow control (use if-check instead)
- `except Exception as e: print(e)` without logging the traceback

---

## Code Files

| File | What It Demonstrates |
|---|---|
| `01_exception_hierarchy.py` | BaseException tree, multiple except, order matters |
| `02_try_else_finally.py` | When each block runs, finally with return |
| `03_custom_exceptions.py` | PaymentError hierarchy, storing data, catching parent |
| `04_context_managers.py` | with statement, __enter__/__exit__, @contextmanager, suppress |
| `05_exception_chaining.py` | raise X from Y, from None, __cause__ |
| `06_django_i18n_exceptions.py` | gettext_lazy, AppError with error_code, Django setup |
| `07_copy_constructor.py` | Assignment, shallow, deep, objects, custom __copy__ |
| `08_eafp_vs_lbyl.py` | Two philosophies, race condition, Pythonic style |
| `09_exception_best_practices.py` | Do's and don'ts, logging, specific catches |

---

## Key Takeaways

1. **Exception hierarchy matters** — catch specific exceptions, never bare `except:`
2. **Custom exceptions encode business logic** — `InsufficientFundsError(balance=500, amount=1000)`
3. **Context managers guarantee cleanup** — `with` calls `__exit__` even on exception
4. **EAFP > LBYL in Python** — try/except is cheaper and avoids race conditions
5. **Copy semantics** — assignment = alias, `.copy()` = shallow (shared inner), `deepcopy` = independent
6. **i18n in Django** — `gettext_lazy(_())` for translatable error messages

**Advanced Programming Concepts module complete! Next: SOLID Principles.**

---

## Resources

- [Python docs — Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
- [Python docs — Built-in Exceptions](https://docs.python.org/3/library/exceptions.html)
- [Python docs — contextlib](https://docs.python.org/3/library/contextlib.html)
- [Python docs — copy module](https://docs.python.org/3/library/copy.html)
- [Django docs — Translation](https://docs.djangoproject.com/5.0/topics/i18n/translation/)
- [Real Python — Exception Handling](https://realpython.com/python-exceptions/)
- [Real Python — Context Managers](https://realpython.com/python-with-statement/)
