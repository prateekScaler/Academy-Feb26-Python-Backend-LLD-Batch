"""
03 — Verifying safely: constant-time comparison
===============================================

Storing the hash right is half the job. COMPARING it also leaks — a naive
`==` on secrets can short-circuit on the first wrong byte, and an attacker
who measures response time can recover a token/hash byte by byte (a TIMING
ATTACK). Use `hmac.compare_digest`, which always compares the whole thing.

Needs:  pip install pytest
"""

import hmac
import pytest


def test_compare_digest_matches_equal_secrets():
    token = "a1b2c3d4e5"
    assert hmac.compare_digest(token, "a1b2c3d4e5") is True

def test_compare_digest_rejects_a_wrong_secret():
    assert hmac.compare_digest("a1b2c3d4e5", "a1b2c3d4e6") is False

def test_compare_digest_is_the_tool_for_secret_comparison():
    # `==` is correct too — but it may return early on the first differing byte,
    # so the time it takes hints at HOW MANY leading bytes matched. compare_digest
    # runs in time independent of where the mismatch is. Same answer, no leak.
    good = "s3cr3t-token-value"
    assert hmac.compare_digest(good, good) == (good == good)
    assert hmac.compare_digest(good, "x" + good[1:]) is False

def constant_time_verify(stored_hash: bytes, candidate_hash: bytes) -> bool:
    return hmac.compare_digest(stored_hash, candidate_hash)

def test_verify_helper_uses_constant_time_compare():
    h = b"\x01\x02\x03\x04"
    assert constant_time_verify(h, b"\x01\x02\x03\x04") is True
    assert constant_time_verify(h, b"\x01\x02\x03\x05") is False


if __name__ == "__main__":
    try:
        import pytest as _pt
    except ImportError:
        raise SystemExit("This is a pytest test file. Install pytest first:  pip install pytest")
    raise SystemExit(_pt.main([__file__, "-v", "-p", "no:cacheprovider"]))
