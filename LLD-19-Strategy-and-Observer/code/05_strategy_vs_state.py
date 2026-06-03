"""
LLD-19 · Strategy vs State · Example 5 — the subtle distinction.

Run:  python3 05_strategy_vs_state.py

Both wrap "what to do next" behind a class. The difference:

  Strategy — the CALLER picks. You set it from outside whenever you want.
  State    — the OBJECT picks (transitions itself in response to events).

Same domain, both flavours, side by side.
"""

from __future__ import annotations
from abc import ABC, abstractmethod


# =====================================================================
# STRATEGY flavour — "compress this with whichever algorithm I tell you"
# =====================================================================
class CompressionStrategy(ABC):
    @abstractmethod
    def compress(self, data: bytes) -> bytes: ...

class GzipCompression(CompressionStrategy):
    def compress(self, data): return b"gz(" + data + b")"

class BrotliCompression(CompressionStrategy):
    def compress(self, data): return b"br(" + data + b")"

class ZstdCompression(CompressionStrategy):
    def compress(self, data): return b"zst(" + data + b")"


class Uploader:
    """The CALLER picks the strategy — Uploader doesn't care."""
    def __init__(self, compression: CompressionStrategy):
        self.compression = compression

    def upload(self, payload: bytes) -> None:
        compressed = self.compression.compress(payload)
        print(f"  uploading {compressed!r}")


# =====================================================================
# STATE flavour — "a Document goes through DRAFT → REVIEW → PUBLISHED
#                  and EACH STATE decides what's legal next"
# =====================================================================
class DocumentState(ABC):
    @abstractmethod
    def submit(self, doc: "Document") -> None: ...
    @abstractmethod
    def approve(self, doc: "Document") -> None: ...
    @abstractmethod
    def name(self) -> str: ...


class DraftState(DocumentState):
    def name(self): return "DRAFT"
    def submit(self, doc):
        print(f"  [{self.name()}] submit() → transitioning to REVIEW")
        doc.state = ReviewState()                     # state CHOOSES the next state
    def approve(self, doc):
        raise RuntimeError("Cannot approve a draft — must submit first")


class ReviewState(DocumentState):
    def name(self): return "REVIEW"
    def submit(self, doc):
        raise RuntimeError("Already in review — cannot submit twice")
    def approve(self, doc):
        print(f"  [{self.name()}] approve() → transitioning to PUBLISHED")
        doc.state = PublishedState()


class PublishedState(DocumentState):
    def name(self): return "PUBLISHED"
    def submit(self, doc):
        raise RuntimeError("Already published")
    def approve(self, doc):
        raise RuntimeError("Already approved")


class Document:
    """The OBJECT picks (its current state decides what's legal)."""
    def __init__(self):
        self.state: DocumentState = DraftState()

    def submit(self):  self.state.submit(self)
    def approve(self): self.state.approve(self)


# =====================================================================
# Demos
# =====================================================================
def demo_strategy() -> None:
    print("--- STRATEGY: the CALLER picks ---")
    payload = b"hello world"
    # caller freely picks any algorithm at any time
    Uploader(GzipCompression()).upload(payload)
    Uploader(BrotliCompression()).upload(payload)
    Uploader(ZstdCompression()).upload(payload)
    print("  Notice: nothing about Uploader's state restricts the choice.\n")


def demo_state() -> None:
    print("--- STATE: the OBJECT picks (transitions itself) ---")
    doc = Document()
    print(f"  initial: {doc.state.name()}")

    doc.submit()                          # legal — transitions to REVIEW
    doc.approve()                         # legal — transitions to PUBLISHED

    print(f"  final:   {doc.state.name()}")
    try:
        doc.submit()
    except RuntimeError as e:
        print(f"  blocked: {e}")
    print("\n  Notice: the legal actions changed AS THE STATE CHANGED.")
    print("  The caller couldn't have forced an illegal transition.")


if __name__ == "__main__":
    demo_strategy()
    demo_state()
    print("\nMnemonic:")
    print("  Strategy: 'I'll use THIS algorithm for the next call.'  ← caller decides")
    print("  State:    'I'm in THIS mode, so only these moves are legal.'  ← object decides")
