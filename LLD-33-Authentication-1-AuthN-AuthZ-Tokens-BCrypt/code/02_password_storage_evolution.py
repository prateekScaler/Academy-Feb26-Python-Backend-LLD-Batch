"""
02 — Password storage evolution (and the attack that breaks each stage)
=======================================================================

  Stage 1  plaintext        breach = every password, instantly (Facebook 2019)
  Stage 2  md5 / sha (fast) rainbow tables — precomputed hash->password lookups
  Stage 3  salted hash      salt defeats rainbow tables... but fast hashes still
                            fall to GPU brute force (billions/sec)
  Stage 4  slow + salted    bcrypt / scrypt / argon2 — deliberately slow, so each
                            guess costs real time. This is the answer.

These tests PROVE the vulnerability of each stage, so you feel why we moved on.
(Slow hashing here uses stdlib `hashlib.scrypt`; production usually reaches for
bcrypt or argon2 via a library — same idea, salt + a tunable work factor.)

Needs:  pip install pytest
"""

import hashlib
import os
import pytest


# ── Stage 2: a fast, unsalted hash LEAKS that two users share a password ──

def md5(pw: str) -> str:
    return hashlib.md5(pw.encode()).hexdigest()

def test_unsalted_hash_reveals_shared_passwords():
    alice = md5("password123")
    bob   = md5("password123")     # different person, same weak password
    assert alice == bob            # identical hashes -> attacker learns they match
    # and it's rainbow-table-able: this exact md5 is in every cracking dictionary.


# ── Stage 3: a per-user SALT makes identical passwords hash differently ──

def sha256_salted(pw: str, salt: bytes) -> str:
    return hashlib.sha256(salt + pw.encode()).hexdigest()

def test_salt_makes_identical_passwords_hash_differently():
    salt_a, salt_b = os.urandom(16), os.urandom(16)   # unique per user
    alice = sha256_salted("password123", salt_a)
    bob   = sha256_salted("password123", salt_b)
    assert alice != bob            # one leaked rainbow table can't cover both
    # ...but sha256 is still ~billions/sec on a GPU: salt stops tables, not brute force.


# ── Stage 4: slow + salted (scrypt). Same idea, but each guess is expensive ──

def hash_password(pw: str, salt: bytes | None = None) -> tuple[bytes, bytes]:
    salt = salt or os.urandom(16)
    digest = hashlib.scrypt(pw.encode(), salt=salt, n=2**14, r=8, p=1)
    return salt, digest

def test_scrypt_is_salted_and_verifiable():
    salt, digest = hash_password("password123")
    # verify = hash the candidate with the SAME salt and compare
    _, again = hash_password("password123", salt)
    assert again == digest                                  # correct password verifies
    _, wrong = hash_password("password124", salt)
    assert wrong != digest                                  # wrong password fails

def test_scrypt_salts_are_unique_so_hashes_differ():
    (_, a), (_, b) = hash_password("password123"), hash_password("password123")
    assert a != b            # fresh random salt each time -> different stored hash


if __name__ == "__main__":
    try:
        import pytest as _pt
    except ImportError:
        raise SystemExit("This is a pytest test file. Install pytest first:  pip install pytest")
    raise SystemExit(_pt.main([__file__, "-v", "-p", "no:cacheprovider"]))
