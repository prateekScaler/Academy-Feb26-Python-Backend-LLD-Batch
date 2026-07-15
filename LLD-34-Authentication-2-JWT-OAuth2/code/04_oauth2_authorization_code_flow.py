"""
OAuth 2 — "Login with Google" — demystified as a runnable simulation.
Stdlib only, zero installs, always green.

The one-sentence idea: OAuth lets a user grant App LIMITED access to their
data on a Provider (Google) WITHOUT giving App their Google password.
The valet-key analogy: you hand the valet a key that drives the car but
won't open the trunk or the glovebox.

Four roles:
    Resource Owner  — the user (owns the data)
    Client          — your app ("Login with Google" button)
    Auth Server     — Google's consent + token endpoint
    Resource Server — Google's API holding the user's profile

We simulate the Authorization Code flow WITH PKCE (the flow every modern
web/mobile app should use). Run it live at:
    https://developers.google.com/oauthplayground
    https://www.oauth.com/playground/
"""
import base64
import hashlib
import secrets

import pytest


class Provider:
    """A toy Google: issues auth codes after consent, swaps them for tokens."""

    def __init__(self):
        self._registered = {}     # client_id -> redirect_uri
        self._codes = {}          # code -> {user, challenge, redirect}
        self._tokens = {}         # access_token -> user
        self.users = {"alice": {"name": "Alice", "email": "alice@gmail.com"}}

    def register_app(self, redirect_uri: str) -> str:
        client_id = "client_" + secrets.token_hex(4)
        self._registered[client_id] = redirect_uri
        return client_id

    # Step A: user consents at the provider; provider returns a short-lived CODE
    def authorize(self, client_id, redirect_uri, user, code_challenge, scope):
        assert self._registered.get(client_id) == redirect_uri, "redirect mismatch"
        assert "profile" in scope, "user must consent to the requested scope"
        code = secrets.token_urlsafe(16)
        self._codes[code] = {"user": user, "challenge": code_challenge,
                             "redirect": redirect_uri}
        return code

    # Step B: app swaps CODE + verifier for an ACCESS TOKEN (back-channel)
    def exchange(self, client_id, code, code_verifier, redirect_uri):
        rec = self._codes.pop(code, None)          # codes are single-use
        if rec is None:
            raise ValueError("invalid or already-used code")
        if rec["redirect"] != redirect_uri:
            raise ValueError("redirect_uri mismatch")
        # PKCE proof: SHA256(verifier) must equal the challenge sent in step A
        expected = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()).rstrip(b"=").decode()
        if expected != rec["challenge"]:
            raise ValueError("PKCE verification failed — code was intercepted")
        token = secrets.token_urlsafe(24)
        self._tokens[token] = rec["user"]
        return token

    # Step C: app calls the API with the token to read ONLY the granted data
    def userinfo(self, access_token):
        user = self._tokens.get(access_token)
        if user is None:
            raise ValueError("invalid access token")
        return self.users[user]


def login_with_google(provider: Provider, redirect_uri="https://app.example/cb"):
    """The client side of the dance, end to end."""
    client_id = provider.register_app(redirect_uri)
    # PKCE: make a secret verifier, send only its hash (the challenge)
    verifier = secrets.token_urlsafe(32)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    code = provider.authorize(client_id, redirect_uri, "alice", challenge, ["profile"])
    token = provider.exchange(client_id, code, verifier, redirect_uri)
    return provider.userinfo(token)


# ── the flow works, and the app never sees the password ─────────────────────

def test_login_with_google_returns_profile_without_a_password():
    provider = Provider()
    profile = login_with_google(provider)
    assert profile == {"name": "Alice", "email": "alice@gmail.com"}
    # Note: nowhere did the app receive Alice's Google password. That's OAuth.


def test_only_the_consented_scope_is_reachable():
    provider = Provider()
    client_id = provider.register_app("https://app.example/cb")
    with pytest.raises(AssertionError, match="consent"):
        provider.authorize(client_id, "https://app.example/cb", "alice",
                           "x", scope=["nothing"])   # user didn't grant profile


# ── the attacks the flow defends against ────────────────────────────────────

def test_authorization_code_is_single_use():
    provider = Provider()
    client_id = provider.register_app("https://app.example/cb")
    verifier = secrets.token_urlsafe(32)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    code = provider.authorize(client_id, "https://app.example/cb", "alice",
                             challenge, ["profile"])
    provider.exchange(client_id, code, verifier, "https://app.example/cb")
    with pytest.raises(ValueError, match="already-used"):
        provider.exchange(client_id, code, verifier, "https://app.example/cb")


def test_pkce_blocks_a_stolen_code():
    """An attacker who intercepts the code still can't use it — they don't
    have the verifier, and SHA256(theirs) won't match the challenge."""
    provider = Provider()
    client_id = provider.register_app("https://app.example/cb")
    verifier = secrets.token_urlsafe(32)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    code = provider.authorize(client_id, "https://app.example/cb", "alice",
                             challenge, ["profile"])
    with pytest.raises(ValueError, match="PKCE"):
        provider.exchange(client_id, code, "attacker-guessed-verifier",
                         "https://app.example/cb")
