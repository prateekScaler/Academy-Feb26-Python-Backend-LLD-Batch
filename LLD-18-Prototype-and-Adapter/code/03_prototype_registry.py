"""
LLD-18 · Prototype · Example 3 — Prototype Registry.

Run:  python3 03_prototype_registry.py

When you want to clone "by name" — "give me a fresh welcome email",
"give me the staging config", "spawn an enemy of type 'orc'" — store
your prototypes in a registry keyed by name. Callers ask the registry
for a clone; they never touch the original prototypes.

This is what IDE "new file from template", notification template systems,
and game engine spawning all look like under the hood.
"""

from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Self


# ---- Prototype interface ----
class Prototype(ABC):
    @abstractmethod
    def clone(self) -> Self: ...


# ---- Concrete prototypes — notification templates ----
@dataclass
class NotificationTemplate(Prototype):
    channel: str
    template: str
    retry_count: int = 3
    placeholders: dict[str, str] = field(default_factory=dict)
    recipient: str | None = None

    def clone(self) -> "NotificationTemplate":
        return copy.deepcopy(self)


# ---- The Registry ----
class PrototypeRegistry:
    def __init__(self) -> None:
        self._prototypes: dict[str, Prototype] = {}

    def register(self, name: str, proto: Prototype) -> None:
        if name in self._prototypes:
            raise ValueError(f"Already registered: {name}")
        self._prototypes[name] = proto

    def get(self, name: str) -> Prototype:
        if name not in self._prototypes:
            raise KeyError(f"No prototype named '{name}'")
        return self._prototypes[name].clone()

    def names(self) -> list[str]:
        return sorted(self._prototypes)


# ---- Demo ----
def main() -> None:
    registry = PrototypeRegistry()

    # One-time setup — register the templates
    registry.register(
        "welcome-email",
        NotificationTemplate(
            channel="email",
            template="Welcome to Scaler, {name}!",
            retry_count=3,
            placeholders={"name": ""},
        ),
    )
    registry.register(
        "payment-failed-sms",
        NotificationTemplate(
            channel="sms",
            template="Hi {name}, payment of ₹{amount} failed.",
            retry_count=5,
            placeholders={"name": "", "amount": ""},
        ),
    )
    registry.register(
        "weekly-digest-email",
        NotificationTemplate(
            channel="email",
            template="Your weekly digest: {summary}",
            retry_count=2,
            placeholders={"summary": ""},
        ),
    )

    print(f"Templates available: {registry.names()}\n")

    # --- Usage ---
    msg1 = registry.get("welcome-email")
    msg1.recipient = "riya@scaler.com"
    msg1.placeholders["name"] = "Riya"
    print("msg1:", msg1)

    msg2 = registry.get("welcome-email")
    msg2.recipient = "karan@scaler.com"
    msg2.placeholders["name"] = "Karan"
    print("msg2:", msg2)

    # Prove the originals are untouched and clones independent
    assert msg1.recipient != msg2.recipient
    assert msg1.placeholders["name"] != msg2.placeholders["name"]
    print("\nEach clone independent — registry safe to reuse ✓")


if __name__ == "__main__":
    main()
