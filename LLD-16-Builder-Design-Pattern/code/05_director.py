"""
05 - Director (named preset configurations)
===========================================

A Director sits ON TOP of a Builder and exposes one-liner factory
methods for commonly-used configurations. The caller writes:

    db = DatabaseDirector.local()

instead of repeating the same 5-line .set_*().build() chain in
every test / dev script.

Use a Director only when you have RECURRING presets - not speculation.
"""

import os
from dataclasses import dataclass


# Re-use the Database from file 01 - inlined here for self-containment
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
        return Database.Builder()

    class Builder:
        def __init__(self):
            self._host = self._port = self._username = self._password = None

        def set_host(self, host):         self._host = host;         return self
        def set_port(self, port):         self._port = port;         return self
        def set_username(self, username): self._username = username; return self
        def set_password(self, password): self._password = password; return self

        def build(self) -> "Database":
            return Database(self._host, self._port, self._username, self._password)


# ---------------------------------------------------------------------------
# The Director - presets on top of the Builder
# ---------------------------------------------------------------------------

class DatabaseDirector:
    """Each method is one named, validated configuration."""

    @staticmethod
    def local() -> Database:
        """Local development - no secrets, fixed creds."""
        return (Database.builder()
                .set_host("localhost")
                .set_port(5432)
                .set_username("dev")
                .set_password("dev")
                .build())

    @staticmethod
    def test() -> Database:
        """In-memory style settings for unit tests."""
        return (Database.builder()
                .set_host("localhost")
                .set_port(5433)            # different port - test DB
                .set_username("test")
                .set_password("test")
                .build())

    @staticmethod
    def production(host: str) -> Database:
        """Production - credentials from env vars, not in code."""
        return (Database.builder()
                .set_host(host)
                .set_port(5432)
                .set_username(os.environ.get("DB_USER", "postgres"))
                .set_password(os.environ.get("DB_PASS", ""))
                .build())


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo():
    print("--- Local DB (preset) ---")
    DatabaseDirector.local().connect()

    print("\n--- Test DB (preset) ---")
    DatabaseDirector.test().connect()

    print("\n--- Production DB (with override) ---")
    DatabaseDirector.production("db.example.com").connect()


if __name__ == "__main__":
    demo()
