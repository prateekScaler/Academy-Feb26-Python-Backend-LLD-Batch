# LLD-36 — Authentication, Part 4: Implementing Auth in Django

> **Module 4, session 6 — the finale of the auth arc.** You know the theory; now you wire it up. We open with **when a JWT helps and when it hurts**, then the browser-security trio every real app hits (**CORS, CSRF, SameSite**) plus what an **`Authorization: Bearer`** header actually is, then **OAuth** made intuitive with the **OIDC** and **SSO** pieces that sit on top — and each topic is followed *immediately* by the runnable **Django** demo that builds it.

**How to use this class:** open `index.html` for the interactive page. Everything is beginner-first, with diagrams, scenario questions, and step-by-step Django. Theory and hands-on are interleaved: each concept is followed by the exact commands to demo it live. Three **runnable Django projects** live in [`code/`](code/) — each with its own README (exact `pip install` / `migrate` / `runserver` steps).

---

## CORS, CSRF & the SameSite flag — untangled
The three things beginners mix up, pulled apart:
- **Origin** = scheme + host + port. Change any one → different origin (that's what triggers CORS).
- **CORS** answers *"who may READ my API's response?"* Your React app at `:3000` calling your Django API at `:8000` is cross-origin — the request still *runs* on the server, but the **browser** refuses to hand the response to the app's JS unless the API allows that origin (`Access-Control-Allow-Origin`). It is **not** a server-side guard (curl ignores CORS).
- **CSRF** is the opposite worry: the browser auto-attaches your cookie to *any* request to a site, so a hidden form on `evil.com` can make your browser POST to your bank *as you*.
- **The picture to remember:** CORS guards *reading* your data from another origin; CSRF abuses your cookie being *sent* from another origin. Opposite directions — which is why they're confused. Fix CSRF with **SameSite** (modern) or a **CSRF token** (classic).
- **SameSite** — `Lax` (default: cookie rides on links you click, not background cross-site POSTs), `Strict` (never cross-site), `None` (everywhere, needs `Secure`). The page has a *when-to-use-which* table for the three values.
- **Middleware, from scratch** — what `CorsMiddleware` (from `django-cors-headers`) and the built-in `CsrfViewMiddleware` each do, and *why* `CorsMiddleware` must sit near the top of `MIDDLEWARE` (it has to stamp `Allow-Origin` before a lower middleware can short-circuit the response).

## `Authorization: Bearer` — what it actually is
- **One header, two parts** — `Authorization: <scheme> <credential>`. The scheme word (`Bearer`) tells the server how to read what follows; the credential is your token (a JWT or an opaque id).
- **Why "Bearer"** — it works like cash or a cinema ticket: whoever *bears* it gets in. Possession is the proof — which is also why a stolen bearer token works for the thief until it expires (so: short-lived, HTTPS-only).
- **Bearer ≠ the token, Bearer ≠ JWT** — `Bearer` is just the scheme label; an opaque token can follow it too. Other schemes you'll meet: `Basic` (base64 `user:pass`, not encryption), `Digest` (legacy), and API-keys in a custom header (`X-API-Key`).
- **Where it's stored** — unlike a cookie the browser auto-attaches, *your code* stores and sends a bearer token (memory / `localStorage` / `sessionStorage`; OS keychain on mobile). Trade-off: CSRF-immune (nothing auto-sends it) but XSS-exposed — the mirror image of an `HttpOnly` cookie. The page shows how to locate it live in DevTools → Network → Request Headers.

## OAuth 2, the intuitive way
- **The valet key** — OAuth lets an app do *one limited thing* with your data without your *real* key (your password), and you can revoke it anytime.
- **The problem it kills** — before OAuth, apps asked you to type your Google password *into the app*; now the app never sees it.
- **Four players** — You, the App, Google (auth server), Google's API.
- **The dance, as a story** — the app sends you to Google → you log in and consent *at Google* → Google hands the app a short-lived **code** it swaps for a scoped **access token** → the app reads only what you allowed. (Built up one arrow at a time on the page.)
- **Three words** — *scope* (what it may touch), *consent* (your yes), *redirect URI* (the one pre-registered address the code returns to). Plus `state` (anti-CSRF on the callback) and `PKCE` (a stolen code is useless).
- **The callback, ELI5** — the redirect URI is an address on *your own* app that Google calls you back at, carrying `?code=&state=`. Your callback view reads it, verifies `state`, swaps the code for a token, and logs the user in. It's pre-registered so an attacker can't point the code at `evil.com`.
- **PKCE, ELI5** — your app keeps a secret **verifier** and sends only its hash, the **challenge**, up front. At the token swap it must present the verifier; Google re-hashes and compares. A thief with only the code can't reverse the challenge → the stolen code is useless. *(Like mailing a photo of your padlock ahead, while only you hold the key.)*

## OIDC vs OAuth 2 — the confusion, cleared
- **One line** — OAuth 2 answers *"what may this app **do**?"* (authori**z**ation). OpenID Connect answers *"**who** is this user?"* (authe**n**tication). OIDC isn't a rival — it's a thin identity layer *on top of* OAuth 2.
- **Why it appeared** — OAuth 2 (2012) was built for authorization only. Apps faked login on top of it, but an access token doesn't prove *identity*, which caused real bugs. **OIDC (2014)** standardized it: ask for `scope=openid` and you also get an **`id_token`** (a signed JWT with `sub`/`iss`/`aud`/`exp`) plus a standard `/userinfo`.
- **The classic bug** — using an *access* token as proof of identity. For login, verify the `id_token`'s signature, `iss`, and `aud`.

## SSO (Single Sign-On) — log in once, use everything
- **The trick** — one central **Identity Provider (IdP)** holds your login. The first app redirects you there, you log in once, and the IdP keeps a session cookie *on its own domain*. Every app after that redirects to the IdP too — but it already has your session, so it issues a token **silently, no second login**.
- **How it's built** — **OIDC** (`id_token` JWTs, consumer web/mobile) or **SAML 2.0** (XML assertions, enterprise). Same idea, different envelope.
- **Trade-off** — convenient and centrally controllable (disable the account → locked out everywhere), but the IdP is a **single point of failure**, so it gets hardened hard (MFA, monitoring).

## JWT — when it shines, when it bites
Scenario judgment (good fit or about to hurt?):
- ✅ **Stateless REST API for mobile/SPA** — Bearer header, verify anywhere. JWT's home turf.
- ✅ **Microservices verifying independently** — sign with a private key, verify with the public key offline, no shared store.
- ⚠️ **Instant "log out everywhere"** — a stateless JWT can't be un-issued; use sessions, or short access + refresh with a denylist / `token_version`.
- ❌ **Big/secret data in the payload** — it's public (base64) and re-sent every request; keep a small `sub` and fetch server-side.
- ❌ **Token in `localStorage`** — any XSS reads it; prefer an `HttpOnly` cookie or in-memory + refresh cookie.
- ❌ **No `exp`** — a stolen token is valid forever.

## Wire it up in Django
On the page, each demo sits **right after its own theory** (no separate "Django" chapter): the CORS/CSRF and JWT/Bearer builds follow the browser-security section, and the "Login with Google" build follows the OAuth section. Full runnable projects in `code/`:
1. **CORS/CSRF** — `django-cors-headers` (`CorsMiddleware` high in `MIDDLEWARE`, `CORS_ALLOWED_ORIGINS`), `{% csrf_token %}` in forms / `X-CSRFToken` header for fetch, `SESSION_COOKIE_HTTPONLY/SAMESITE/SECURE`.
2. **JWT** — DRF + `djangorestframework-simplejwt`: `JWTAuthentication`, `SIMPLE_JWT` lifetimes, `TokenObtainPairView` / `TokenRefreshView`, protect with `IsAuthenticated`.
3. **Login with Google** — get a Google OAuth client, build the authorize URL with a PKCE challenge + `state`, handle the callback (verify state, swap `code` + `verifier` for a token, call userinfo). *For production, use `django-allauth`.*

---

## `code/` — three runnable Django projects

Each is a minimal, self-contained Django 5 project with a beginner README. All three pass `manage.py check`; the JWT and CORS/CSRF flows were smoke-tested end to end.

Each project runs on **its own port**, so all three can stay up side by side during class — no "port already in use" mid-demo. A bare `python manage.py runserver` already picks the right one (each `manage.py` sets its own `DEFAULT_PORT`), so there is no port to type or remember.

| Project | Port | Demonstrates | Run |
|---|---|---|---|
| [`01_cors_csrf_django/`](code/01_cors_csrf_django/) | **8001** | A CSRF-protected form (`POST` without the token → **403**), a CORS-enabled JSON API for cross-origin fetch, and hardened `SameSite`/`HttpOnly` cookies | `pip install -r requirements.txt` → `migrate` → `runserver` → http://127.0.0.1:8001/ |
| [`02_jwt_django/`](code/02_jwt_django/) | **8002** | DRF + SimpleJWT: register → `POST /api/token/` (access + refresh) → protected `GET /api/me/` with `Bearer` (401 without it) → `/api/token/refresh/` | `migrate` → `runserver` + the copy-paste `curl` commands in its README |
| [`03_oauth_django/`](code/03_oauth_django/) | **8000** | "Login with Google" — the full Authorization Code + PKCE redirect → consent → callback flow, done manually with `requests` so every step is visible | needs Google OAuth creds (README has the Cloud Console steps) → `runserver` → click Login with Google |

> **Why 03 keeps 8000:** its redirect URI `http://127.0.0.1:8000/oauth/callback/` is what's registered in Google Cloud Console, and Google matches it character for character. Changing the port means adding the new URI in the Console first, or the login fails with `redirect_uri_mismatch`.

```bash
cd code/02_jwt_django
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Homework — run all three
1. **CORS/CSRF:** submit the form (token present → accepted); delete the hidden `csrfmiddlewaretoken` in DevTools → **403**; call `/api/ping/` from a page on another port → CORS block.
2. **JWT:** register, get a token, call `/api/me/` with and without `Bearer`, then refresh. Paste the access token into [jwt.io](https://jwt.io).
3. **OAuth:** run `03_oauth_django` with your own Google credentials and log in end to end.
4. *Stretch:* move `02_jwt_django`'s token to an `HttpOnly` cookie and add "logout everywhere" via `token_version`.

**Next class — Email Service & Message Queues:** auth is done; now we go *async* — producers, consumers, retries, and why you don't send email on the request thread.
