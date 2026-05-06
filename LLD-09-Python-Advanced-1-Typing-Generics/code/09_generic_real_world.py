"""Real-world Generic patterns — Repository, Result, Stack."""
from typing import TypeVar, Generic
from dataclasses import dataclass


T = TypeVar("T")


# --- Pattern 1: Generic Repository (Database layer) ---
@dataclass
class User:
    id: int
    name: str
    email: str


@dataclass
class Order:
    id: int
    amount: float
    user_id: int


class Repository(Generic[T]):
    """Type-safe CRUD — works for User, Order, Product, anything."""

    def __init__(self) -> None:
        self._items: dict[int, T] = {}

    def add(self, id: int, item: T) -> None:
        self._items[id] = item

    def get(self, id: int) -> T | None:
        return self._items.get(id)

    def get_all(self) -> list[T]:
        return list(self._items.values())

    def delete(self, id: int) -> bool:
        return self._items.pop(id, None) is not None


# Usage: ONE class, type-safe for both
user_repo = Repository[User]()
user_repo.add(1, User(1, "Alice", "alice@example.com"))
user_repo.add(2, User(2, "Bob", "bob@example.com"))

order_repo = Repository[Order]()
order_repo.add(1, Order(1, 999.99, 1))

# IDE knows: user_repo.get(1) returns User | None
user = user_repo.get(1)
if user:
    print(f"User repo: {user.name} ({user.email})")

# IDE knows: order_repo.get(1) returns Order | None
order = order_repo.get(1)
if order:
    print(f"Order repo: ₹{order.amount}")

# This would be a mypy error:
# user_repo.add(3, Order(3, 50.0, 1))  # error: expected User, got Order


# --- Pattern 2: Result type (Success or Error) ---
E = TypeVar("E")


@dataclass
class Success(Generic[T]):
    value: T


@dataclass
class Failure(Generic[E]):
    error: E


Result = Success[T] | Failure[E]  # type: ignore


def divide(a: float, b: float) -> Success[float] | Failure[str]:
    if b == 0:
        return Failure("Division by zero")
    return Success(a / b)


print("\nResult pattern:")
r1 = divide(10, 3)
r2 = divide(10, 0)
print(f"  divide(10, 3) = {r1}")
print(f"  divide(10, 0) = {r2}")


# --- Pattern 3: Generic Stack ---
class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items.pop()

    def peek(self) -> T:
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items[-1]

    @property
    def size(self) -> int:
        return len(self._items)


print("\nGeneric Stack:")
int_stack = Stack[int]()
int_stack.push(10)
int_stack.push(20)
int_stack.push(30)
print(f"  Stack[int]: pushed 10, 20, 30")
print(f"  pop() = {int_stack.pop()}")
print(f"  peek() = {int_stack.peek()}")

str_stack = Stack[str]()
str_stack.push("hello")
str_stack.push("world")
# str_stack.push(42)  # mypy error: expected str, got int
print(f"\n  Stack[str]: pushed 'hello', 'world'")
print(f"  pop() = '{str_stack.pop()}'")
