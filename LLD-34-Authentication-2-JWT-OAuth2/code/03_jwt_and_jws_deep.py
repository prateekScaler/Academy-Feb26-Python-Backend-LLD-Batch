"""
LLD-33 built a JWT once to show header.payload.signature. Here we go DEEP —
still stdlib-only (hmac, hashlib, base64, json), zero installs, always green —
so you can see exactly what PyJWT does for you, and the attacks it defends.

A JWT is the common shape of a JWS (JSON Web SIGNATURE): a signed, readable
token. (Its lesser-seen cousin JWE is ENCRYPTED — unreadable. 99% of "JWT"
in the wild means JWS. Signed ≠ encrypted: the payload is public.)

Production: `pip install PyJWT` — jwt.encode / jwt.decode. Never hand-roll
crypto in real systems; we hand-roll here only to demystify it.
Decode any real token by hand at https://jwt.io.
"""
import base64
import hashlib
import hmac
import json
import time

import pytest

SECRET = b"server-only-secret-key"


# ── the three primitives ────────────────────────────────────────────────────

def b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def b64url_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def sign(header: dict, payload: dict, secret: bytes = SECRET) -> str:
    h = b64url(json.dumps(header, separators=(",", ":")).encode())
    p = b64url(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{h}.{p}".encode()
    sig = hmac.new(secret, signing_input, hashlib.sha256).digest()
    return f"{h}.{p}.{b64url(sig)}"


def verify(token: str, secret: bytes = SECRET) -> dict:
    h, p, s = token.split(".")
    header = json.loads(b64url_decode(h))
    # 1) DEFEND ALG-CONFUSION: pin the algorithm; never trust the header's alg.
    if header.get("alg") != "HS256":
        raise ValueError(f"unexpected alg: {header.get('alg')!r}")
    # 2) recompute the signature and compare in CONSTANT TIME (LLD-33, step 4)
    expected = hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest()
    if not hmac.compare_digest(expected, b64url_decode(s)):
        raise ValueError("signature mismatch — token forged or altered")
    payload = json.loads(b64url_decode(p))
    # 3) honour expiry (exp) and not-before (nbf)
    now = int(time.time())
    if "exp" in payload and now >= payload["exp"]:
        raise ValueError("token expired")
    if "nbf" in payload and now < payload["nbf"]:
        raise ValueError("token not yet valid")
    return payload


# ── 1. happy path ───────────────────────────────────────────────────────────

def test_roundtrip_reads_the_claims_back():
    token = sign({"alg": "HS256", "typ": "JWT"}, {"sub": "42", "role": "admin"})
    assert verify(token) == {"sub": "42", "role": "admin"}


def test_anyone_can_read_the_payload_signed_not_encrypted():
    """The middle segment is only base64 — no secret needed to READ it.
    This is why you must never put a password/card/PII in a JWT."""
    token = sign({"alg": "HS256"}, {"sub": "42", "email": "a@b.com"})
    _, p, _ = token.split(".")
    assert json.loads(b64url_decode(p))["email"] == "a@b.com"   # readable by all


# ── 2. tamper detection ─────────────────────────────────────────────────────

def test_editing_a_claim_breaks_the_signature():
    token = sign({"alg": "HS256"}, {"sub": "42", "role": "user"})
    h, _, s = token.split(".")
    forged_payload = b64url(json.dumps({"sub": "42", "role": "admin"}).encode())
    forged = f"{h}.{forged_payload}.{s}"        # promote yourself to admin...
    with pytest.raises(ValueError, match="signature mismatch"):
        verify(forged)                          # ...and verification rejects it


# ── 3. the classic attacks ──────────────────────────────────────────────────

def test_alg_none_attack_is_refused():
    """The infamous CVE: attacker sets alg='none' and drops the signature,
    hoping the server 'trusts' an unsigned token. Pinning alg kills it."""
    h = b64url(json.dumps({"alg": "none", "typ": "JWT"}).encode())
    p = b64url(json.dumps({"sub": "42", "role": "admin"}).encode())
    with pytest.raises(ValueError, match="unexpected alg"):
        verify(f"{h}.{p}.")


def test_wrong_secret_cannot_forge():
    attacker_token = sign({"alg": "HS256"}, {"role": "admin"}, secret=b"guessed")
    with pytest.raises(ValueError, match="signature mismatch"):
        verify(attacker_token)                  # server's real SECRET differs


# ── 4. expiry & the access/refresh pattern ──────────────────────────────────

def test_expired_token_is_rejected():
    token = sign({"alg": "HS256"}, {"sub": "42", "exp": int(time.time()) - 1})
    with pytest.raises(ValueError, match="expired"):
        verify(token)


def test_short_lived_access_token_still_valid_within_window():
    token = sign({"alg": "HS256"}, {"sub": "42", "exp": int(time.time()) + 900})
    assert verify(token)["sub"] == "42"
    # Access token (~15 min, sent every request) + refresh token (~days, only
    # to /refresh) is the standard answer to "JWTs are hard to revoke".
