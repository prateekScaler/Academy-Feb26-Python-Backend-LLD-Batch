"""
06 — A proper password service (putting it together)
====================================================

Everything from files 01-03, as the small service you'd actually ship:
  * register  -> slow, salted hash (scrypt); store salt + hash, never the password
  * verify    -> hash the candidate with the stored salt, constant-time compare
  * the stored value never contains the plaintext password

(Production tip: reach for `bcrypt` or `argon2-cffi` — they bundle salt + work
factor and are battle-tested. The shape below is identical; scrypt is stdlib so
this file runs with zero installs.)

Needs:  pip install pytest
"""

import hashlib
import hmac
import os
import pytest

N, R, P = 2**14, 8, 1        # scrypt work factors (tune up as hardware improves)


class PasswordService:
    def __init__(self):
        self._store: dict[str, tuple[bytes, bytes]] = {}   # user -> (salt, hash)

    def register(self, user: str, password: str) -> None:
        salt = os.urandom(16)
        digest = hashlib.scrypt(password.encode(), salt=salt, n=N, r=R, p=P)
        self._store[user] = (salt, digest)                 # NOT the password

    def verify(self, user: str, password: str) -> bool:
        if user not in self._store:
            return False
        salt, expected = self._store[user]
        candidate = hashlib.scrypt(password.encode(), salt=salt, n=N, r=R, p=P)
        return hmac.compare_digest(candidate, expected)    # constant-time


@pytest.fixture
def svc():
    s = PasswordService()
    s.register("vipul", "correct horse battery staple")
    return s


def test_the_right_password_verifies(svc):
    assert svc.verify("vipul", "correct horse battery staple") is True

def test_a_wrong_password_is_rejected(svc):
    assert svc.verify("vipul", "Correct Horse Battery Staple") is False

def test_an_unknown_user_is_rejected_without_crashing(svc):
    assert svc.verify("ghost", "anything") is False

def test_the_plaintext_password_is_never_stored(svc):
    salt, digest = svc._store["vipul"]
    assert b"correct horse battery staple" not in salt + digest

def test_two_users_with_the_same_password_get_different_hashes(svc):
    svc.register("mallory", "correct horse battery staple")   # same password
    assert svc._store["vipul"][1] != svc._store["mallory"][1]  # different salt -> hash


if __name__ == "__main__":
    try:
        import pytest as _pt
    except ImportError:
        raise SystemExit("This is a pytest test file. Install pytest first:  pip install pytest")
    raise SystemExit(_pt.main([__file__, "-v", "-p", "no:cacheprovider"]))
