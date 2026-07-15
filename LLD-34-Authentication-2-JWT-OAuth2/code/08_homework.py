"""
HOMEWORK — the code under test is COMPLETE and CORRECT. You only write the
tests. Delete each `pytest.skip(...)` and make the assertion real.

Run:  pytest code/08_homework.py -v
Skills exercised: bcrypt anatomy, argon2 rehash, JWT verify/tamper/expiry,
OAuth PKCE. Everything you need is in files 01–04.
"""
import base64
import hashlib
import hmac
import json
import time

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Code under test (correct — don't change it)
# ─────────────────────────────────────────────────────────────────────────────
SECRET = b"hw-secret"


def _b64(raw):  # base64url without padding
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _b64d(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def make_jwt(payload, secret=SECRET):
    h = _b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    p = _b64(json.dumps(payload).encode())
    sig = hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest()
    return f"{h}.{p}.{_b64(sig)}"


def read_jwt(token, secret=SECRET):
    h, p, s = token.split(".")
    expected = hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest()
    if not hmac.compare_digest(expected, _b64d(s)):
        raise ValueError("signature mismatch")
    payload = json.loads(_b64d(p))
    if "exp" in payload and int(time.time()) >= payload["exp"]:
        raise ValueError("expired")
    return payload


def pkce_pair():
    verifier = "fixed-verifier-for-testing-only-1234567890"
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    return verifier, challenge


# ─────────────────────────────────────────────────────────────────────────────
# YOUR TESTS — delete each skip and assert the real behaviour
# ─────────────────────────────────────────────────────────────────────────────

def test_jwt_roundtrip():
    pytest.skip("TODO: make_jwt({'sub': '7'}) then assert read_jwt(...)['sub'] == '7'")


def test_jwt_payload_is_readable_without_the_secret():
    pytest.skip("TODO: split the token on '.', base64url-decode the middle part, "
                "assert you can read the claim WITHOUT knowing SECRET")


def test_tampered_payload_is_rejected():
    pytest.skip("TODO: make a token, swap its payload segment for a forged one, "
                "assert read_jwt raises ValueError('signature mismatch')")


def test_expired_jwt_raises():
    pytest.skip("TODO: make_jwt with exp = now - 10, assert read_jwt raises 'expired'")


def test_token_signed_with_other_secret_is_rejected():
    pytest.skip("TODO: make_jwt(..., secret=b'attacker'), assert read_jwt (default "
                "SECRET) raises 'signature mismatch'")


def test_bcrypt_hash_is_self_describing():
    pytest.skip("TODO: pip install bcrypt; hash a password with rounds=4, "
                "assert the stored string starts with '$2b$04$'")


def test_argon2_hash_verifies_and_rejects_wrong_password():
    pytest.skip("TODO: pip install argon2-cffi; PasswordHasher().hash('pw'), "
                "assert verify(stored, 'pw') is True and verify(stored, 'nope') raises")


def test_pkce_challenge_matches_its_verifier():
    pytest.skip("TODO: use pkce_pair(); assert "
                "sha256url(verifier) == challenge (the check a provider runs)")


def test_pkce_rejects_a_wrong_verifier():
    pytest.skip("TODO: assert sha256url('some-other-verifier') != challenge "
                "from pkce_pair() — a stolen code alone can't be redeemed")
