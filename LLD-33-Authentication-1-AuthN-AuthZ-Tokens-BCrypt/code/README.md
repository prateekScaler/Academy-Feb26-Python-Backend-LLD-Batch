# LLD-33 · code/ — runnable examples

Pure **pytest**, **stdlib only** (`hashlib`, `hmac`, `base64`, `secrets`) — no
`bcrypt`/`pyjwt` install needed. 30 tests green + a 9-stub homework.

```bash
pip install pytest
pytest -v 01_encoding_encryption_hashing.py
python3 01_encoding_encryption_hashing.py     # same — hands over to pytest
pytest -q 0*.py                               # the whole folder
```

| File | What it teaches |
|---|---|
| `01_encoding_encryption_hashing.py` | The three that get confused: **encoding** (base64, reversible, no key — not security), **encryption** (reversible *with* a key), **hashing** (one-way, deterministic, fixed-length, avalanche). |
| `02_password_storage_evolution.py` | Each stage and the attack that breaks it: plaintext → fast unsalted hash (**reveals shared passwords** / rainbow tables) → **salt** (defeats tables, not brute force) → **scrypt** (slow + salted, verifiable). |
| `03_verifying_safely_timing.py` | Comparing secrets leaks too: `hmac.compare_digest` runs in constant time so response timing can't reveal how many bytes matched (**timing attack**). |
| `04_build_a_jwt_from_scratch.py` | A JWT by hand with `hmac` + `base64url` + `json`: `header.payload.signature`. Proves it — round-trips, the payload is **readable without the secret** (signed ≠ encrypted), tampering & wrong-secret are **rejected**, and `exp` expires it. |
| `05_rbac.py` | Authorization: **users → roles → permissions**, roles compose, and you check a *permission* not a *role name* (the same association shape as LLD-29's Membership). |
| `06_password_service.py` | It all together: a `PasswordService` that stores `(salt, scrypt-hash)` — never the password — and `verify()`s with a constant-time compare. |
| `08_homework.py` | **HOMEWORK** — hashing, salting, constant-time compare, JWT (round-trip / tamper / expiry) and RBAC: 9 `pytest.skip` stubs to turn green. |

> **In production** use `bcrypt` or `argon2-cffi` for passwords and `PyJWT` for tokens — they bundle the salt, work factor, and signing safely. These files build the pieces by hand (on stdlib `scrypt`/`hmac`) so the mechanisms stop being magic; the *shape* is identical.
