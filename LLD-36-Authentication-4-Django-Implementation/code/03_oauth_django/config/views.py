"""
"Login with Google" done BY HAND with `requests`, so every step of the
OAuth 2.0 Authorization Code flow (with PKCE) is visible.

The big idea
------------
Our app wants to know who the user is. It must NOT ask for their Google
password. So instead we bounce the user's browser over to Google, Google
authenticates them, and Google hands us back a short-lived "code" that proves
"yes, this person logged in and agreed to share their profile with you".

The five steps, mapped to the code below:

    1. login_google      : we build an authorize URL and REDIRECT the browser
                           to Google (front channel - travels through the user).
    2. (at Google)       : user logs in + clicks "Allow". We never see this.
    3. oauth_callback    : Google redirects the browser back to us with
                           ?code=...&state=...
    4. oauth_callback    : our SERVER POSTs that code (+ the PKCE verifier +
                           our client secret) to Google's token endpoint and
                           gets an access_token (back channel - server to
                           server, the browser never sees this request).
    5. oauth_callback    : our server calls the userinfo endpoint with that
                           token and learns the user's name/email/picture.

Two security ideas you should be able to explain after reading this file:

    * PKCE  - "Proof Key for Code Exchange". We invent a random secret
              (code_verifier), send only its SHA-256 HASH (code_challenge) to
              Google up front, and reveal the original secret only in the
              back-channel token request. If an attacker steals the `code`
              from the redirect URL, it is useless to them: they cannot
              produce the verifier that hashes to the challenge Google stored.

    * state - a random value we send to Google and get back unchanged. On the
              callback we check it matches what we saved in the session. This
              proves the callback belongs to a flow WE started, and stops an
              attacker from feeding us their own code (login CSRF).
"""

import base64
import hashlib
import secrets
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render


def home(request):
    """
    The only page. If `user` is in the session we are "logged in";
    if not, we show the Login with Google button.

    Note the session is our whole notion of a login here - deliberately
    simple so the OAuth part stays in focus.
    """
    return render(
        request,
        "home.html",
        {
            "user": request.session.get("user"),
            # Classroom-only: the PKCE values from the login that just happened,
            # so the page can show them. See login_google / oauth_callback.
            "pkce": request.session.get("pkce_trace"),
        },
    )


def login_google(request):
    """
    STEP 1 - send the user to Google.

    We do not call Google here. We build a URL and tell the BROWSER to go
    there. That matters: only the browser (and therefore only Google) ever
    handles the password.
    """

    # --- PKCE part A: invent a secret -------------------------------------
    # code_verifier is a high-entropy random string. It stays on our server
    # (in the session). It is the "proof" we will show later.
    verifier = secrets.token_urlsafe(32)

    # --- PKCE part B: hash it --------------------------------------------
    # code_challenge = BASE64URL( SHA256( verifier ) ), with the '=' padding
    # stripped. This is what RFC 7636 calls the "S256" method.
    # Only the HASH travels through the browser, so seeing it tells an
    # attacker nothing useful - hashes are one-way.
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        .rstrip(b"=")          # base64url for OAuth is UNPADDED - keep this!
        .decode()
    )

    # --- anti-CSRF: a random, unguessable round-trip value ----------------
    state = secrets.token_urlsafe(16)

    # Save BOTH on the server side. The callback will need them.
    # (This is exactly why SessionMiddleware is mandatory for this demo.)
    request.session["pkce_verifier"] = verifier
    request.session["oauth_state"] = state

    # DEMO ONLY. Keep a copy purely so home.html can print the verifier next to
    # the challenge after login. A real app never shows these to anyone.
    request.session["pkce_trace"] = {"verifier": verifier, "challenge": challenge}

    params = {
        # Who is asking. Public identifier of our app, issued by Google.
        "client_id": settings.GOOGLE_CLIENT_ID,
        # Where Google should send the browser back. Must match the value
        # registered in Google Cloud Console, character for character.
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        # We want the Authorization *Code* flow (not the old implicit flow).
        "response_type": "code",
        # What we are asking permission for. `openid email profile` = "tell me
        # who this is, their email, and their basic profile". Nothing more:
        # ask for the least you need.
        "scope": "openid email profile",
        # Comes back to us untouched in the callback -> we compare it.
        "state": state,
        # PKCE: the hash, and which hashing method we used.
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        # Ask for a refresh token too (Google only sends one on the first
        # consent). Not used in this demo, but shown so you know where it
        # would come from.
        "access_type": "offline",
        # Always show the account picker instead of silently reusing a
        # session. Very handy when demoing / switching test accounts.
        "prompt": "select_account",
    }

    url = f"{settings.GOOGLE_AUTH_URL}?{urlencode(params)}"

    # Look at this URL in your browser's address bar after clicking the
    # button - you can literally read every parameter above in it.
    return redirect(url)


