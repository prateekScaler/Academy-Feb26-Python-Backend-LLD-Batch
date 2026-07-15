# LLD-34 — Authentication, Part 2: bcrypt & argon2, Tokens, JWT/JWS & OAuth 2

> **Module 4, session 4.** Part 1 taught us to *store* the secret. Part 2 teaches us to *carry* identity. We finish the password story with the real libraries (**bcrypt**, **argon2**), then learn how a server keeps you logged in — **sessions vs tokens**, **JWT/JWS** in depth — and finally **OAuth 2**, so an app can act on your behalf without ever seeing your password.

**How to use this class:** open `index.html` for the interactive page (a recap of the hash/salt debate, then bcrypt → argon2 → tokens → JWT → OAuth, with diagrams, discussion-first questions, and a live demo server). This README is the same content in prose. Every section names the code file to run; all examples live in [`code/`](code/README.md).

Each concept section opens with a **"📁 Code for this section"** pointer, and every quiz/answer is paired with a small diagram.

---

## Recap — the hash + salt debate (Part 1)
Five questions settle Part 1 before we add anything: hashing is **one-way** (a *Forgot Password* flow must set a *new* password, never recover the old); **no salt → identical passwords share a hash** (rainbow-tableable); **salt is public**, stored next to the hash (its job is uniqueness, not secrecy); a **pepper** is salt's *secret* sibling (one site-wide secret kept *outside* the DB, so a database-only leak is useless); and salt kills *tables* while a **slow hash** kills *brute force* — you need both. API keys get **encrypted** (you must use them back), passwords get **hashed** (you only compare).

