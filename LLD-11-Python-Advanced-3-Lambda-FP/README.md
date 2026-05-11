
# LLD-11: Python Advanced-3 — Lambda Functions and Functional Programming

> Functions are objects. Once you see that, lambda, map, filter, closures, and decorators all click.

---

## Recap — Collections

> **Q:** `d = defaultdict(list)` — what does `d["new_key"]` return without setting it first?

<details><summary>Answer</summary>

**`[]`** — an empty list. That's the whole point of defaultdict: accessing a missing key auto-creates it using the factory function (here `list`). No KeyError.

</details>

> **Q:** `dq = deque(maxlen=3)` — you append 1, 2, 3, 4, 5. What's in `dq`?

<details><summary>Answer</summary>

**`deque([3, 4, 5])`** — maxlen=3 means only the last 3 items are kept. When you append 4, item 1 is auto-removed. When you append 5, item 2 is auto-removed.

</details>

> **Q:** `Counter("mississippi")["s"]` = ?

<details><summary>Answer</summary>

**4** — Counter counts each character: `{'i': 4, 's': 4, 'p': 2, 'm': 1}`. The letter 's' appears 4 times.

</details>

---

## Functions Are Objects — The Foundation

This is the most important idea in this class. Everything else builds on it.

### Step 1: A function IS an object

```python
def greet(name):
    return f"Hello, {name}!"

print(type(greet))   # <class 'function'>
print(greet)         # <function greet at 0x...>
```

A function is just a variable that points to a function object. Like `x = 42` makes `x` point to an integer, `def greet(...)` makes `greet` point to a function.

### Step 2: Store in a variable

```python
say_hi = greet        # NO parentheses — copying the reference
print(say_hi("Kaarthik"))  # "Hello, Kaarthik!" — same function, different name
```

`greet` vs `greet()`:
- `greet` = the function object itself (like a recipe card)
- `greet()` = calling the function (like cooking the recipe)

### Step 3: Pass as argument

```python
def apply(func, a, b):
    return func(a, b)

apply(add, 5, 3)  # 8 — we passed the add function to apply
```

### Step 4: Return from a function

```python
def make_greeter(greeting):
    def greeter(name):
        return f"{greeting}, {name}!"
    return greeter

hello = make_greeter("Hello")
hello("Vipul")  # "Hello, Vipul!"
```

**Another example — a discount factory:**

```python
def make_discount(percent):
    """Returns a function that applies the given discount."""
    def apply_discount(price):
        return price * (1 - percent / 100)
    return apply_discount

student_discount = make_discount(10)   # 10% off
premium_discount = make_discount(25)   # 25% off

print(student_discount(1000))  # 900.0
print(premium_discount(1000))  # 750.0
```

> **This is WHY lambda, map, filter, decorators, and closures work.** They all depend on functions being objects you can pass around.

---

## Lambda — A Function Without a Name

### The Idea

```python
# The long way:
def double(x):
    return x * 2

# The short way (same thing):
double = lambda x: x * 2
```

A lambda is just a shortcut for a tiny function. No name, one expression, the expression IS the return value.

### Syntax

```python
lambda x: x * 2              # one parameter
lambda a, b: a + b           # two parameters
lambda: 3.14                 # no parameters
lambda x: "even" if x % 2 == 0 else "odd"  # with ternary
```

### Where Lambda Shines

**1. Sorting by a key:**
```python
# Lambda (concise):
students = [
    {"name": "Vipul", "age": 22},
    {"name": "Kaarthik", "age": 20},
    {"name": "Ajit", "age": 25},
]
sorted(students, key=lambda s: s["age"])

# Without lambda (verbose):
def get_age(student):
    return student["age"]
sorted(students, key=get_age)
# A whole function just to extract one field!
```

**2. max/min by a key:**
```python
# Lambda:
oldest = max(students, key=lambda s: s["age"])
shortest_name = min(students, key=lambda s: len(s["name"]))

# Without lambda:
def get_age(student):
    return student["age"]
def get_name_length(student):
    return len(student["name"])
oldest = max(students, key=get_age)
# 2 extra functions for one-time use
```

