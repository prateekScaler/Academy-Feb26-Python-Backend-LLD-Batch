"""
LLD-18 · Adapter · Example 7 — Class Adapter vs Object Adapter.

Run:  python3 07_class_vs_object_adapter.py

The GoF describes two flavours of Adapter:

  Object Adapter (composition)
      Adapter HAS-A Adaptee. Idiomatic in Python. Hides the Adaptee
      cleanly behind the Target interface.

  Class Adapter (multiple inheritance)
      Adapter IS-A Target AND IS-A Adaptee. Works in Python but leaks
      every method of the Adaptee, and pulls in MRO complexity.

This file shows both and demonstrates the leak.
"""

from __future__ import annotations
from abc import ABC, abstractmethod


# ====================================================================
# Target
# ====================================================================
class Logger(ABC):
    """The interface our codebase expects."""
    @abstractmethod
    def log(self, level: str, message: str) -> None: ...


# ====================================================================
# Adaptee
# ====================================================================
class OldFileWriter:
    """A legacy file writer with its own (incompatible) API."""

    def __init__(self) -> None:
        self.lines: list[str] = []

    def write_line(self, severity: int, text: str) -> None:
        # 0 = debug, 1 = info, 2 = warning, 3 = error
        self.lines.append(f"[sev={severity}] {text}")

    def dump(self) -> str:
        return "\n".join(self.lines)


# ====================================================================
# Object Adapter — composition (RECOMMENDED)
# ====================================================================
class ObjectAdapterLogger(Logger):
    _LEVEL_TO_SEV = {"debug": 0, "info": 1, "warning": 2, "error": 3}

    def __init__(self, writer: OldFileWriter) -> None:
        self._writer = writer        # HAS-A relationship

    def log(self, level: str, message: str) -> None:
        sev = self._LEVEL_TO_SEV[level]
        self._writer.write_line(sev, message)


# ====================================================================
# Class Adapter — multiple inheritance (RARELY WORTH IT)
# ====================================================================
class ClassAdapterLogger(Logger, OldFileWriter):
    _LEVEL_TO_SEV = {"debug": 0, "info": 1, "warning": 2, "error": 3}

    def __init__(self) -> None:
        OldFileWriter.__init__(self)

    def log(self, level: str, message: str) -> None:
        # We can call write_line directly — it's inherited
        self.write_line(self._LEVEL_TO_SEV[level], message)


# ====================================================================
# Demonstrate the leak
# ====================================================================
def main() -> None:
    # --- Object Adapter ---
    print("--- Object Adapter (composition) ---")
    writer = OldFileWriter()
    obj_log: Logger = ObjectAdapterLogger(writer)
    obj_log.log("info", "user signed in")
    obj_log.log("error", "db timeout")
    print(writer.dump())

    # The client only sees Logger's API. The adapter's _writer is private.
    print(f"  public methods of obj_log: {[m for m in dir(obj_log) if not m.startswith('_')]}")
    print("  ↑ Only 'log' is exposed — Adaptee hidden cleanly.\n")

    # --- Class Adapter — the leak ---
    print("--- Class Adapter (multiple inheritance) ---")
    cls_log = ClassAdapterLogger()
    cls_log.log("info", "user signed in")
    cls_log.log("error", "db timeout")
    print(cls_log.dump())

    leaked = [m for m in dir(cls_log) if not m.startswith("_") and m not in {"log"}]
    print(f"  public methods of cls_log: ['log', ...] PLUS leaked: {leaked}")
    print("  ↑ write_line and dump are now part of the adapter's public surface.")
    print("    Any caller can bypass log() and call cls_log.write_line(99, '...').")
    print("    That defeats the abstraction.")


if __name__ == "__main__":
    main()