## bcrypt, properly — `code/01_bcrypt_properly.py`
The real library: `bcrypt.hashpw(pw.encode(), bcrypt.gensalt(rounds=12))` at signup, `bcrypt.checkpw(attempt.encode(), stored)` at login — there is no `decrypt`.
- **Anatomy** of the hash string `$2b$12$<22-char salt><31-char hash>`: version, cost, salt, and hash all live inside it, so no separate salt column, and you can raise the cost for new users without touching old rows.
- **`.encode()`** is Python str→UTF-8 *bytes* (bcrypt hashes bytes, not text) — *not* the encoding-vs-encryption "encode". It's also where the **72-byte cap** is counted (accents/emoji are multiple bytes).
- **Cost factor**: `rounds=12` = 2¹² = 4,096 internal iterations (~0.3 s). Each **+1 doubles** the time — adaptive security: bump one integer as hardware improves. A signup/login flow diagram shows the salt+cost being read back out of the stored string at verify time.
- Live: [bcrypt-generator.com](https://bcrypt-generator.com/).

## scrypt & argon2 — `code/02_argon2_and_the_family.py`
bcrypt only makes the **CPU** work; a GPU has thousands of cores. The counter is **memory-hardness** — make each guess also eat RAM.
- The family: **PBKDF2** (CPU) · **bcrypt** (CPU) · **scrypt** (CPU + memory, in the stdlib) · **argon2id** (CPU + memory + parallelism; 2015 PHC winner, **OWASP's first pick**).
- argon2's three knobs, `$argon2id$v=19$m=65536,t=3,p=4$…`: **t** = passes (time), **m** = RAM to fill (the *space cost* bcrypt lacks), **p** = parallel lanes. An attacker running 10,000 guesses at once needs 10,000 × 64 MiB ≈ 640 GiB — no GPU has that.
- **Reading `m`:** it's in **KiB** (1 KiB = 1024 bytes; 1 MiB = 1024 KiB — the "i" means binary). Divide by 1024 → `m=65536` = **64 MiB**. (19456 = 19 MiB OWASP min; 1048576 = 1 GiB.)
- `check_needs_rehash` upgrades old hashes on next login. Rule of thumb: **new project → argon2id; already on bcrypt → fine, keep the cost current.** Live: [argon2.online](https://argon2.online/).

## What is a token, really? — `code/demo_server.py`
HTTP is **stateless** — each request arrives cold. After login the server hands you a **token** you attach to every later request to prove "I'm already authenticated." Two families:
- **Stateful (session):** the server stores the truth (a session row) and gives you an **opaque id**, usually in a **cookie**; every request is a lookup. Logout = delete the row → *instant* revocation.
- **Stateless (JWT):** the **token itself** carries the signed claims; the server stores nothing, just verifies the signature.

**Cookie vs session vs token:** a **cookie** is *transport* (a header the browser auto-resends); a **session id** and a **JWT** are both **tokens**. *"Are session cookies tokens?"* — yes: the session id is a bearer token; the cookie is just the envelope. Don't compare "cookies vs tokens."

**Session auth, start to finish:** one `Set-Cookie: sid=abc123; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=3600` at login; the browser then auto-sends `Cookie: sid=abc123`. The flags: **HttpOnly** (JS can't read it → anti-XSS), **Secure** (HTTPS-only → anti-sniff), **SameSite** (not on cross-site POSTs → anti-CSRF), **Path**, **Max-Age**. Find them in DevTools: Application → Cookies, Network → Headers, Console → `document.cookie` (where `sid` is *missing* because it's HttpOnly).

**In Django:** keep `SessionMiddleware` then `AuthenticationMiddleware`; `migrate` creates `django_session`; `login(request, user)` sets the row + cookie; `@login_required` (or DRF `SessionAuthentication` + `IsAuthenticated`) protects views; `logout(request)` revokes; harden with `SESSION_COOKIE_HTTPONLY/SECURE/SAMESITE/AGE`. *(This is a homework task.)*

Run `python3 code/demo_server.py` → open localhost:8034 to log in via session (cookie + server store) and JWT (nothing stored), and tamper a token to see verification fail.

## JWT / JWS in depth — `code/03_jwt_and_jws_deep.py`
**Why stateless?** With sessions on many servers behind a load balancer, every server must hit a **shared session store** on every request — a bottleneck + single point of failure. A **stateless** token is verified locally with just the secret → scales freely; ideal for microservices and mobile/third-party APIs. The price: revocation is hard (you can't un-issue what you don't store).

**Which to use?** A click-to-reveal table maps scenarios: single server / instant "log-out-everywhere" / bank → **session**; many servers, microservices, mobile/SPA, Login-with-Google → **JWT**. Most big apps go **hybrid** (a short-lived JWT access token + a refresh token / `token_version` for revocation).

**Anatomy:** `header.payload.signature`, all base64url. **What's the algorithm?** header & payload → **base64url ENCODING** (readable by anyone, not security); signature → **HMAC-SHA256, a keyed HASH** (one-way). A JWS is **encoding + hashing, zero encryption** — which is exactly why the payload is public. **Signed, not encrypted → never put a secret in it.**
- **Claims:** `sub` (who), `exp` (expiry — bounds a leak), `iat`, `nbf`, `iss`/`aud` (reject tokens for another service).
- **Attacks:** `alg:none` (pin the algorithm server-side) and HS/RS confusion (never make symmetric/asymmetric verification interchangeable).
- **Access + refresh** tokens answer "JWTs are hard to revoke." Live: [jwt.io](https://jwt.io/).

## OAuth 2 — `code/04_oauth2_authorization_code_flow.py`
**Why it exists:** in the 2005–07 "dark ages," an app that wanted your contacts asked for your actual email **password** and logged in *as you* — total access, no revocation. OAuth replaces that with a **scoped, revocable token**: prove yourself to the provider, and it hands the app just enough. Real examples: **CRED** (read statements only), **INDmoney** (read portfolio only), **Buffer** (post tweets, not read DMs).
- **History:** 2006 (Twitter's need) → **OAuth 1.0** (2007, per-request signatures, hard) → **OAuth 2.0** (2012, RFC 6749, bearer tokens over TLS) → **OIDC** (2014, adds an **ID token = a JWT** so "Login with Google" is a *login*).
- **Four roles:** Resource Owner (you), Client (the app), Authorization Server (Google's consent/token endpoints), Resource Server (Google's API).
- **Authorization Code + PKCE flow:** redirect with `client_id`/`scope`/PKCE challenge → you consent → short-lived **code** → app swaps code + verifier for an **access token** (back-channel) → app calls the API. PKCE makes a stolen code useless without the verifier. Live: [OAuth Playground](https://www.oauth.com/playground/).

---

## The `code/` folder
Pure pytest; the JWT & OAuth files are **stdlib-only** and always green; the bcrypt & argon2 files use the real libraries and **skip politely** if they're not installed.

| File | Concept | Live tool |
|---|---|---|
| `demo_server.py` | live browser demo — session vs JWT (`python3 demo_server.py`) | localhost:8034 |
| `01_bcrypt_properly.py` | bcrypt anatomy, cost curve, 72-byte cap | bcrypt-generator.com |
| `02_argon2_and_the_family.py` | scrypt (stdlib) + argon2id, memory-hardness, rehash | argon2.online |
| `03_jwt_and_jws_deep.py` | JWS build/verify, tamper, `alg=none`, expiry | jwt.io |
| `04_oauth2_authorization_code_flow.py` | login-with-Google + PKCE, simulated | oauth.com/playground |
| `08_homework.py` | 9 `pytest.skip` stubs to turn green | — |

```bash
pip install pytest                 # required for the test files
pip install bcrypt argon2-cffi     # optional — unlocks files 01 & 02
pytest -q 0*.py                    # run the suites (name files explicitly — they're numbered)
python3 demo_server.py             # the live demo — no installs
```

## Homework
1. **`code/08_homework.py`** — 9 stubs across JWT (roundtrip / readable / tamper / expiry / wrong-secret), bcrypt anatomy, argon2 verify, and PKCE. Turn them all green.
2. **Session auth in Django** — build a tiny app with `login` / `me` (`@login_required`) / `logout`; watch the `sessionid` cookie appear/vanish in DevTools; set the `SESSION_COOKIE_*` flags; test with `APIClient`.
3. Swap your Part-1 password code to **argon2** (`argon2-cffi`) with `check_needs_rehash`.
4. Decode one of your app's JWTs at [jwt.io](https://jwt.io); confirm the payload is readable.
5. *Stretch:* walk the [OAuth Playground](https://www.oauth.com/playground/) and note where the code, verifier, and token each appear.

**Next class — Authentication-3:** put it together — build a real **User Service** (register / login / me), issue access + refresh tokens, wire RBAC, tested with LLD-31/32.