def oauth_callback(request):
    """
    STEPS 3, 4, 5 - Google has sent the browser back to us.

    The URL looks like:
        /oauth/callback/?code=4%2F0Ab...&state=xYz...&scope=...
    """

    # Google reports user-facing problems (e.g. the user clicked "Cancel")
    # with an ?error= parameter rather than a code.
    if request.GET.get("error"):
        return _error_page(
            request,
            f"Google returned an error: {request.GET['error']}. "
            "The most common cause is clicking Cancel on the consent screen.",
        )

    code = request.GET.get("code")
    state = request.GET.get("state")

    # --- anti-CSRF check on the callback ---------------------------------
    # `state` must equal the value we generated in login_google and stored in
    # THIS user's session. If it does not match, this callback did not come
    # from a flow this browser started - someone is trying to log us in as
    # them (login CSRF). Refuse.
    # We pop() it so each state value is single-use.
    expected_state = request.session.pop("oauth_state", None)
    if not state or state != expected_state:
        return HttpResponseBadRequest(
            "Invalid OAuth state. This request did not come from a login "
            "flow started by this browser, so it was rejected."
        )

    # Pop the verifier too: one flow, one verifier.
    verifier = request.session.pop("pkce_verifier", None)
    if not code or not verifier:
        return _error_page(
            request,
            "Missing the authorization code or the PKCE verifier. "
            "Start again from the home page.",
        )

    try:
        # --- STEP 4: swap the code for a token (BACK CHANNEL) -------------
        # This is a server-to-server POST. The browser is not involved, so
        # the client_secret and the code_verifier never travel through it.
        token_response = requests.post(
            settings.GOOGLE_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                # The one-time code Google just gave us. Single use, expires
                # in minutes.
                "code": code,
                # Must match the redirect_uri used in step 1 - Google checks.
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                # PKCE proof: Google re-hashes this and compares it with the
                # code_challenge we sent in step 1. Mismatch -> rejected.
                "code_verifier": verifier,
            },
            timeout=10,
        )

        token_data = token_response.json()

        if token_response.status_code != 200 or "access_token" not in token_data:
            # Typical causes: placeholder client id/secret still in place,
            # or the redirect URI registered in Google Cloud Console does not
            # match GOOGLE_REDIRECT_URI exactly.
            return _error_page(
                request,
                "Google refused the token exchange: "
                f"{token_data.get('error_description') or token_data.get('error') or token_response.text}. "
                "Check GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET and that the "
                "Authorized redirect URI in Google Cloud Console is exactly "
                f"{settings.GOOGLE_REDIRECT_URI}",
            )

        access_token = token_data["access_token"]

        # --- STEP 5: use the token to read the profile --------------------
        # The token goes in the Authorization header as a Bearer token.
        # "Bearer" literally means: whoever holds this, gets access. Treat
        # tokens like passwords - never log them, never put them in URLs.
        userinfo_response = requests.get(
            settings.GOOGLE_USERINFO_URL,
            headers={"Authorization": "Bearer " + access_token},
            timeout=10,
        )

        if userinfo_response.status_code != 200:
            return _error_page(
                request,
                "Got a token, but the userinfo call failed: "
                f"{userinfo_response.text}",
            )

        profile = userinfo_response.json()

    except requests.RequestException as exc:
        # Network problems, DNS, timeouts, no internet in the classroom, ...
        return _error_page(request, f"Could not reach Google: {exc}")

    # Store just what we need. This session cookie is now the user's login.
    request.session["user"] = {
        "name": profile.get("name", ""),
        "email": profile.get("email", ""),
        "picture": profile.get("picture", ""),
    }

    # DEMO ONLY: record the code as well, so the page can show all three
    # values together - verifier, challenge, and the code that came back
    # through the address bar.
    trace = request.session.get("pkce_trace") or {}
    trace["code"] = code
    request.session["pkce_trace"] = trace

    # In a REAL app you would now map this Google account to a row in your
    # own users table (get_or_create by email or by the stable `sub` id) and
    # call django.contrib.auth.login(request, user) so that request.user and
    # @login_required work. We stop at the session dict to keep the OAuth
    # mechanics front and centre.

    return redirect("home")


def logout_view(request):
    """
    Log out locally: throw away the whole session (profile, and any leftover
    state/verifier). Note this does NOT log the user out of Google itself -
    it only ends their session with *our* app.
    """
    request.session.flush()
    return redirect("home")


def _error_page(request, message):
    """Small helper so configuration mistakes give a readable page, not a 500."""
    return render(request, "home.html", {"user": None, "error": message}, status=400)
