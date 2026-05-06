"""mypy demo — run this with: mypy 11_mypy_demo.py

This file has INTENTIONAL type errors that mypy will catch.
Python will run it fine — but mypy will show the bugs."""


def add_numbers(a: int, b: int) -> int:
    return a + b


def get_name(user_id: int) -> str | None:
    users = {1: "Alice", 2: "Bob"}
    return users.get(user_id)


def process_items(items: list[str]) -> int:
    return len(items)


# --- Bug 1: Wrong argument type ---
result1 = add_numbers(10, "20")  # mypy: Argument 2 has incompatible type "str"
print(f"Bug 1: add_numbers(10, '20') = {result1}")

# --- Bug 2: Not handling None ---
name = get_name(999)
print(f"Bug 2: name.upper() = {name.upper()}")  # mypy: Item "None" has no attribute "upper"

# --- Bug 3: Wrong container element type ---
items: list[str] = ["apple", "banana", 42]  # mypy: List item 2 has incompatible type "int"
count = process_items(items)
print(f"Bug 3: process_items with mixed list = {count}")

# --- Bug 4: Incompatible return type ---
def get_age() -> int:
    return "twenty-five"  # mypy: Incompatible return value type (got "str", expected "int")


# --- Bug 5: Missing attribute ---
class Dog:
    def __init__(self, name: str):
        self.name = name

    def bark(self) -> str:
        return f"{self.name}: Woof!"


dog = Dog("Rex")
print(dog.bark())
print(dog.speak())  # mypy: "Dog" has no attribute "speak"


print("\n" + "=" * 60)
print("Run: mypy 11_mypy_demo.py")
print("You'll see 5 errors — ALL caught without running the code!")
print("=" * 60)
print("\nTo install: pip install mypy")
print("To run:     mypy your_file.py")
print("Config:     create mypy.ini or pyproject.toml for project-wide settings")
