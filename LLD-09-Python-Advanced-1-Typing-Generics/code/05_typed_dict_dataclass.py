"""TypedDict and dataclasses — structured data with types."""
from typing import TypedDict
from dataclasses import dataclass


# --- Problem: plain dicts have no structure ---
# What keys does this dict have? What types are the values?
user_bad = {"name": "Alice", "age": 25, "email": "alice@example.com"}
# user_bad["namee"]  # typo — no error until runtime!


# --- Solution 1: TypedDict (for dict-like data, e.g., API responses) ---
class UserDict(TypedDict):
    name: str
    age: int
    email: str


def create_user_dict(name: str, age: int, email: str) -> UserDict:
    return {"name": name, "age": age, "email": email}


user1 = create_user_dict("Alice", 25, "alice@example.com")
print(f"TypedDict user: {user1}")
# mypy catches: user1["namee"]  → error: TypedDict has no key 'namee'


# --- Solution 2: dataclass (preferred for most cases) ---
@dataclass
class User:
    name: str
    age: int
    email: str

    def is_adult(self) -> bool:
        return self.age >= 18


user2 = User(name="Bob", age=30, email="bob@example.com")
print(f"\ndataclass user: {user2}")
print(f"  user2.name = '{user2.name}'")
print(f"  user2.is_adult() = {user2.is_adult()}")
# user2.namee  → IDE and mypy catch this immediately


# --- dataclass with defaults and frozen (immutable) ---
@dataclass(frozen=True)
class Config:
    host: str = "localhost"
    port: int = 8000
    debug: bool = False


config = Config(host="api.example.com", port=443)
print(f"\nfrozen dataclass: {config}")
try:
    config.port = 8080  # type: ignore
except Exception as e:
    print(f"  Can't mutate frozen: {e}")


# --- When to use which ---
print("\n--- When to use which ---")
print("  TypedDict → when you're working with JSON/dict data (API responses)")
print("  dataclass → when you're defining your own data structures")
print("  Plain class → when you need complex behavior beyond data")
print("  Pydantic BaseModel → when you need validation (FastAPI, config)")
