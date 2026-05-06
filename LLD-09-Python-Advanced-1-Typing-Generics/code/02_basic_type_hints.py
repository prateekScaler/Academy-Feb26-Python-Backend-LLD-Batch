"""Basic type hints — telling Python (and your IDE) what you expect."""


# --- Without types: What does this function accept? Return? ---
def greet(name):
    return f"Hello, {name}!"


# --- With types: Crystal clear ---
def greet_typed(name: str) -> str:
    return f"Hello, {name}!"


# --- Common basic types ---
def add(a: int, b: int) -> int:
    return a + b


def is_adult(age: int) -> bool:
    return age >= 18


def get_average(numbers: list[float]) -> float:
    return sum(numbers) / len(numbers)


# --- Python does NOT enforce types at runtime! ---
# Types are HINTS, not constraints.
result = add("hello", " world")  # Python runs this fine!
print(f"add('hello', ' world') = '{result}'")
print("  Python doesn't care. It ran anyway.")
print("  But mypy would catch this: 'error: Argument 1 has incompatible type \"str\"'")
print()

# --- So why bother? ---
# 1. IDE autocomplete — your editor knows what methods are available
# 2. mypy catches bugs BEFORE runtime — like a compiler for Python
# 3. Documentation — you don't need to read the implementation
# 4. Refactoring safety — change a type, mypy shows all broken callers
print("Benefits of type hints:")
print("  1. IDE autocomplete (try typing 'name.' in VS Code)")
print("  2. mypy catches type errors before you run code")
print("  3. Self-documenting — no need to guess what a function expects")
print("  4. Safe refactoring — change a type, find all breakages instantly")
