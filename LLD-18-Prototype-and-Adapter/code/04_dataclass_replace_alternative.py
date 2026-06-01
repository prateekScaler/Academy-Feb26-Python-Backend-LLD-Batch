"""
LLD-18 · Prototype · Example 4 — When Prototype is overkill.

Run:  python3 04_dataclass_replace_alternative.py

Not every "I want a similar object with one field changed" needs the full
Prototype pattern. For simple immutable dataclasses, the standard library
already gives you `dataclasses.replace()` — one line, no clone method, no
copy module, no extra class.

This file demonstrates when each approach is right.
"""

from dataclasses import dataclass, replace
import copy


# ====================================================================
# A.  SIMPLE CASE — use dataclasses.replace, NOT Prototype
# ====================================================================
@dataclass(frozen=True)
class PageRequest:
    """A simple, immutable request object. Just five primitive fields."""
    url: str
    method: str = "GET"
    timeout: float = 5.0
    retries: int = 3
    verify_ssl: bool = True


def demo_simple_case() -> None:
    print("--- Simple immutable dataclass: use dataclasses.replace ---")
    base = PageRequest(url="https://scaler.com/courses")

    # One-line "copy with one tweak" — no Prototype needed.
    long_timeout = replace(base, timeout=30.0)
    no_ssl_verify = replace(base, verify_ssl=False)
    a_post = replace(base, method="POST", retries=0)

    print(f"  base          = {base}")
    print(f"  long_timeout  = {long_timeout}")
    print(f"  no_ssl_verify = {no_ssl_verify}")
    print(f"  a_post        = {a_post}")
    print("  Zero clone() method written. Zero copy module used.\n")


# ====================================================================
# B.  NON-SIMPLE CASE — Prototype is still the right tool
# ====================================================================
class BaseConfig:
    """Expensive to build (imagine 1.2s of DB + network + warm-up).
       Mutable, holds dicts. dataclasses.replace can't help here."""

    def __init__(self) -> None:
        print("    [BaseConfig.__init__] ... pretending this takes 1.2s ...")
        self.flags: dict[str, bool] = {f"flag_{i}": False for i in range(200)}
        self.pricing: dict[str, float] = {"basic": 9.99, "pro": 29.99}
        self.segments: dict[str, list[str]] = {"new_users": [], "vip": []}

    def clone(self) -> "BaseConfig":
        return copy.deepcopy(self)


def demo_prototype_case() -> None:
    print("--- Expensive + mutable: Prototype earns its keep ---")
    prototype = BaseConfig()                 # 1 expensive build

    experiments = ["flag_5", "flag_42", "flag_88"]
    for flag in experiments:
        cfg = prototype.clone()              # cheap deepcopy
        cfg.flags[flag] = True               # tweak one bit
        print(f"  experiment {flag}: flag set on independent clone")

    # Original prototype must remain untouched
    assert prototype.flags["flag_5"] is False
    print("  Prototype unchanged — clones isolated ✓\n")


# ====================================================================
# C.  DECISION RULE
# ====================================================================
DECISION_RULE = """
   ┌─────────────────────────────────────────────────────────────┐
   │  Is the class an immutable @dataclass with primitive fields?│
   │                                                             │
   │     YES ──► use dataclasses.replace(obj, field=new)         │
   │     NO  ──► is __init__ expensive AND you need many?        │
   │                                                             │
   │             YES ──► implement Prototype (clone + deepcopy)  │
   │             NO  ──► just call the constructor               │
   └─────────────────────────────────────────────────────────────┘
"""


if __name__ == "__main__":
    demo_simple_case()
    demo_prototype_case()
    print(DECISION_RULE)
