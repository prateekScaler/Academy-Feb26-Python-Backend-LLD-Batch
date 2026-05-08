"""namedtuple — tuples with names. Immutable, lightweight, readable."""
from collections import namedtuple
from typing import NamedTuple


# --- Problem: plain tuples are unreadable ---
# What is point[0]? x? latitude? id?
point = (28.6139, 77.2090)
print(f"Plain tuple: {point}")
print(f"  point[0] = {point[0]}  ← what is this? x? lat? who knows!")


# --- Solution: namedtuple ---
Point = namedtuple("Point", ["x", "y"])
p = Point(28.6139, 77.2090)

print(f"\nNamedTuple: {p}")
print(f"  p.x = {p.x}")      # readable!
print(f"  p.y = {p.y}")
print(f"  p[0] = {p[0]}")    # still works as tuple
print(f"  immutable: can't do p.x = 10")


# --- Typed NamedTuple (preferred, modern syntax) ---
class User(NamedTuple):
    name: str
    age: int
    email: str

user = User("Alice", 25, "alice@example.com")
print(f"\nTyped NamedTuple: {user}")
print(f"  user.name = '{user.name}'")
print(f"  user.age = {user.age}")

# Immutable — can't change
try:
    user.age = 26  # type: ignore
except AttributeError as e:
    print(f"  Can't mutate: {e}")


# --- _replace: create new with some fields changed ---
older_user = user._replace(age=26)
print(f"\n  _replace(age=26): {older_user}")
print(f"  Original unchanged: {user}")


# --- _asdict: convert to dict ---
print(f"  _asdict(): {user._asdict()}")


# --- Unpacking ---
name, age, email = user
print(f"\n  Unpacked: name={name}, age={age}")


# --- Real-world uses ---
# API responses, DB rows, config, function return values
class HTTPResponse(NamedTuple):
    status: int
    body: str
    headers: dict

response = HTTPResponse(200, '{"ok": true}', {"Content-Type": "application/json"})
print(f"\nHTTPResponse: status={response.status}, body={response.body}")


# --- namedtuple vs dataclass ---
print("\n--- namedtuple vs dataclass ---")
print("  namedtuple: immutable, lightweight, is a tuple, unpackable")
print("  dataclass:  mutable by default, has methods, more flexible")
print("  Use namedtuple for: small immutable records, function returns")
print("  Use dataclass for:  larger structures, need methods, need mutability")
