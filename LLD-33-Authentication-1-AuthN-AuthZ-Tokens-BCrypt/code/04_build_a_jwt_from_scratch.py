"""
04 — Build a JWT from scratch (so it stops being magic)
=======================================================

A JWT is just three base64url parts joined by dots:

    header . payload . signature

  header    = {"alg":"HS256","typ":"JWT"}         (metadata)
  payload   = your claims: sub, exp, iat, ...      (the data)
  signature = HMAC-SHA256(header.payload, SECRET)  (the seal)

Key truths this file proves:
  * the payload is only ENCODED, not encrypted — anyone can read it.
  * the SIGNATURE is what makes it trustworthy — tamper with the payload and
    verification fails, because you can't forge the signature without the secret.
  * `exp` lets the token expire.

Production uses PyJWT; we build it by hand once to demystify it.

Needs:  pip install pytest
"""

import base64
import hashlib
import hmac
import json
import time
import pytest

SECRET = b"a-256-bit-secret-key-kept-on-the-server"


def _b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

def _b64url_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))

def _sign(signing_input: str, secret: bytes) -> str:
    return _b64url(hmac.new(secret, signing_input.encode(), hashlib.sha256).digest())


def encode_jwt(claims: dict, secret: bytes = SECRET) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    h = _b64url(json.dumps(header, separators=(",", ":")).encode())
    p = _b64url(json.dumps(claims, separators=(",", ":")).encode())
    return f"{h}.{p}.{_sign(f'{h}.{p}', secret)}"


class InvalidToken(Exception):
    pass

def decode_jwt(token: str, secret: bytes = SECRET) -> dict:
    try:
        h, p, sig = token.split(".")
    except ValueError:
        raise InvalidToken("malformed")
    expected = _sign(f"{h}.{p}", secret)
    if not hmac.compare_digest(expected, sig):        # the seal must match
        raise InvalidToken("bad signature")
    claims = json.loads(_b64url_decode(p))
    if "exp" in claims and claims["exp"] < time.time():
        raise InvalidToken("expired")
    return claims


# ─────────────────────────── the tests ───────────────────────────

def test_a_valid_token_round_trips():
    token = encode_jwt({"sub": "42", "role": "admin"})
    assert decode_jwt(token) == {"sub": "42", "role": "admin"}
    assert token.count(".") == 2                       # header.payload.signature

def test_anyone_can_read_the_payload_without_the_secret():
    # "signed, NOT encrypted" — never put a secret in a JWT payload
    token = encode_jwt({"sub": "42", "card": "DO-NOT-DO-THIS"})
    _, payload_b64, _ = token.split(".")
    leaked = json.loads(_b64url_decode(payload_b64))   # no secret used at all
    assert leaked["card"] == "DO-NOT-DO-THIS"

def test_tampering_with_the_payload_is_rejected():
    token = encode_jwt({"sub": "42", "role": "user"})
    h, p, sig = token.split(".")
    forged_p = _b64url(json.dumps({"sub": "42", "role": "admin"},
                                  separators=(",", ":")).encode())
    with pytest.raises(InvalidToken):                  # signature no longer matches
        decode_jwt(f"{h}.{forged_p}.{sig}")

def test_a_token_signed_with_another_secret_is_rejected():
    token = encode_jwt({"sub": "42"}, secret=b"attacker-secret")
    with pytest.raises(InvalidToken):
        decode_jwt(token, secret=SECRET)

def test_an_expired_token_is_rejected():
    token = encode_jwt({"sub": "42", "exp": time.time() - 1})   # already expired
    with pytest.raises(InvalidToken):
        decode_jwt(token)

def test_a_future_expiry_is_accepted():
    token = encode_jwt({"sub": "42", "exp": time.time() + 3600})
    assert decode_jwt(token)["sub"] == "42"


if __name__ == "__main__":
    try:
        import pytest as _pt
    except ImportError:
        raise SystemExit("This is a pytest test file. Install pytest first:  pip install pytest")
    raise SystemExit(_pt.main([__file__, "-v", "-p", "no:cacheprovider"]))