**3. Dict of operations:**
```python
# Lambda (compact dispatch table):
ops = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b}
print(ops["+"](3, 4))  # 7

# OOP approach:
class Calculator:
    def add(self, a, b): return a + b
    def sub(self, a, b): return a - b
    def compute(self, op, a, b):
        if op == "+": return self.add(a, b)
        # ... way more code for a simple lookup
```

### Rules

- **One expression only** — no `if`/`for`/multiple statements
- **Use inline** — `sorted(key=lambda ...)` is the sweet spot
- **If it needs a name, use `def`** — `double = lambda x: x * 2` is an anti-pattern
- **If it needs explanation, use `def`** — readability counts

> **Q:** What's wrong with this code?
> ```python
> double = lambda x: x * 2
> print(double(5))  # 10
> ```

<details><summary>Answer</summary>

It's an anti-pattern. PEP 8 says: don't assign a lambda to a variable. If you're naming it, just use `def`:

```python
# Instead of: double = lambda x: x * 2
# Write:
def double(x):
    return x * 2

print(double(5))  # 10 — same result, better practice
```

Lambda is for anonymous, inline use (inside `sorted()`, `map()`, etc.). If you're giving it a name, you've just made a worse `def` — no docstring, no name in tracebacks.

</details>

> **Q:** You need a function to validate email addresses with regex, logging, and error messages. Lambda or def?

<details><summary>Answer</summary>

**Use `def`.** This function needs a descriptive name (`validate_email`), multiple lines of logic, a docstring, and a clear name in tracebacks. Lambda can only handle one expression.

</details>

> **Q:** You're sorting a list of tuples `[(3, 'c'), (1, 'a'), (2, 'b')]` by the second element. Lambda or def?

<details><summary>Answer</summary>

**Lambda is perfect:** `sorted(data, key=lambda x: x[1])`. Tiny, one-expression, used inline, no name needed. This is exactly what lambda was designed for.

</details>

---

## Iterable vs Iterator — Know the Difference

Before we dive into `map()` and `filter()`, let's clear up two terms you'll see everywhere.

### Iterable = "I *can be* looped over"

An **iterable** is any object you can put after `in` in a `for` loop:

```python
for x in [1, 2, 3]:       # list ✓   → loops over elements
for x in (1, 2, 3):       # tuple ✓  → loops over elements
for ch in "hello":         # string ✓ → loops over each character

# Yes, dict and set are iterable too!
d = {"name": "Vipul", "psp": 85}
for k in d:                # dict ✓   → loops over KEYS ("name", "psp")
for k, v in d.items():     # dict.items() → loops over (key, value) pairs

s = {10, 20, 30}
for x in s:                # set ✓    → loops over elements (unordered!)

for n in range(5):         # range ✓  → loops over 0, 1, 2, 3, 4
```

> **Q:** Which of these can you **NOT** loop over with `for x in ...`? — `[1, 2, 3]`, `"hello"`, `42`, `range(10)`

<details><summary>Answer</summary>

**`42` is not iterable.** `for x in 42` raises `TypeError: 'int' object is not iterable`.

Things that are **NOT** iterable (you cannot loop over them):

```python
for x in 42:         # ✗ int — single value, not a collection
for x in 3.14:       # ✗ float — same reason
for x in True:       # ✗ bool — True/False are single values
for x in None:       # ✗ NoneType — "nothing" can't be looped
for x in len:        # ✗ function — callable, not iterable

# All raise: TypeError: '...' object is not iterable
# Rule of thumb: if it's a SINGLE value (not a collection), you can't loop over it.
```

</details>

### Iterator = "I *am* looping — and I remember where I am"

An **iterator** produces values **one at a time** using `next()`:

```python
nums = [10, 20, 30]       # iterable (the book)
it = iter(nums)            # iterator (the bookmark)

print(next(it))            # 10
print(next(it))            # 20
print(next(it))            # 30
print(next(it))            # StopIteration error!
```

A `for` loop does exactly this behind the scenes: calls `iter()` to get an iterator, then `next()` until `StopIteration`.

### Why does this matter?

`map()`, `filter()`, and `range()` return **iterators**, not lists:

```python
result = map(lambda x: x * 2, range(10_000_000))
# Nothing computed yet! It's lazy.

print(next(result))  # 0 — computes just this one
print(next(result))  # 2 — just this one

# list(result) would compute ALL 10M values — careful!
```

