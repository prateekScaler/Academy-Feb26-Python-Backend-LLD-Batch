# Class 9: Quick Revision Guide

Use this to revise before interviews or when you need a refresher.

---

## 1. Exception Handling

### What happens without exception handling?
```python
item = MenuItem.objects.get(id=99999)  # Crashes if not found!
```
Your program crashes with `MenuItem.DoesNotExist`. Users see an ugly error page.

### The fix: try-except
```python
try:
    item = MenuItem.objects.get(id=99999)
except MenuItem.DoesNotExist:
    return HttpResponse("Item not found", status=404)
```

### When to use `else`?
Code in `else` runs ONLY if `try` succeeded. Why not just put it after `except`?

```python
# WRONG - crashes if file doesn't exist
try:
    f = open("data.txt")
except FileNotFoundError:
    print("Not found")
data = f.read()  # f doesn't exist here!

# RIGHT - else only runs if open() worked
try:
    f = open("data.txt")
except FileNotFoundError:
    print("Not found")
else:
    data = f.read()  # Safe - f definitely exists
    f.close()
```

### When to use `finally`?
For cleanup that MUST happen, even if there's an error or early return.

```python
try:
    db = connect_to_database()
    do_stuff(db)
except DatabaseError:
    log_error()
finally:
    db.close()  # Always runs - prevents connection leaks!
```

**Resource leaks to watch for:** file handles, database connections, network sockets, locks

### Django shortcut
```python
from django.shortcuts import get_object_or_404

item = get_object_or_404(MenuItem, id=item_id)
# Returns item if found, auto-returns 404 page if not
```

### Re-raising exceptions
Log the error but let someone else handle the response:
```python
def process_payment(order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist as e:
        logger.error(f"Order {order_id} not found")
        raise  # Re-raise so the view can return 404
```

### Custom exceptions
```python
class InsufficientStockError(Exception):
    def __init__(self, available, requested):
        self.available = available
        self.requested = requested
        super().__init__(f"Only {available} in stock, {requested} requested")

# Usage
if item.stock < quantity:
    raise InsufficientStockError(item.stock, quantity)
```

---

## 2. Decorators

### What is a decorator?
A function that wraps another function to add behavior before/after it runs.

```python
@timing_decorator
def my_view(request):
    ...

# Is the same as:
my_view = timing_decorator(my_view)
```

### Basic decorator template (memorize this!)
```python
import functools

def my_decorator(func):
    @functools.wraps(func)  # Preserves original function's name & docstring
    def wrapper(*args, **kwargs):
        # Code here runs BEFORE the function
        print("Before")

        result = func(*args, **kwargs)  # Call the original function

        # Code here runs AFTER the function
        print("After")

        return result
    return wrapper
```

### Why `@functools.wraps(func)`?
Without it, debugging shows "wrapper" instead of your function's real name:
```python
print(my_view.__name__)  # Without wraps: "wrapper"
print(my_view.__name__)  # With wraps: "my_view"
```

### What are `*args` and `**kwargs`?
- `*args` = all positional arguments as a tuple
- `**kwargs` = all keyword arguments as a dictionary

```python
def example(*args, **kwargs):
    print(args)    # (1, 2, 3)
    print(kwargs)  # {'name': 'John', 'age': 25}

example(1, 2, 3, name='John', age=25)
```

### Decorator WITH arguments (3 levels)
When your decorator needs parameters like `@repeat(times=3)`:

```python
def repeat(times):              # Level 1: takes the argument
    def decorator(func):        # Level 2: takes the function
        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # Level 3: takes function's args
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)
def say_hello():
    print("Hello!")

say_hello()  # Prints "Hello!" three times
```

### Common Django decorators
```python
@login_required          # Must be logged in
@permission_required('app.add_item')  # Must have permission
@require_POST            # Only allow POST requests
@cache_page(60 * 15)     # Cache for 15 minutes
```

---

## 3. Middleware

### What is middleware?
Code that runs on EVERY request/response. Like a checkpoint all traffic must pass through.

```
Request → Middleware1 → Middleware2 → View → Middleware2 → Middleware1 → Response
```

### Basic middleware template
```python
class TimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response  # This is the next thing in the chain

    def __call__(self, request):
        # BEFORE view (request going in)
        start = time.time()

        response = self.get_response(request)  # Call view (or next middleware)

        # AFTER view (response going out)
        duration = time.time() - start
        response['X-Request-Time'] = f'{duration:.2f}s'

        return response
```

### What is `get_response`?
It's the next step in the chain - either the next middleware or the view itself. Calling `self.get_response(request)` passes the request forward and waits for the response to come back.

### Registering middleware
Add to `settings.py`:
```python
MIDDLEWARE = [
    # ... existing middleware ...
    'myapp.middleware.TimingMiddleware',  # Add yours at the end
]
```

### Where to put middleware files?
- `yourapp/middleware.py` - app-specific middleware
- `project/middleware.py` - project-wide middleware

---

## 4. Middleware vs Decorator - Quick Decision Guide

| Scenario | Use |
|----------|-----|
| Log ALL requests | Middleware |
| Auth on 5 specific views | Decorator (`@login_required`) |
| Add security headers to all responses | Middleware |
| Rate limit one API endpoint | Decorator |
| Site-wide maintenance mode | Middleware |
| Cache one specific page | Decorator (`@cache_page`) |

**Rule of thumb:**
- **Middleware** = applies to EVERYTHING automatically
- **Decorator** = you CHOOSE which views to apply it to

---

## 5. Quick Self-Test

1. What exception does `.get()` raise if nothing found?
2. When would you use `else` with try-except?
3. What does `@functools.wraps(func)` do?
4. Why does a decorator with arguments need 3 levels of functions?
5. What's the difference between middleware and decorator?

<details>
<summary>Answers</summary>

1. `Model.DoesNotExist` (e.g., `MenuItem.DoesNotExist`)
2. When you need code to run only if `try` succeeded, especially when variables are only created in the `try` block
3. Preserves the original function's `__name__` and `__doc__` (docstring)
4. Level 1 takes the argument, Level 2 takes the function, Level 3 takes the function's arguments
5. Middleware runs on ALL requests; decorators only on views you explicitly decorate

</details>
