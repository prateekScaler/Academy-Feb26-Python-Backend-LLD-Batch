"""Decorators — closures in disguise. A preview.

A decorator is a function that takes a function and returns a new function.
That's it. It's just a closure that wraps the original function.
"""
import time


# --- Step 1: A function that wraps another function ---
def timer(func):
    """Wrap func with timing logic."""

    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)     # call the original function
        elapsed = time.time() - start
        print(f"  {func.__name__} took {elapsed:.4f}s")
        return result

    return wrapper   # return the wrapped version


# --- Step 2: Use it manually ---
def slow_add(a, b):
    time.sleep(0.1)
    return a + b

timed_add = timer(slow_add)   # timer wraps slow_add
result = timed_add(3, 4)
print(f"  Result: {result}\n")


# --- Step 3: The @ syntax is just shorthand ---
@timer                         # same as: calculate = timer(calculate)
def calculate(n):
    """Sum of squares."""
    return sum(x**2 for x in range(n))

result = calculate(10000)
print(f"  Result: {result}\n")

# @timer is syntactic sugar for:
#   calculate = timer(calculate)
# It's a closure: wrapper() remembers 'func' (the original calculate)


# --- Step 4: Another decorator — logging ---
def log_calls(func):
    call_count = [0]   # closure variable

    def wrapper(*args, **kwargs):
        call_count[0] += 1
        print(f"  [{func.__name__}] call #{call_count[0]}, args={args}")
        return func(*args, **kwargs)

    return wrapper

@log_calls
def greet(name):
    return f"Hello, {name}!"

greet("Vipul")
greet("Kaarthik")
greet("Ajit")


# --- The decorator pattern ---
print("\n" + "=" * 50)
print("Decorator = closure that wraps a function")
print()
print("  def my_decorator(func):       # takes a function")
print("      def wrapper(*args):       # creates a new function")
print("          # do something before")
print("          result = func(*args)  # call original")
print("          # do something after")
print("          return result")
print("      return wrapper            # return the new function")
print()
print("  @my_decorator                 # sugar for: f = my_decorator(f)")
print("  def f(): ...")
print()
print("  Real uses: @timer, @cache, @login_required,")
print("  @app.route, @retry, @validate, @deprecated")