**Iterators save memory** because they don't store everything upfront. When you see `map()` returning a "map object" — now you know why you need `list()` to see the values.

---

> **A bit of history:** `map()`, `filter()`, and `lambda` were added in **Python 1.0 (1994)**, borrowed from Lisp. List comprehensions came later in **Python 2.0 (2000)**, inspired by Haskell. [Guido van Rossum](https://gvanrossum.github.io/) actually wanted to *remove* `map()`, `filter()`, `reduce()`, and `lambda` from Python 3 — he argued comprehensions made them redundant. The community pushed back. `reduce()` got demoted to `functools`, but the rest stayed. **Bottom line:** comprehensions are the Pythonic default, but `map()`/`filter()` earn their place when you already have a named function.

---

## map() — Transform Every Element

**Syntax:** `map(function, iterable)`
- **Takes:** a function and one (or more) iterables
- **Returns:** an **iterator** (lazy) — not a list! Wrap in `list()` to see all values
- **What it does:** applies the function to each element, one at a time

```
Input:  [100, 250, 50, 400]
         ↓     ↓    ↓    ↓      × 0.9 (apply 10% discount)
Output: [90,  225,  45, 360]
```

### Three Ways to Transform

```python
prices = [100, 250, 50, 400]

# Loop
result = []
for p in prices:
    result.append(p * 0.9)

# List comprehension
result = [p * 0.9 for p in prices]

# map
result = list(map(lambda p: p * 0.9, prices))
```

All three produce the same output. Comprehension is usually the most Pythonic.

> **What is a list comprehension?** It's Python's shortcut for "build a new list by transforming each item": `[expression for item in iterable]`. It reads like English: *"give me p * 0.85 for each p in prices"*. Comprehensions are more **Pythonic** (idiomatic Python) than `map()`.

### map Is Lazy

```python
result = map(lambda x: x ** 2, [1, 2, 3])
print(result)        # <map object at 0x...> — NOT a list!
print(list(result))  # [1, 4, 9] — computed when you iterate
```

This saves memory for large datasets — values are computed one at a time.

> **When to use map vs comprehension:** Use `map()` when you already HAVE a named function — `map(str.upper, words)` is cleaner than `[str.upper(w) for w in words]`. Use a comprehension when you'd need a lambda — `[p * 0.9 for p in prices]` beats `list(map(lambda p: p * 0.9, prices))`. Rule of thumb: if you're writing `map(lambda ...`, switch to a comprehension.

---

## filter() — Keep Only What Matches

**Syntax:** `filter(function, iterable)`
- **Takes:** a function that returns `True`/`False` (a "predicate"), and an iterable
- **Returns:** an **iterator** (lazy) — just like `map()`, wrap in `list()` to see values
- **What it does:** keeps only elements where the function returns `True`

```
Input:  [1, -3, 5, -7, 10, -2]
         ✓   ✗   ✓   ✗   ✓   ✗     keep if > 0
Output: [1,  5,  10]
```

### Three Ways to Filter

```python
numbers = [1, -3, 5, -7, 10, -2]

# Loop
result = [n for n in numbers if n > 0]

# filter
result = list(filter(lambda n: n > 0, numbers))
```

### filter(None) — Remove Falsy Values

```python
messy = [0, 1, "", "hello", None, 42, False, "world"]
clean = list(filter(None, messy))
# [1, "hello", 42, "world"] — removes 0, "", None, False
```

### Real Example — Filter Students by PSP

```python
students = [
    {"name": "Vipul", "psp": 85},
    {"name": "Gobi", "psp": 45},
    {"name": "Kaarthik", "psp": 92},
    {"name": "Ajit", "psp": 38},
]

# Strong performers: PSP >= 70
strong = list(filter(lambda s: s["psp"] >= 70, students))
strong = [s for s in students if s["psp"] >= 70]
```

### Chaining map + filter (and why comprehensions are better)

```python
# FP style (hard to read):
names = list(map(lambda s: s["name"], filter(lambda s: s["psp"] >= 70, students)))

# Comprehension (reads like English):
names = [s["name"] for s in students if s["psp"] >= 70]
```

---

## reduce() — Combine Into One Value

**Syntax:** `reduce(function, iterable[, initial])`
- **Takes:** a function with **two parameters** (accumulator, current_item), an iterable, optional initial value
- **Returns:** a **single value** — the final accumulated result
- **What it does:** applies the function cumulatively — first two items, then result + next, and so on
- **Import:** `from functools import reduce` — NOT a built-in

```python
from functools import reduce

# reduce(func, [a, b, c, d])
#   Step 1: result = func(a, b)
#   Step 2: result = func(result, c)
#   Step 3: result = func(result, d)
```

### Visual

```
reduce(+, [1, 2, 3, 4, 5])
  1 + 2 = 3
      3 + 3 = 6
          6 + 4 = 10
              10 + 5 = 15  → final result
```

### Examples

```python
# Sum
reduce(lambda acc, x: acc + x, [1, 2, 3, 4, 5])  # 15

# Product
reduce(lambda acc, x: acc * x, [1, 2, 3, 4, 5])  # 120

# Flatten
reduce(lambda acc, lst: acc + lst, [[1,2], [3,4], [5,6]])  # [1,2,3,4,5,6]
```

> **Note:** `reduce` is in `functools`, not built-in. Python prefers `sum()`, `max()`, `''.join()` for common cases. Use `reduce` when no built-in exists for your fold operation.

---

## Comprehensions vs FP — The Python Way

| Task | FP Style | Pythonic Style |
|---|---|---|
| Transform | `list(map(func, items))` | `[func(x) for x in items]` |
| Filter | `list(filter(func, items))` | `[x for x in items if cond]` |
| Both | `map(f, filter(g, items))` | `[f(x) for x in items if g(x)]` |
| Dict | — | `{k: v for k, v in items}` |
| Set | — | `{x for x in items}` |
| Lazy/Large | `map(func, items)` | `(func(x) for x in items)` generator |

> **Pythonic = comprehensions for 90% of cases.** Use map/filter only when you already have a named function.

---

## Closures — Functions That Remember

### The Idea

```python
def make_greeter(greeting):
    def greeter(name):
        return f"{greeting}, {name}!"   # uses 'greeting' from outer scope
    return greeter

hello = make_greeter("Hello")
namaste = make_greeter("Namaste")

hello("Vipul")    # "Hello, Vipul!"
namaste("Kaarthik")    # "Namaste, Kaarthik!"
```

`make_greeter("Hello")` has finished running. But `hello()` still remembers `greeting = "Hello"`. That's a closure: the inner function **closes over** the outer variable.

### Practical: Counter with Private State

```python
def make_counter(start=0):
    count = [start]
    def increment():
        count[0] += 1
        return count[0]
    return increment

counter_a = make_counter()
counter_a()  # 1
counter_a()  # 2
counter_a()  # 3
```

Each counter has its own `count`. They don't interfere.

### The Classic Gotcha: Lambda in a Loop

```python
functions = []
for i in range(5):
    functions.append(lambda: i)

[f() for f in functions]  # [4, 4, 4, 4, 4] — NOT [0, 1, 2, 3, 4]!
```

**Why?** All 5 lambdas share the SAME variable `i`. After the loop, `i = 4`. The lambda captures the **variable**, not the **value**.

**Fix:** Default argument captures the value at creation time:
```python
functions = [lambda i=i: i for i in range(5)]
[f() for f in functions]  # [0, 1, 2, 3, 4] ✓
```

---

## Decorators Preview — Closures in Disguise

A decorator is a function that takes a function and returns a new (wrapped) function.

```python
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time() - start:.4f}s")
        return result
    return wrapper

@timer
def calculate(n):
    return sum(x**2 for x in range(n))

calculate(10000)  # prints: "calculate took 0.0023s"
```

`@timer` is just syntactic sugar for `calculate = timer(calculate)`. It's a closure: `wrapper()` remembers `func` (the original `calculate`).

> **Real decorators you'll use:** `@cache`, `@login_required`, `@app.route`, `@retry`, `@validate`, `@property`

---

## FP vs OOP — When to Use Which

| | Functional Style | OOP Style |
|---|---|---|
| **Use for** | Transforming data | Managing state |
| **Tools** | lambda, map, filter, comprehensions | Classes, methods, inheritance |
| **State** | Stateless (no side effects) | Stateful (objects change over time) |
| **Examples** | Data pipelines, one-off transforms | User accounts, orders, game objects |

> **Pythonic = mix both.** Classes for structure, comprehensions for data. `sorted(users, key=lambda u: u.age)` — FP inside OOP. Django: OOP models + FP querysets.

### Concrete Examples — When Each Style Wins

**1. Extract student names (Comprehension wins):**
```python
students = [{"name": "Vipul", "psp": 85}, {"name": "Kaarthik", "psp": 92}, {"name": "Ajit", "psp": 38}]

# Comprehension — clean and obvious:
names = [s["name"] for s in students if s["psp"] >= 70]
# ['Vipul', 'Kaarthik']

# OOP — overkill for a one-liner:
class StudentFilter:
    def __init__(self, students): self.students = students
    def get_strong_names(self, threshold=70):
        return [s["name"] for s in self.students if s["psp"] >= threshold]
# A whole class just to filter a list?
```

**2. Track order lifecycle (OOP wins):**
```python
# OOP — natural fit for stateful objects:
class Order:
    def __init__(self, items):
        self.items = items
        self.status = "pending"
    def confirm(self):
        self.status = "confirmed"
    def ship(self):
        self.status = "shipped"

order = Order(["Pizza", "Pasta"])
order.confirm()
order.ship()
# State transitions are clear and encapsulated

# FP — awkward for state:
# You'd need to pass state around, return new dicts, track history... messy.
```

**3. Sales data pipeline (Comprehension wins):**
```python
sales = [
    {"item": "Pizza", "amount": 500, "paid": True},
    {"item": "Burger", "amount": 300, "paid": False},
    {"item": "Pasta", "amount": 450, "paid": True},
]

# Comprehension — one clean pipeline:
total_paid = sum(s["amount"] for s in sales if s["paid"])
# 950

# OOP — unnecessary ceremony:
class SalesReport:
    def __init__(self, sales): self.sales = sales
    def total_paid(self):
        return sum(s["amount"] for s in self.sales if s["paid"])
# Still uses a comprehension inside!
```

**4. Django-style mix (Both win):**
```python
# OOP for the model:
class Student:
    def __init__(self, name, psp):
        self.name = name
        self.psp = psp

students = [Student("Vipul", 85), Student("Kaarthik", 92), Student("Ajit", 38)]

# FP for the query:
top_students = sorted(
    [s for s in students if s.psp >= 70],
    key=lambda s: s.psp,
    reverse=True
)
# OOP defines structure, FP transforms data — best of both worlds
```

---

## Comprehensions — The Full Picture

We've seen comprehensions beat map/filter all class. Here's the full syntax, from basic to advanced.

### Syntax breakdown

```
[ expression   for item in iterable   if condition ]
  ^^^^^^^^^^   ^^^^^^^^^^^^^^^^^^^^   ^^^^^^^^^^^^
  what to       where to get data     optional filter
  produce
```

Read it like English: *"give me **expression** for each **item** in **iterable** if **condition**"*

### 1. Basic — Transform every element

```python
[n ** 2 for n in [1, 2, 3, 4, 5]]        # [1, 4, 9, 16, 25]
[name.upper() for name in ["vipul", "kaarthik"]]  # ['VIPUL', 'KAARTHIK']
[p * 1.18 for p in [100, 250, 500]]       # [118.0, 295.0, 590.0]
```

### 2. With filter — Keep only matching elements

```python
[n for n in range(1, 11) if n % 2 == 0]   # [2, 4, 6, 8, 10]
[s["name"] for s in students if s["psp"] >= 70]  # ['Vipul', 'Kaarthik']
```

### 3. With ternary — Transform differently based on condition

> **Important:** `if` at the END = filter (drops items). `if/else` in the EXPRESSION = ternary (keeps all items).

```python
# Filter (drops negatives):
[x for x in nums if x > 0]           # fewer items

# Ternary (replaces negatives with 0):
[x if x > 0 else 0 for x in nums]    # same count, different values

# Pass/fail labels:
[f"{s['name']}: Pass" if s["psp"] >= 70 else f"{s['name']}: Fail" for s in students]
```

### 4. Nested loops — Multiple `for` clauses

```python
# All combinations
colors = ["red", "blue"]
sizes = ["S", "M", "L"]
[f"{c}-{s}" for c in colors for s in sizes]
# ['red-S', 'red-M', 'red-L', 'blue-S', 'blue-M', 'blue-L']

# Flatten nested lists
nested = [[1, 2], [3, 4], [5, 6]]
[item for sublist in nested for item in sublist]  # [1, 2, 3, 4, 5, 6]
```

### 5. Dict & Set comprehensions

```python
# Dict: {key: value for item in iterable}
{s["name"]: s["psp"] for s in students}
# {'Vipul': 85, 'Kaarthik': 92, 'Ajit': 78}

# Set: {expression for item in iterable}
{name[0] for name in ["Vipul", "Kaarthik", "Ajit", "Kavya"]}
# {'V', 'K', 'A'} — unique values only
```

### 6. Generator expression — Lazy comprehension

```python
# List comprehension — all in memory:
total = sum([x ** 2 for x in range(1_000_000)])

# Generator — one at a time, almost zero memory:
total = sum(x ** 2 for x in range(1_000_000))
#           ^ no brackets = generator
```

### When NOT to use comprehensions

- More than 2 conditions or nested loops — use a regular `for` loop
- Side effects (printing, writing to file) — use a `for` loop
- Complex multi-step logic — break into readable steps

---

## map vs filter vs reduce — At a Glance

| | map() | filter() | reduce() |
|---|---|---|---|
| **Purpose** | Transform every element | Keep elements that pass a test | Combine all into one value |
| **Input** | function + iterable | predicate (True/False) + iterable | function(acc, item) + iterable + optional initial |
| **Output** | Iterator (same count, transformed) | Iterator (fewer or equal, unchanged) | Single value (not an iterator) |
| **Lazy?** | Yes — needs `list()` | Yes — needs `list()` | No — computes immediately |
| **Built-in?** | Yes | Yes | No — `from functools import reduce` |
| **Example** | `map(lambda x: x*2, [1,2,3])` → `[2,4,6]` | `filter(lambda x: x>0, [-1,2,-3])` → `[2]` | `reduce(lambda a,x: a+x, [1,2,3])` → `6` |
| **Pythonic alt** | `[x*2 for x in nums]` | `[x for x in nums if x>0]` | `sum()`, `max()`, `min()`, `''.join()` |
| **Think of as** | Conveyor belt | Gatekeeper | Snowball |

---

## Exercises

### Exercise 1: map() — Add 18% GST to all prices

```python
prices = [1200, 450, 3200, 890, 150]
# Use map() to multiply each price by 1.18
with_gst = ???
```

<details><summary>Solution</summary>

```python
with_gst = list(map(lambda p: round(p * 1.18, 2), prices))
# Comprehension: [round(p * 1.18, 2) for p in prices]
```

</details>

### Exercise 2: filter() — Students with attendance >= 85%

```python
students = [
    {"name": "Vipul", "psp": 85, "attendance": 92},
    {"name": "Kaarthik", "psp": 92, "attendance": 88},
    {"name": "Ajit", "psp": 78, "attendance": 95},
    {"name": "Gobi", "psp": 45, "attendance": 60},
    {"name": "Sneha", "psp": 91, "attendance": 85},
]
# Use filter() to keep only students with attendance >= 85
regular = ???
```

<details><summary>Solution</summary>

```python
regular = list(filter(lambda s: s["attendance"] >= 85, students))
# Comprehension: [s for s in students if s["attendance"] >= 85]
```

</details>

### Exercise 3: reduce() — Total PSP of all students

```python
from functools import reduce
# Use reduce() to sum up all PSP values
total_psp = ???
```

<details><summary>Solution</summary>

```python
total_psp = reduce(lambda acc, s: acc + s["psp"], students, 0)
# Pythonic: sum(s["psp"] for s in students)
```

</details>

### Exercise 4: filter + map — Get NAMES of students with PSP >= 70

```python
# Step 1: filter where PSP >= 70
# Step 2: map to extract just the name
strong_names = ???
```

<details><summary>Solution</summary>

```python
# FP way:
strong_names = list(map(lambda s: s["name"], filter(lambda s: s["psp"] >= 70, students)))

# Comprehension (much more readable!):
strong_names = [s["name"] for s in students if s["psp"] >= 70]
```

</details>

### Exercise 5: map + reduce — Total revenue after 18% GST

```python
prices = [1200, 450, 3200, 890, 150]
# Step 1: map each price to price * 1.18
# Step 2: reduce to get the total
total_revenue = ???
```

<details><summary>Solution</summary>

```python
# FP way:
total_revenue = reduce(lambda acc, p: acc + p, map(lambda p: p * 1.18, prices))

# Pythonic: sum(p * 1.18 for p in prices)
```

</details>

### Exercise 6: filter + map + reduce — Total PSP of students with attendance >= 80%

```python
# Combine all three!
total_psp_regular = ???
```

<details><summary>Solution</summary>

```python
# FP way (hard to read!):
total_psp_regular = reduce(
    lambda acc, psp: acc + psp,
    map(lambda s: s["psp"], filter(lambda s: s["attendance"] >= 80, students)),
    0
)

# Pythonic (much cleaner):
total_psp_regular = sum(s["psp"] for s in students if s["attendance"] >= 80)
```

Every time we chain map/filter/reduce, the comprehension version is shorter and clearer. But knowing map/filter/reduce helps you read FP code and understand what comprehensions do under the hood.

</details>

### Exercise 7: sorted + lambda — Rank students by PSP (highest first)

```python
ranked = ???
# Print: #1 Kaarthik: PSP=92, #2 Sneha: PSP=91, ...
```

<details><summary>Solution</summary>

```python
ranked = sorted(students, key=lambda s: s["psp"], reverse=True)
for i, s in enumerate(ranked, 1):
    print(f"#{i} {s['name']}: PSP={s['psp']}")
```

</details>

---

## Code Files

| File | What It Demonstrates |
|---|---|
| `01_functions_are_objects.py` | Functions stored, passed, returned — the foundation |
| `02_lambda_basics.py` | Lambda syntax, one expression, no name |
| `03_lambda_real_uses.py` | sorted(key=), max(key=), dict of operations |
| `04_map.py` | map() with lambda, named functions, lazy evaluation |
| `05_filter.py` | filter(), filter(None), chaining with map |
| `06_reduce.py` | reduce() step by step, sum/product/flatten |
| `07_comprehensions_vs_fp.py` | When comprehension wins vs map/filter |
| `08_closures.py` | make_greeter, make_counter, make_multiplier |
| `09_closure_gotcha.py` | Lambda in loop bug + fix |
| `10_decorators_preview.py` | @timer, @log_calls — closures in disguise |
| `11_fp_vs_oop.py` | Same problem three ways: OOP, FP, Pythonic |
| `12_exercises.py` | Practice exercises: map, filter, reduce — isolated and combined |

---

## Key Takeaways

1. **Functions are objects** — store, pass, return them. This enables everything else.
2. **Lambda = anonymous one-liner** — use inline (`sorted(key=lambda ...)`), not assigned to variables
3. **map/filter/reduce** — transform, keep, combine. But comprehensions are more Pythonic for most cases.
4. **Closures = inner function + remembered outer variable** — the basis of decorators, factories, callbacks
5. **Decorators = closures that wrap functions** — `@timer` is just `f = timer(f)`
6. **Pythonic = mix FP + OOP** — classes for state, comprehensions for data transforms

**Next class:** Python Advanced-4 — Exception Handling

---

## Resources

- [Python docs — Lambda expressions](https://docs.python.org/3/reference/expressions.html#lambda)
- [Python docs — map()](https://docs.python.org/3/library/functions.html#map)
- [Python docs — filter()](https://docs.python.org/3/library/functions.html#filter)
- [Python docs — functools.reduce()](https://docs.python.org/3/library/functools.html#functools.reduce)
- [Python docs — List comprehensions](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions)
- [Real Python — Closures](https://realpython.com/python-closures/)
- [Real Python — Decorators](https://realpython.com/primer-on-python-decorators/)
