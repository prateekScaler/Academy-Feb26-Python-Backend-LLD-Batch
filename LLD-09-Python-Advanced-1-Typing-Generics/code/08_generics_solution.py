"""Generics — ONE class/function, type-safe for ANY type."""
from typing import TypeVar, Generic


# --- TypeVar: a placeholder for "some type" ---
T = TypeVar("T")  # T will be replaced by the actual type at usage


# --- Generic class ---
class Box(Generic[T]):
    def __init__(self, item: T):
        self.item = item

    def get(self) -> T:
        return self.item

    def replace(self, new_item: T) -> None:
        self.item = new_item


# Now the type flows through!
int_box = Box[int](42)       # T = int for this instance
str_box = Box[str]("hello")  # T = str for this instance

# IDE knows: int_box.get() returns int
val1: int = int_box.get()
print(f"Box[int](42).get() = {val1}")

# IDE knows: str_box.get() returns str
val2: str = str_box.get()
print(f"Box[str]('hello').get() = {val2}")
print(f"  val2.upper() = '{val2.upper()}'  ← IDE autocompletes string methods!")

# mypy catches this:
# int_box.replace("oops")  # error: Argument 1 has incompatible type "str"; expected "int"
print("\n  int_box.replace('oops') → mypy error! Type safety preserved.")


# --- Generic function ---
def first(items: list[T]) -> T:
    """Return first element — return type matches element type."""
    return items[0]


# IDE knows: first([1,2,3]) returns int
num = first([1, 2, 3])
print(f"\nfirst([1, 2, 3]) = {num}  (IDE knows it's int)")

# IDE knows: first(["a","b"]) returns str
word = first(["a", "b", "c"])
print(f"first(['a', 'b', 'c']) = '{word}'  (IDE knows it's str)")


# --- Multiple TypeVars ---
K = TypeVar("K")
V = TypeVar("V")


def get_or_default(d: dict[K, V], key: K, default: V) -> V:
    """Type-safe dict.get() — key and default match the dict's types."""
    return d.get(key, default)


scores: dict[str, int] = {"Alice": 95, "Bob": 87}
result = get_or_default(scores, "Charlie", 0)
print(f"\nget_or_default(scores, 'Charlie', 0) = {result}")
print("  Key must be str, default must be int — enforced by generics.")
