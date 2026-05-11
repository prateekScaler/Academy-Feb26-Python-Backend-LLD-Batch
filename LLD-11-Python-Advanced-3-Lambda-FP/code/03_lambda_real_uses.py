"""Where lambda actually shines — sorting, callbacks, one-liners."""


# --- Use case 1: Custom sorting ---
students = [
    {"name": "Ajit", "age": 20, "gpa": 3.5},
    {"name": "Vipul", "age": 22, "gpa": 3.9},
    {"name": "Kaarthik", "age": 21, "gpa": 3.2},
]

# Sort by age
by_age = sorted(students, key=lambda s: s["age"])
print("Sorted by age:")
for s in by_age:
    print(f"  {s['name']}: {s['age']}")

# Sort by GPA (descending)
by_gpa = sorted(students, key=lambda s: s["gpa"], reverse=True)
print("\nSorted by GPA (highest first):")
for s in by_gpa:
    print(f"  {s['name']}: {s['gpa']}")

# Sort by name length
by_name_len = sorted(students, key=lambda s: len(s["name"]))
print("\nSorted by name length:")
for s in by_name_len:
    print(f"  {s['name']} ({len(s['name'])} chars)")


# --- Use case 2: max/min with key ---
oldest = max(students, key=lambda s: s["age"])
print(f"\nOldest: {oldest['name']} (age {oldest['age']})")

shortest_name = min(students, key=lambda s: len(s["name"]))
print(f"Shortest name: {shortest_name['name']}")


# --- Use case 3: Inline callback ---
def do_twice(func, value):
    return func(func(value))

result = do_twice(lambda x: x + 10, 5)
print(f"\ndo_twice(+10, 5) = {result}")  # 5 + 10 + 10 = 25


# --- Use case 4: Dictionary of operations ---
ops = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b if b != 0 else "div by zero",
}

print(f"\nCalculator:")
for symbol, func in ops.items():
    print(f"  10 {symbol} 3 = {func(10, 3)}")


# --- Anti-pattern: DON'T assign lambda to a variable ---
# BAD:  double = lambda x: x * 2
# GOOD: def double(x): return x * 2
# If it needs a name, use def. Lambda is for anonymous, inline use.
print("\n--- Rule of thumb ---")
print("  Lambda: use INLINE where a function is expected")
print("  def:    use when you need a name, docstring, or multiple lines")


# --- OOP equivalent of the dict approach ---
class Calculator:
    def add(self, a, b): return a + b
    def sub(self, a, b): return a - b
    def mul(self, a, b): return a * b

    def compute(self, op, a, b):
        if op == "+": return self.add(a, b)
        if op == "-": return self.sub(a, b)
        if op == "*": return self.mul(a, b)

calc = Calculator()
print(f"\nOOP calculator: 10 + 3 = {calc.compute('+', 10, 3)}")
# Works, but WAY more code for a simple lookup table
