"""Functions are objects — you can store them, pass them, return them.

This is the foundation of everything in this class.
If you understand this, lambda/map/filter/closures all make sense.
"""


# --- Step 1: A function is just an object with a name ---
def greet(name):
    return f"Hello, {name}!"

# greet is a VARIABLE that points to a function object
print(type(greet))          # <class 'function'>
print(greet)                # <function greet at 0x...>
print(greet("Vipul"))       # "Hello, Vipul!"


# --- Step 2: You can store a function in a variable ---
say_hi = greet              # NO parentheses — we're copying the reference, not calling it
print(say_hi("Kaarthik"))   # "Hello, Kaarthik!" — same function, different name

# greet and say_hi point to the SAME function object
print(greet is say_hi)      # True


# --- Step 3: You can put functions in a list ---
def add(a, b): return a + b
def sub(a, b): return a - b
def mul(a, b): return a * b

operations = [add, sub, mul]

for op in operations:
    print(f"  {op.__name__}(10, 3) = {op(10, 3)}")
# add(10, 3) = 13
# sub(10, 3) = 7
# mul(10, 3) = 30


# --- Step 4: You can pass a function to another function ---
def apply(func, a, b):
    """Takes a function and two numbers, calls the function."""
    return func(a, b)

print(f"\napply(add, 5, 3) = {apply(add, 5, 3)}")   # 8
print(f"apply(mul, 5, 3) = {apply(mul, 5, 3)}")     # 15


# --- Step 5: You can return a function from a function ---
def make_greeter(greeting):
    """Returns a NEW function that uses the greeting."""
    def greeter(name):
        return f"{greeting}, {name}!"
    return greeter          # return the function, don't call it

hello = make_greeter("Hello")
namaste = make_greeter("Namaste")

print(f"\nhello('Vipul') = '{hello('Vipul')}'")         # "Hello, Vipul!"
print(f"namaste('Kaarthik') = '{namaste('Kaarthik')}'")  # "Namaste, Kaarthik!"


# --- Step 5b: Another example — discount factory ---
def make_discount(percent):
    """Returns a function that applies the given discount."""
    def apply_discount(price):
        return price * (1 - percent / 100)
    return apply_discount

student_discount = make_discount(10)
premium_discount = make_discount(25)

print(f"\nstudent_discount(1000) = {student_discount(1000)}")  # 900.0
print(f"premium_discount(1000) = {premium_discount(1000)}")    # 750.0


# --- Summary ---
print("\n" + "=" * 50)
print("Functions are first-class objects in Python:")
print("  1. Store in variables:  say_hi = greet")
print("  2. Put in lists:        ops = [add, sub, mul]")
print("  3. Pass as arguments:   apply(add, 5, 3)")
print("  4. Return from funcs:   make_greeter('Hello')")
print("This is WHY lambda, map, filter, decorators work.")
