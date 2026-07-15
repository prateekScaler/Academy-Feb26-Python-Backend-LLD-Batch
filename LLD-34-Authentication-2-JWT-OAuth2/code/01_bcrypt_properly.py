"""
LLD-33 introduced WHY slow hashing wins. This file is bcrypt IN PRACTICE —
the real library, the real hash string, the real cost curve.

Needs:  pip install pytest bcrypt
        (every test here skips politely if bcrypt isn't installed)

Try it live too: https://bcrypt-generator.com — paste a password, move the
"rounds" slider, and feel the cost factor with your own clock.
"""
import base64
import hashlib
import time

import pytest

bcrypt = pytest.importorskip("bcrypt", reason="pip install bcrypt to run this file")


# ── 1. The API is two calls: hashpw to store, checkpw to verify ─────────────

def test_hash_and_verify_roundtrip():
    stored = bcrypt.hashpw(b"correct horse battery staple", bcrypt.gensalt(rounds=4))
    assert bcrypt.checkpw(b"correct horse battery staple", stored)   # right password
    assert not bcrypt.checkpw(b"correct horse battery stapl", stored)  # wrong password


def test_nothing_is_ever_decrypted():
    """checkpw re-hashes the attempt with the SAME salt and compares.
    There is no 'bcrypt.decrypt' — the password cannot come back."""
    assert not hasattr(bcrypt, "decrypt")


# ── 2. Anatomy of the stored string: $2b$12$<22-char salt><31-char hash> ────

def test_hash_string_anatomy():
    stored = bcrypt.hashpw(b"hunter2", bcrypt.gensalt(rounds=12)).decode()
    #        $2b$      12$        <22 chars of salt><31 chars of hash>
    assert stored.startswith("$2b$12$")
    _, version, cost, salt_and_hash = stored.split("$")
    assert version == "2b"          # bcrypt variant
    assert int(cost) == 12          # the work factor, stored IN the hash
    assert len(salt_and_hash) == 53  # 22 (salt) + 31 (hash), bcrypt's base64
    # Because salt + cost live inside the string, verification needs NO extra
    # columns — and you can raise the cost for new users without breaking old.


def test_same_password_two_users_different_hashes():
    a = bcrypt.hashpw(b"letmein", bcrypt.gensalt(rounds=4))
    b = bcrypt.hashpw(b"letmein", bcrypt.gensalt(rounds=4))
    assert a != b                      # unique salt each time
    assert bcrypt.checkpw(b"letmein", a) and bcrypt.checkpw(b"letmein", b)


# ── 3. The cost factor: each +1 DOUBLES the work ────────────────────────────

def _timed_hash(rounds: int) -> float:
    start = time.perf_counter()
    bcrypt.hashpw(b"benchmark", bcrypt.gensalt(rounds=rounds))
    return time.perf_counter() - start


def test_each_extra_round_roughly_doubles_the_time():
    fast, slow = _timed_hash(8), _timed_hash(11)     # 3 steps apart ⇒ ~8×
    assert slow > fast * 3   # generous bound; on quiet machines it's ~8×
    # This is ADAPTIVE security: hardware gets faster → you bump one integer.


# ── 4. The 72-byte gotcha every bcrypt user must know ───────────────────────

def test_bcrypt_caps_the_password_at_72_bytes():
    """bcrypt only ever looks at the first 72 bytes. Historically (bcrypt < 4)
    it SILENTLY TRUNCATED — so 'x'*72 + anything all hashed the same, a real
    footgun for long passphrases. Modern bcrypt (4.x) refuses instead:"""
    with pytest.raises(ValueError, match="72 bytes"):
        bcrypt.hashpw(b"x" * 73, bcrypt.gensalt(rounds=4))
    # Either way the lesson stands: for long inputs, pre-hash with sha256 first
    # (base64 the digest) or cap length at signup — never rely on the tail.

    prehashed = base64.b64encode(hashlib.sha256(b"a very long passphrase " * 10).digest())
    stored = bcrypt.hashpw(prehashed, bcrypt.gensalt(rounds=4))   # always < 72 bytes
    assert bcrypt.checkpw(prehashed, stored)
