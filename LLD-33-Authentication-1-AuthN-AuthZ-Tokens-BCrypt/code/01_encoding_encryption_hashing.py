"""
01 — Encoding vs Encryption vs Hashing
======================================

Three things students constantly confuse. The one-line difference:

  * ENCODING   — reversible, NO key. Just a different representation
                 (base64). Anyone can decode it. NOT security.
  * ENCRYPTION — reversible WITH a key. Hidden from anyone without the key.
  * HASHING    — ONE-WAY. You can't get the input back, by design.

Passwords are HASHED. Data you need to read back later is ENCRYPTED.
base64 is ENCODING and protects nothing.

Needs:  pip install pytest
"""

import base64
import hashlib
import pytest


# ── ENCODING: base64 — reversible, no key ──

def test_base64_is_reversible_by_anyone_no_key_needed():
    secret = "hunter2"
    encoded = base64.b64encode(secret.encode()).decode()   # "aHVudGVyMg=="
    assert encoded != secret                                # looks scrambled...
    assert base64.b64decode(encoded).decode() == secret     # ...but trivially reversed
    # lesson: base64 is a costume, not a lock. Never "secure" data with it.


# ── ENCRYPTION: reversible WITH a key (toy XOR cipher for illustration) ──
# NOTE: real code uses the `cryptography` library (Fernet / AES-GCM). XOR here
# only demonstrates the *shape*: same function + key encrypts and decrypts.

def xor_cipher(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

def test_encryption_needs_the_key_to_reverse():
    key = b"my-secret-key"
    cipher = xor_cipher(b"transfer 1000", key)

    assert xor_cipher(cipher, key) == b"transfer 1000"           # right key -> back
    assert xor_cipher(cipher, b"wrong-key-xxx") != b"transfer 1000"  # wrong key -> garbage


# ── HASHING: one-way, deterministic, fixed length ──

def test_hash_is_deterministic_and_fixed_length():
    a = hashlib.sha256(b"hunter2").hexdigest()
    b = hashlib.sha256(b"hunter2").hexdigest()
    assert a == b                          # same input -> same hash, always
    assert len(a) == 64                    # sha256 is always 64 hex chars...
    assert len(hashlib.sha256(b"x" * 10_000).hexdigest()) == 64   # ...regardless of size

def test_hash_has_no_reverse_function():
    # there is no hashlib.unsha256 — that's the whole point. You can only
    # verify by hashing a candidate and comparing.
    assert not hasattr(hashlib, "unsha256")

def test_one_bit_change_avalanches_the_whole_hash():
    h1 = hashlib.sha256(b"hunter2").hexdigest()
    h2 = hashlib.sha256(b"hunter3").hexdigest()   # one character different
    differing = sum(1 for x, y in zip(h1, h2) if x != y)
    assert differing > 40                          # ~half the 64 chars flip


if __name__ == "__main__":
    try:
        import pytest as _pt
    except ImportError:
        raise SystemExit("This is a pytest test file. Install pytest first:  pip install pytest")
    raise SystemExit(_pt.main([__file__, "-v", "-p", "no:cacheprovider"]))
