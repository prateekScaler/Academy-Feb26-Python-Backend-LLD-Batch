"""
LLD-20 · Decorator vs Adapter · Example 4 — the structural-pattern lookalikes.

Run:  python3 04_decorator_vs_adapter.py

Decorator and Adapter look identical on a UML class diagram:
both are a wrapper class that holds another object. The pattern
name says WHY the wrapping exists, not how it's coded.

This file shows both around the SAME object so the difference
is impossible to miss.

  - Decorator:  same interface as wrapped, ADDS behaviour
  - Adapter:    different interface from wrapped, TRANSLATES calls
"""

from __future__ import annotations
from abc import ABC, abstractmethod


# ====================================================================
# Scenario: we have an old vendor library (LegacyXMLWriter)
# that exposes write_xml(tag, fields). Our codebase wants two things:
#
#   1. To talk to it via a JSON-like interface (Adapter use case)
#   2. To add logging around writes (Decorator use case)
# ====================================================================

# ----- The Adaptee: foreign vendor SDK we can't change -----
class LegacyXMLWriter:
    def __init__(self) -> None:
        self.buffer: list[str] = []

    def write_xml(self, root_tag: str, fields: list[tuple[str, str]]) -> None:
        inner = "".join(f"<{k}>{v}</{k}>" for k, v in fields)
        self.buffer.append(f"<{root_tag}>{inner}</{root_tag}>")


# =====================================================================
# Adapter — DIFFERENT interface, translates dict → list of tuples
# =====================================================================
class JSONSink(ABC):
    """Our codebase's target interface — takes a dict, writes a record."""
    @abstractmethod
    def write(self, record: dict) -> None: ...


class XMLWriterAdapter(JSONSink):
    """Implements JSONSink (the Target) by wrapping LegacyXMLWriter (the Adaptee)."""
    def __init__(self, writer: LegacyXMLWriter, root_tag: str = "record") -> None:
        self._writer = writer
        self._root = root_tag

    # Translates: dict → list of tuples; renamed method
    def write(self, record: dict) -> None:
        fields = [(k, str(v)) for k, v in record.items()]
        self._writer.write_xml(self._root, fields)


# =====================================================================
# Decorator — SAME interface as wrapped, ADDS behaviour
# =====================================================================
class LoggedJSONSink(JSONSink):
    """Wraps a JSONSink and exposes the same JSONSink interface, plus logging."""
    def __init__(self, inner: JSONSink) -> None:
        self._inner = inner

    def write(self, record: dict) -> None:
        print(f"  [log] writing record with keys: {list(record.keys())}")
        self._inner.write(record)
        print("  [log] done")


# =====================================================================
# Demo
# =====================================================================
def main() -> None:
    raw = LegacyXMLWriter()

    print("--- 1. The Adapter: same wrapping shape, DIFFERENT interface ---")
    adapter: JSONSink = XMLWriterAdapter(raw, root_tag="user")
    adapter.write({"id": 1, "name": "Ada", "role": "admin"})
    print("  XML produced:", raw.buffer[-1])
    print("  Caller called .write(dict). Adapter changed the SHAPE of the call.")

    print("\n--- 2. The Decorator: same wrapping shape, SAME interface ---")
    decorated: JSONSink = LoggedJSONSink(adapter)
    decorated.write({"id": 2, "name": "Grace", "role": "engineer"})
    print("  XML produced:", raw.buffer[-1])
    print("  Caller called .write(dict). Decorator added behaviour AROUND it.")

    print("\n--- 3. Both at once: Decorator wrapping Adapter wrapping Adaptee ---")
    print("  LoggedJSONSink( XMLWriterAdapter( LegacyXMLWriter() ) )")
    print("  decorated.write(record) →")
    print("    log 'before'   ← decorator")
    print("    write(dict)    ← decorator delegates to its inner (the adapter)")
    print("      translate dict → tuples + call write_xml  ← adapter")
    print("        push '<user>...</user>' to buffer       ← adaptee")
    print("    log 'done'     ← decorator")
    print("\nSame UML on paper. Two different intents.")
    print("  Adapter intent: 'I want this in MY interface.'")
    print("  Decorator intent: 'I want behaviour AROUND each call.'")


if __name__ == "__main__":
    main()
