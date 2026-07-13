"""
08 — HOMEWORK: you write the tests (auth)
=========================================

The code under test is COMPLETE and CORRECT — you only write the tests.
Delete each `pytest.skip(...)` and make it pass.

    pytest -v 08_homework.py     ->  s s s ...   then   . . . (all PASSED)

Skills (this class):
  * hashing is one-way & deterministic            (model: file 01)
  * a salt makes equal passwords hash differently (model: file 02)
  * constant-time compare for secrets             (model: file 03)
  * a JWT: round-trip, readable payload, tamper-proof, expiry  (model: file 04)
  * RBAC: permissions compose; check perms not roles (model: file 05)

Needs:  pip install pytest
"""

import hashlib
import hmac
import os
import time
import pytest

# reuse the from-scratch JWT built in file 04
from importlib import import_module
jwtmod = import_module("04_build_a_jwt_from_scratch")
encode_jwt, decode_jwt, InvalidToken = jwtmod.encode_jwt, jwtmod.decode_jwt, jwtmod.InvalidToken


# ═══════════════════ the code under test ═══════════════════

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def hash_with_salt(pw: str, salt: bytes) -> bytes:
    return hashlib.scrypt(pw.encode(), salt=salt, n=2**14, r=8, p=1)

ROLE_PERMS = {"viewer": {"read"}, "editor": {"read", "write"}}
def permissions_for(roles: set[str]) -> set[str]:
    out: set[str] = set()
    for r in roles:
        out |= ROLE_PERMS.get(r, set())
    return out


# ═══════════════════ the exercises ═══════════════════

def test_ex01_sha256_is_deterministic():
    # Assert sha256_hex("abc") gives the same value twice, and is 64 chars long.
    pytest.skip("TODO ex01")

def test_ex02_sha256_has_no_reverse():
    # Assert there is no hashlib attribute that un-hashes (e.g. 'unsha256').
    pytest.skip("TODO ex02")

def test_ex03_salt_changes_the_hash():
    # Hash "hunter2" with two different os.urandom(16) salts; assert the two
    # digests differ (hash_with_salt).
    pytest.skip("TODO ex03")

def test_ex04_same_salt_same_hash_so_you_can_verify():
    # Hash "hunter2" twice with the SAME salt; assert the digests are equal.
    pytest.skip("TODO ex04")

def test_ex05_constant_time_compare():
    # Use hmac.compare_digest: assert it's True for two equal byte strings and
    # False for two that differ in the last byte.
    pytest.skip("TODO ex05")

def test_ex06_jwt_round_trips():
    # encode_jwt({"sub": "7"}) then decode_jwt(...) == {"sub": "7"}.
    pytest.skip("TODO ex06")

def test_ex07_a_tampered_jwt_is_rejected():
    # Take a valid token, change a character in its payload segment, and assert
    # decode_jwt raises InvalidToken (use pytest.raises).
    pytest.skip("TODO ex07")

def test_ex08_an_expired_jwt_is_rejected():
    # encode_jwt with "exp": time.time() - 1, assert decode_jwt raises InvalidToken.
    pytest.skip("TODO ex08")

def test_ex09_editor_permissions_compose():
    # Assert permissions_for({"editor"}) == {"read", "write"} and that
    # permissions_for({"viewer"}) has no "write".
    pytest.skip("TODO ex09")


if __name__ == "__main__":
    try:
        import pytest as _pt
    except ImportError:
        raise SystemExit("This is a pytest test file. Install pytest first:  pip install pytest")
    raise SystemExit(_pt.main([__file__, "-v", "-p", "no:cacheprovider"]))
