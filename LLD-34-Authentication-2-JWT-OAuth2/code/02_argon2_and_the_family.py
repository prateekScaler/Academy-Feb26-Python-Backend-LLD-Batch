"""
bcrypt is great; argon2 is what OWASP recommends FIRST in 2024. This file
shows the modern password-hash family and the ONE axis bcrypt can't offer:
memory-hardness (starving GPUs/ASICs of RAM, not just CPU time).

Needs:  pip install pytest argon2-cffi
        scrypt needs nothing — it's in the stdlib (hashlib), used as the
        memory-hard example that always runs.

The password-hash family, at a glance:
    PBKDF2   — slow via many iterations. CPU-hard only. FIPS-approved.
    bcrypt   — slow via cost factor. CPU-hard. 72-byte cap. Battle-tested.
    scrypt   — CPU + MEMORY hard. Tunable RAM (N,r,p). In the stdlib.
    argon2id — CPU + MEMORY + parallelism. 2015 PHC winner. OWASP's pick.
"""
import hashlib

import pytest


# ── scrypt (stdlib): the memory-hard idea, zero installs ────────────────────

def test_scrypt_is_deterministic_with_same_salt_and_params():
    salt = b"a-fixed-salt-16b"
    kw = dict(salt=salt, n=2**14, r=8, p=1, dklen=32)   # n = CPU/MEM cost
    assert hashlib.scrypt(b"pw", **kw) == hashlib.scrypt(b"pw", **kw)
    assert hashlib.scrypt(b"pw", **kw) != hashlib.scrypt(b"different", **kw)


def test_scrypt_memory_cost_is_a_dial():
    """n is the work/memory knob — raising it costs more CPU AND more RAM.
    Unlike bcrypt, the attacker needs proportionally more memory per guess,
    which is what blunts massively-parallel GPUs/ASICs.
    (scrypt RAM ≈ 128 * n * r bytes, so we pass maxmem to allow the bigger n.)"""
    salt = b"a-fixed-salt-16b"
    cheap = hashlib.scrypt(b"pw", salt=salt, n=2**12, r=8, p=1)
    dear = hashlib.scrypt(b"pw", salt=salt, n=2**15, r=8, p=1, maxmem=128 * 2**20)
    assert cheap != dear     # different params ⇒ different derived key


# ── argon2id: the modern default ────────────────────────────────────────────

argon2 = pytest.importorskip("argon2", reason="pip install argon2-cffi to run these")


def test_argon2_hash_and_verify():
    from argon2 import PasswordHasher
    ph = PasswordHasher()                       # sensible defaults (argon2id)
    stored = ph.hash("correct horse")
    assert stored.startswith("$argon2id$")      # self-describing, like bcrypt
    assert ph.verify(stored, "correct horse")   # returns True or raises
    with pytest.raises(argon2.exceptions.VerifyMismatchError):
        ph.verify(stored, "wrong horse")


def test_argon2_encodes_all_three_costs_in_the_hash():
    from argon2 import PasswordHasher
    ph = PasswordHasher(time_cost=2, memory_cost=64 * 1024, parallelism=2)
    stored = ph.hash("pw")
    # $argon2id$v=19$m=65536,t=2,p=2$<salt>$<hash>  — m (RAM KiB), t (passes), p (lanes)
    assert "m=65536" in stored and "t=2" in stored and "p=2" in stored
    # bcrypt has ONE knob (cost). argon2 has THREE — tune RAM independently.


def test_argon2_needs_rehash_when_params_change():
    """As you raise cost over the years, check_needs_rehash tells you which
    stored hashes are stale so you can upgrade them on the user's next login."""
    from argon2 import PasswordHasher
    weak = PasswordHasher(time_cost=1, memory_cost=8, parallelism=1)
    strong = PasswordHasher(time_cost=3, memory_cost=64 * 1024, parallelism=4)
    stored = weak.hash("pw")
    assert strong.check_needs_rehash(stored) is True
