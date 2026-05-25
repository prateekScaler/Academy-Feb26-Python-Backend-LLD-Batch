"""
01 - Database Builder (the canonical implementation)
====================================================

The 4-step recipe:
  Step 1: Product class with trivial __init__
  Step 2: Inner Builder class with mutable state
  Step 3: Setters that return self
  Step 4: build() validates and constructs

Run me to see the happy path + two failure cases.
"""

from dataclasses import dataclass


@dataclass
class Database:
    host: str
    port: int
    username: str
    password: str

    def connect(self):
        print(f"connecting to {self.host}:{self.port} as {self.username}")

    @staticmethod
    def builder():
        """Entry point - no Database instance needed to start."""
        return Database.Builder()

    class Builder:
        def __init__(self):
            self._host = None
            self._port = None
            self._username = None
            self._password = None

        def set_host(self, host):
            self._host = host
            return self

        def set_port(self, port):
            self._port = port
            return self

        def set_username(self, username):
            self._username = username
            return self

        def set_password(self, password):
            self._password = password
            return self

        def build(self) -> "Database":
            self._validate()
            return Database(
                host=self._host,
                port=self._port,
                username=self._username,
                password=self._password,
            )

        def _validate(self):
            if not self._host:
                raise ValueError("host required")
            if not self._port:
                raise ValueError("port required")
            if not (1024 <= self._port <= 65535):
                raise ValueError("port out of range (1024-65535)")
            if not self._username:
                raise ValueError("username required")
            if not self._password:
                raise ValueError("password required")


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo_happy_path():
    print("--- Happy path ---")
    db = (Database.builder()
            .set_host("localhost")
            .set_port(5432)
            .set_username("admin")
            .set_password("secret")
            .build())
    db.connect()


def demo_invalid_value():
    print("\n--- Invalid value (port out of range) ---")
    try:
        (Database.builder()
            .set_host("localhost")
            .set_port(80)             # too low
            .set_username("admin")
            .set_password("secret")
            .build())
    except ValueError as e:
        print(f"ValueError: {e}")


def demo_missing_field():
    print("\n--- Missing field (no credentials) ---")
    try:
        (Database.builder()
            .set_host("localhost")
            .set_port(5432)
            .build())                  # forgot username + password
    except ValueError as e:
        print(f"ValueError: {e}")


if __name__ == "__main__":
    demo_happy_path()
    demo_invalid_value()
    demo_missing_field()
