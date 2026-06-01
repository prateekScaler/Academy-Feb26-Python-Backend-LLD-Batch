"""
LLD-18 · Adapter · Example 5 — The minimal Object Adapter.

Run:  python3 05_basic_object_adapter.py

The smallest possible Adapter, with the three roles spelled out:

  Target   — the interface the client expects
  Adaptee  — the existing object with the "wrong" interface
  Adapter  — implements Target, holds the Adaptee, translates calls

The relationship is COMPOSITION: the Adapter *has-a* Adaptee, not *is-a*.
"""

from __future__ import annotations
from abc import ABC, abstractmethod


# ====================================================================
# Target — what our client code wants to talk to
# ====================================================================
class JSONSink(ABC):
    """Anything that can take a dict and persist it as JSON."""
    @abstractmethod
    def write(self, record: dict) -> None: ...


# ====================================================================
# Adaptee — the third-party class with the "wrong" interface
# ====================================================================
class LegacyXMLWriter:
    """Imagine this is an old library we depend on. We can't change it."""
    def __init__(self) -> None:
        self.buffer: list[str] = []

    def push_xml(self, root_tag: str, fields: list[tuple[str, str]]) -> None:
        inner = "".join(f"<{k}>{v}</{k}>" for k, v in fields)
        self.buffer.append(f"<{root_tag}>{inner}</{root_tag}>")

    def flush(self) -> str:
        out = "".join(self.buffer)
        self.buffer.clear()
        return out


# ====================================================================
# Adapter — speaks JSONSink outward, LegacyXMLWriter inward
# ====================================================================
class XMLWriterToJSONSinkAdapter(JSONSink):
    def __init__(self, xml_writer: LegacyXMLWriter, root_tag: str = "record") -> None:
        self._writer = xml_writer        # COMPOSITION: holds, not inherits
        self._root_tag = root_tag

    def write(self, record: dict) -> None:
        # Translate: dict[str, Any] → list[tuple[str, str]]
        fields = [(k, str(v)) for k, v in record.items()]
        self._writer.push_xml(self._root_tag, fields)


# ====================================================================
# Client code — knows ONLY about Target. Has no idea XML is involved.
# ====================================================================
def export_users(sink: JSONSink, users: list[dict]) -> None:
    for u in users:
        sink.write(u)


if __name__ == "__main__":
    users = [
        {"id": 1, "name": "Ada Lovelace", "role": "admin"},
        {"id": 2, "name": "Grace Hopper", "role": "engineer"},
    ]

    # Plug the legacy XML writer in through the adapter
    legacy = LegacyXMLWriter()
    sink: JSONSink = XMLWriterToJSONSinkAdapter(legacy, root_tag="user")

    export_users(sink, users)

    print("Adapted output (XML, but client never saw XML):")
    print(legacy.flush())
