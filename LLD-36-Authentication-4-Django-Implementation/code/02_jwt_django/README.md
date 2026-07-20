# JWT Auth with Django + DRF + SimpleJWT

A tiny, runnable project that shows the complete JWT login flow:
**register → get tokens → call a protected endpoint → refresh the access token.**

Five endpoints, ~100 lines of our own code. Everything token-related is handled
by [`djangorestframework-simplejwt`](https://django-rest-framework-simplejwt.readthedocs.io/).

| Method | Endpoint              | Auth needed?     | What it does                          |
| ------ | --------------------- | ---------------- | ------------------------------------- |
| POST   | `/api/register/`      | no               | Creates a user                        |
| POST   | `/api/token/`         | no               | username+password → access + refresh  |
| POST   | `/api/token/refresh/` | refresh token    | → a fresh access token                |
| GET    | `/api/me/`            | **yes** (Bearer) | Returns the logged-in user            |
| GET    | `/api/public/`        | no               | Returns a message to anyone           |

---

## 1. Run it

From this directory (`02_jwt_django/`):

```bash
# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create the database tables (users, sessions, ...)
python manage.py migrate

# Start the dev server
python manage.py runserver
```

The server is now at **http://127.0.0.1:8002/**.

Leave it running and open a **second terminal** for the curl commands below.

---

## 2. Register a user

```bash
curl -X POST http://127.0.0.1:8002/api/register/ -H "Content-Type: application/json" -d '{"username":"alice","password":"secret123"}'
```

Response (`201 Created`):

```json
{"id": 1, "username": "alice"}
```

Notice there are **no tokens here**. Registering is not logging in — that's the
next step. (Run this command twice and the second one gives you
`400 {"error": "username already taken"}`.)

---

## 3. Log in — get your tokens

```bash
curl -X POST http://127.0.0.1:8002/api/token/ -H "Content-Type: application/json" -d '{"username":"alice","password":"secret123"}'
```

Response (`200 OK`) — two tokens, both long ugly strings:

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIs...",
  "access":  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwi..."
}
```

**Copy the `access` value.** You'll paste it into the next command. (Copy the
`refresh` one too — you'll need it in step 5.)

Try a wrong password and you get `401 {"detail": "No active account found with the given credentials"}`.

---

## 4. Call the protected endpoint

**Without a token — this fails:**

```bash
curl http://127.0.0.1:8002/api/me/
```

```json
{"detail": "Authentication credentials were not provided."}
```

That's a `401 Unauthorized`. Add `-i` to the curl command to see the status line.

**With the token — this works.** Replace `<ACCESS>` with the access token you
copied (the whole thing, no quotes, no line breaks):

```bash
curl http://127.0.0.1:8002/api/me/ -H "Authorization: Bearer <ACCESS>"
```

```json
{"id": 1, "username": "alice"}
```

For contrast, the public endpoint needs no header at all:

```bash
curl http://127.0.0.1:8002/api/public/
```

```json
{"message": "anyone can see this"}
```

> **Common mistakes:** the word must be `Bearer` (capital B, then a space).
> `Authorization: <ACCESS>` or `Authorization: Token <ACCESS>` both give you a
> 401 that looks identical to having no token at all.

---

## 5. Refresh — when the access token expires

Access tokens die after **15 minutes** (`ACCESS_TOKEN_LIFETIME` in
`config/settings.py`). After that, step 4 starts returning:

```json
{"detail": "Given token not valid for any token type", "code": "token_not_valid"}
```

The user should **not** have to type their password again. Instead the client
sends the refresh token:

```bash
curl -X POST http://127.0.0.1:8002/api/token/refresh/ -H "Content-Type: application/json" -d '{"refresh":"<REFRESH>"}'
```

```json
{
  "access":  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...new one...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...also new..."
}
```

You get a **new refresh token as well**, because `ROTATE_REFRESH_TOKENS = True`.
Your client must store the new one and discard the old.

> **Don't want to wait 15 minutes in class?** Set
> `ACCESS_TOKEN_LIFETIME = timedelta(seconds=10)` in `config/settings.py`,
> restart the server, and you can watch a token expire live.

---

## 6. Look inside the token

Copy an access token and paste it into **https://jwt.io**. You will see it split
into three dot-separated parts and decode into readable JSON:

```json
{"token_type": "access", "exp": 1735689600, "jti": "...", "user_id": 1}
```

Two things to take away from that:

1. **A JWT is signed, not encrypted.** Anyone holding the token can read what's
   inside it — it's just base64, not a secret. So never put a password, a card
   number, or anything private in a token payload.
2. **You still can't forge one.** The third part is a signature made with
   `SIGNING_KEY`. Edit `user_id` to `2` in jwt.io and send that token to
   `/api/me/` — you'll get a 401, because the signature no longer matches the
   payload. Only the server knows the key, so only the server can mint tokens.

---

## How this maps to the concepts

**Access token vs refresh token.**
Two tokens exist because they face opposite risks. The access token travels on
*every* request, so it leaks easily → keep it short-lived (15 min), and a stolen
one is near-worthless. The refresh token travels only to `/api/token/refresh/`,
so it's rarely exposed → it can live for days and spare the user from logging in
constantly. Short-and-noisy vs long-and-quiet.

**The `Bearer` header.**
"Bearer" literally means *whoever bears this token gets in* — the token is not
tied to a device, an IP, or a browser. There's no cookie here, so nothing is
attached automatically: the client must deliberately put the header on each
request. A nice side effect is that CSRF stops being a concern, because a browser
never adds an `Authorization` header on its own the way it auto-sends cookies.
The flip side is that a leaked token is enough on its own — which is why the
short lifetime matters, and why HTTPS is non-negotiable in production.

**Stateless verification.**
With Django's normal session auth, the server stores a session row in the
database and the cookie is just a lookup key — every request costs a DB hit, and
`logout` deletes the row. JWT flips that: the token *carries* the user id, and
the server only recomputes the signature to decide whether to trust it. Nothing
is stored server-side, so any server with the signing key can verify any token
(great for scaling to many machines).

The cost of that trade: since the server keeps no record, it **cannot revoke an
access token**. Ban a user and their current token still works until `exp`
passes. That is exactly why the access lifetime is 15 minutes and not 15 days —
and if you truly need instant logout, you have to add server-side state back in
(SimpleJWT's token blacklist app), which gives up some of the statelessness you
came for.
