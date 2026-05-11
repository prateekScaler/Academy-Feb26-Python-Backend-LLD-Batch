"""Closures — a function that remembers variables from its creation scope.

This is not magic. It's just: inner function + outer variable = closure.
"""


# --- Step 1: A function inside a function ---
def outer():
    message = "Hello from outer!"

    def inner():
        print(message)   # inner uses 'message' from outer

    inner()

outer()
# inner() has access to message even though message is in outer's scope.
# This is just normal scope rules (LEGB: Local → Enclosing → Global → Builtin)


# --- Step 2: Return the inner function ---
def make_greeter(greeting):
    """Returns a function that uses 'greeting'."""

    def greeter(name):
        return f"{greeting}, {name}!"  # 'greeting' is from make_greeter's scope

    return greeter   # return the function, don't call it

hello = make_greeter("Hello")
namaste = make_greeter("Namaste")

print(f"\nhello('Vipul') = '{hello('Vipul')}'")
print(f"namaste('Kaarthik') = '{namaste('Kaarthik')}'")


# make_greeter("Hello") has FINISHED running.
# But hello() still remembers greeting = "Hello".
# That's a closure: the inner function CLOSES OVER the outer variable.


# --- Step 3: Practical — counter ---
def make_counter(start=0):
    count = [start]   # list because we need to mutate (integers are immutable)

    def increment():
        count[0] += 1
        return count[0]

    return increment

counter_a = make_counter()
counter_b = make_counter(100)

print(f"\ncounter_a: {counter_a()}, {counter_a()}, {counter_a()}")  # 1, 2, 3
print(f"counter_b: {counter_b()}, {counter_b()}, {counter_b()}")    # 101, 102, 103
# Each counter has its OWN count. They don't interfere.


# --- Step 4: Practical — multiplier factory ---
def make_multiplier(factor):
    return lambda x: x * factor

double = make_multiplier(2)
triple = make_multiplier(3)

print(f"\ndouble(5) = {double(5)}")   # 10
print(f"triple(5) = {triple(5)}")     # 15
# The lambda closes over 'factor' from make_multiplier.


# --- Step 5: Practical — rate limiter ---
import time

def make_rate_limiter(max_calls, period_seconds):
    """Returns a function that limits calls per time period."""
    calls = []

    def is_allowed():
        now = time.time()
        # Remove old calls outside the window
        while calls and calls[0] < now - period_seconds:
            calls.pop(0)
        if len(calls) < max_calls:
            calls.append(now)
            return True
        return False

    return is_allowed

limiter = make_rate_limiter(3, 1.0)  # max 3 calls per second
for i in range(5):
    print(f"  Call {i+1}: {'allowed' if limiter() else 'BLOCKED'}")


# --- What IS a closure? ---
print("\n" + "=" * 50)
print("Closure = inner function + remembered outer variables")
print()
print("  def make_X(config):")
print("      def X(input):")
print("          # uses 'config' from outer scope")
print("      return X")
print()
print("  The returned function 'remembers' config even after")
print("  make_X has finished running. That's the closure.")
print()
print("  Real uses: counters, factories, callbacks, decorators,")
print("  rate limiters, memoization, middleware")
