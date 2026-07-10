"""
02 — monkeypatch: replace a name for one test
=============================================

Dependency injection is best — but you can't always add a seam (the code
calls a module-level function, reads an env var, or touches `random`
directly). pytest's built-in `monkeypatch` fixture swaps a name out for
the duration of ONE test and puts it back automatically afterwards.

Needs:  pip install pytest
"""

import os
import random
import pytest


def promo_discount() -> int:
    """Reads the environment AND randomness directly — no injection point."""
    if os.environ.get("PROMO") == "on":
        return random.choice([10, 20, 30])
    return 0


def test_env_and_randomness_are_pinned(monkeypatch):
    monkeypatch.setenv("PROMO", "on")                    # control the env
    monkeypatch.setattr(random, "choice", lambda seq: seq[0])   # de-randomise
    assert promo_discount() == 10
    # nothing to clean up — monkeypatch undoes BOTH after the test


def test_promo_off_gives_no_discount(monkeypatch):
    monkeypatch.delenv("PROMO", raising=False)
    assert promo_discount() == 0


def test_the_undo_is_automatic():
    # by now the previous test's setenv/setattr are already reverted:
    assert "PROMO" not in os.environ or os.environ.get("PROMO") != "on"
    assert random.choice.__module__ == "random"          # real function restored


if __name__ == "__main__":
    try:
        import pytest as _pt
    except ImportError:
        raise SystemExit("This is a pytest test file. Install pytest first:  pip install pytest")
    raise SystemExit(_pt.main([__file__, "-v", "-p", "no:cacheprovider"]))
