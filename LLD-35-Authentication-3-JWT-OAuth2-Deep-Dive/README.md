# LLD-35 — Authentication, Part 3: JWT/JWS in Depth & OAuth 2

> **Module 4, session 5.** You can store a password (Auth-1/2) and keep a session (Auth-2). Today identity goes **stateless** — the JWT opened up bolt by bolt — and then **delegated**: OAuth 2, the "login with Google" dance. Next class assembles everything into a real User Service.

**How to use this class:** open `index.html` for the interactive page — a quick-fire **recap** of cookies/sessions, then **how a token travels**, then **JWT/JWS** and **OAuth 2** in depth. Every concept opens with a "Code for this section" pointer and pairs each question with a diagram. Today's runnable pytest suites live in [`../LLD-34-Authentication-2-JWT-OAuth2/code/`](../LLD-34-Authentication-2-JWT-OAuth2/code/); this folder adds two **open-in-a-browser security demos** ([`code/`](code/README.md)).

---

## Recap — cookies, sessions & the two token families
Quick-fire questions on what last class actually covered, then deeper:
- **The deploy that logged everyone out** — in-memory *stateful* sessions die with the process; a JWT would survive. (Precise nuance: Django's default `sessionid` is a **random** key, *not* derived from `SECRET_KEY`, so rotating the key doesn't log those users out — only the `signed_cookies` backend does. The id itself is `get_random_string(32, a-z0-9)` via `secrets.choice`; it's neither encoded nor encrypted, just a random pointer.)
- **What the browser sends back** — only `name=value` (e.g. `Cookie: sid=abc123`); the flags (`HttpOnly`, `Secure`, `SameSite`, `Max-Age`) are server-set *directives* the browser never echoes.
- **The flags, under fire** — three production incidents: dropping `HttpOnly` ("JS needs to read login state" — never; use `/me`), `Secure` on hotel wifi (the browser *withholds* the cookie on `http://`), and `SameSite=Strict` support tickets ("email links land logged out" — **Lax** is the balance).
- **HTTP vs HTTPS ELI5** — postcard vs sealed envelope; the TLS handshake (cert + CA + Let's Encrypt, key exchange, encrypted traffic); nuances (`localhost` treated as secure, **mkcert** for local HTTPS, HSTS, mixed-content). *Real world:* ~95% of Chrome page loads are HTTPS; Let's Encrypt has issued billions of certs.
- **`SameSite` Strict/Lax/None** — precise semantics + plain-word bank/Stripe-iframe examples. *Real world:* Chrome 80 (2020) made `Lax` the default for billions of users.
- **XSS demo** — [`code/xss_demo.html`](code/xss_demo.html): render user text unsafe (`innerHTML` → payload fires) vs safe (`textContent`), and how `HttpOnly` keeps the cookie out of a stolen `document.cookie`.
- **Stateful vs stateless scenario table** — session vs JWT, row by row, ending in the hybrid (short JWT access + refresh token).

## Sending the token — cookie vs header (and mobile)
- **In a Cookie** — the browser attaches it automatically; harden with `HttpOnly + Secure + SameSite`. CSRF-exposed, XSS-safe (if HttpOnly). Default for server-rendered web.
- **In an `Authorization: Bearer` header** — your code attaches it by hand. CSRF-**immune** (never auto-sent), but XSS-exposed if kept in `localStorage`. The norm for APIs, SPAs, mobile.
- **CSRF, demystified** — the browser auto-attaches your cookie even to a request `evil.com` triggered, so a hidden form there can POST to your bank as you. Defences: `SameSite` / CSRF token / Bearer header. Live: [`code/csrf_demo.html`](code/csrf_demo.html) — a simulated bank + evil.com auto-form + a defence selector.
- **Mobile** — native apps don't use cookies; they store the token in **iOS Keychain / Android Keystore** and send it as Bearer.
- Best-practice for web SPAs: short-lived access token in memory + refresh token in an `HttpOnly+Secure+SameSite` cookie.

## JWT / JWS in depth
- **Why stateless** — five servers behind a load balancer + sessions = a shared session store hit on every request (bottleneck). A stateless token verifies **locally** with just the secret → scales freely; ideal for microservices and mobile.
- **Life of a JWT** — *generate* (server signs the payload at login), *send & store* (cookie or Bearer), *verify* (server re-signs, compares, checks `exp`) — each step with a short code snippet.
- **The algorithm** — header & payload are base64url **ENCODING**; the signature is **HMAC-SHA256, a keyed HASH**. A JWS is *encoding + hashing, zero encryption* → readable payload, tamper-proof, **never put a secret in it**.
- **Claims** — `sub`, `exp`, `iat`, `nbf`, `iss`/`aud`.
- **`alg:none` attack** — a live story: edit `role→admin` (signature breaks), then set `alg:none` to try to skip the check; watch it fail on [jwt.io](https://jwt.io/). Defence: pin the algorithm.
- **HS256 vs RS256** — a key diagram: HS256 = one shared secret (sign & verify); RS256 = **private key signs** (issuer only), **public key verifies** (anyone, can't forge). The confusion attack abuses a naive server into using the public key as an HMAC secret.
- **Access + refresh** — a user-journey diagram (login → use → expire → silent refresh → …; refresh dies in days → re-login) and how it restores revocation. *Real world:* GitHub ~8h/6mo, Google 1h, AWS STS 15min–12h.

## OAuth 2 — access without the password
- **Why it exists** — opens with an intrigue quiz (2005 photo-printing site asking for your Facebook password) — the word "OAuth" only appears in the reveal. Then old-way-vs-OAuth-way as a spaced flow, and real apps (CRED, INDmoney, Buffer).
- **History** — 2006 Twitter → **OAuth 1.0** (2007, signatures) → **OAuth 2.0** (2012, RFC 6749, bearer tokens) → **OIDC** (2014, an ID token = a JWT). *Real world:* OAuth 2.0 underpins every "Sign in with…"; PKCE (RFC 7636) is now recommended for all clients in OAuth 2.1.
- **Four players** — Resource Owner (you), Client (the app), Authorization Server (Google's consent/token), Resource Server (Google's API).
- **The Authorization Code + PKCE flow** — built one arrow at a time (a sequence diagram that grows per step), each with an example request (`client_id`, `scope`, `code_challenge`, `code`, `verifier`, token). PKCE makes a stolen code useless.
- **Play with it** — step-by-step guides for [oauth.com/playground](https://www.oauth.com/playground/) and [Google's real playground](https://developers.google.com/oauthplayground).

---

## `code/` — two hands-on demos
| File | What it shows |
|---|---|
| [`xss_demo.html`](code/xss_demo.html) | Cross-Site Scripting: unsafe `innerHTML` vs safe `textContent`, and how `HttpOnly` blocks cookie theft. Double-click to open — all local, `alert()` only. |
| [`csrf_demo.html`](code/csrf_demo.html) | Cross-Site Request Forgery: a simulated bank + evil.com auto-form + a defence selector (None / SameSite / CSRF token / Bearer). Watch ₹5,000 get stolen, then blocked. |

The runnable **pytest** suites for today (`03_jwt_and_jws_deep.py`, `04_oauth2_authorization_code_flow.py`, `demo_server.py`, `08_homework.py`) live in `../LLD-34-Authentication-2-JWT-OAuth2/code/` — stdlib-only, always green.

## Homework
1. Finish the **JWT + PKCE stubs** in `../LLD-34-Authentication-2-JWT-OAuth2/code/08_homework.py`.
2. **Battle-test:** [hackattic — Jotting JWTs](https://hackattic.com/challenges/jotting_jwts).
3. Decode one of your own app's JWTs at [jwt.io](https://jwt.io); confirm the payload is readable.
4. Walk the OAuth Playground end to end; note where the code, verifier, and token appear.
5. *Stretch:* add JWT auth to a Django endpoint with `djangorestframework-simplejwt`.

**Next class — Authentication-4:** build the real **User Service** — register (argon2/bcrypt), login (issue access + refresh JWTs), `/me`, RBAC — tested with the LLD-31/32 toolkit.
