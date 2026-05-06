"""Type aliases — naming complex types for readability."""
from typing import TypeAlias, Callable
from dataclasses import dataclass


# --- Problem: complex types are hard to read ---
# What does this signature even mean?
# def process(data: dict[str, list[tuple[int, str, float]]]) -> list[dict[str, str | int]]: ...
# Unreadable!


# --- Solution: Type aliases ---
# Python 3.12+ syntax:
# type Coordinate = tuple[float, float]

# Python 3.10+ syntax (what we'll use):
Coordinate: TypeAlias = tuple[float, float]
StudentScores: TypeAlias = dict[str, list[int]]
Middleware: TypeAlias = Callable[[dict, dict], dict]
JSONValue: TypeAlias = str | int | float | bool | None | list["JSONValue"] | dict[str, "JSONValue"]


def distance(a: Coordinate, b: Coordinate) -> float:
    """Now the signature is readable!"""
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def top_student(scores: StudentScores) -> str:
    """Clear: we take a dict of student → list of scores."""
    return max(scores, key=lambda s: sum(scores[s]) / len(scores[s]))


print("Type aliases — readable complex types:\n")

delhi: Coordinate = (28.6139, 77.2090)
mumbai: Coordinate = (19.0760, 72.8777)
print(f"  distance(delhi, mumbai) = {distance(delhi, mumbai):.2f}")

scores: StudentScores = {"Alice": [95, 88, 92], "Bob": [87, 91, 85]}
print(f"  top_student(scores) = '{top_student(scores)}'")


# --- Real-world aliases you'll see in frameworks ---
print("\n--- Common patterns in real code ---")
print("  # Django/FastAPI")
print("  QueryParams = dict[str, str | list[str]]")
print("  Headers = dict[str, str]")
print("  # Event-driven")
print("  EventHandler = Callable[[str, dict], None]")
print("  Middleware = Callable[[Request, Response], Response]")
print("  # Data pipelines")
print("  Row = dict[str, str | int | float | None]")
print("  DataFrame = list[Row]")


# --- NewType: stricter than aliases ---
from typing import NewType

UserId = NewType("UserId", int)
OrderId = NewType("OrderId", int)


def get_user(user_id: UserId) -> str:
    return f"User-{user_id}"


# Both are int underneath, but mypy treats them differently:
uid = UserId(42)
oid = OrderId(99)

print(f"\nNewType:")
print(f"  get_user(UserId(42)) = '{get_user(uid)}'")
# get_user(oid)  # mypy error: expected UserId, got OrderId
# get_user(42)   # mypy error: expected UserId, got int
print("  get_user(OrderId(99)) → mypy error! Can't mix up IDs.")
print("  NewType prevents accidentally passing OrderId where UserId expected.")
