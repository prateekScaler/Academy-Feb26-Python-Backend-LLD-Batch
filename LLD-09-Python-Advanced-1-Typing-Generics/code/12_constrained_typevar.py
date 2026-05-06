"""Constrained and Bounded TypeVars — limiting what T can be."""
from typing import TypeVar


# --- Constrained TypeVar: T can ONLY be one of these specific types ---
Number = TypeVar("Number", int, float)


def double(x: Number) -> Number:
    """Only accepts int or float — not str, not bool, not list."""
    return x * 2


print("Constrained TypeVar (int | float only):\n")
print(f"  double(5) = {double(5)}")
print(f"  double(3.14) = {double(3.14)}")
# double("hello")  # mypy error: Value of type variable "Number" cannot be "str"


# --- Bounded TypeVar: T must be a subclass of something ---
from typing import Protocol


class Comparable(Protocol):
    def __lt__(self, other: "Comparable") -> bool: ...


CT = TypeVar("CT", bound=Comparable)


def find_min(items: list[CT]) -> CT:
    """Works with any type that supports < comparison."""
    result = items[0]
    for item in items[1:]:
        if item < result:
            result = item
    return result


print("\nBounded TypeVar (must support < comparison):\n")
print(f"  find_min([5, 2, 8, 1, 9]) = {find_min([5, 2, 8, 1, 9])}")
print(f"  find_min(['banana', 'apple', 'cherry']) = '{find_min(['banana', 'apple', 'cherry'])}'")


# --- TypeVar with bound= (class hierarchy) ---
class Animal:
    def __init__(self, name: str):
        self.name = name

    def speak(self) -> str:
        return f"{self.name} makes a sound"


class Dog(Animal):
    def speak(self) -> str:
        return f"{self.name}: Woof!"


class Cat(Animal):
    def speak(self) -> str:
        return f"{self.name}: Meow!"


A = TypeVar("A", bound=Animal)


def loudest(animals: list[A]) -> A:
    """T must be Animal or subclass. Return type matches input type."""
    return max(animals, key=lambda a: len(a.speak()))


print("\nBounded TypeVar (bound=Animal):\n")
dogs: list[Dog] = [Dog("Rex"), Dog("Buddy")]
result = loudest(dogs)  # IDE knows: result is Dog (not just Animal!)
print(f"  loudest(dogs) = {result.speak()}")

cats: list[Cat] = [Cat("Whiskers"), Cat("Luna")]
result2 = loudest(cats)  # IDE knows: result2 is Cat
print(f"  loudest(cats) = {result2.speak()}")

print("\n--- Summary ---")
print("  TypeVar('T', int, float)    → T can ONLY be int or float")
print("  TypeVar('T', bound=Animal)  → T can be Animal or ANY subclass")
print("  Constrained = pick from a fixed list")
print("  Bounded = anything in a hierarchy")
