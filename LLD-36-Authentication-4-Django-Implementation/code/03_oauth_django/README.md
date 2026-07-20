# Login with Google — OAuth 2.0 Authorization Code + PKCE, by hand

A tiny Django 5 project that implements "Sign in with Google" manually using
`requests`, so you can see every HTTP hop instead of trusting a library.

No models, no forms, no admin. Four URLs and one template.

---

## What this demonstrates

The **Authorization Code flow with PKCE** — the flow you should use for any
server-side web app today.

```
  Browser                      Our Django server                 Google
     |                                |                             |
     |  click "Login with Google"     |                             |
     |------------------------------->|                             |
     |                                | make code_verifier (secret) |
     |                                | code_challenge = S256(v)    |
     |   302 redirect to Google  <----|                             |
     |------------------------------------------------------------->|
     |            (you type your password HERE, on Google)          |
     |            (consent screen: "share name, email, picture?")   |
     |                                |                             |
     |   302 back to /oauth/callback/?code=...&state=...            |
     |<-------------------------------------------------------------|
     |------------------------------->|                             |
     |                                | check state == session      |
     |                                | POST code + code_verifier   |
     |                                |---------------------------->|
     |                                |     access_token            |
     |                                |<----------------------------|
     |                                | GET /userinfo (Bearer tok)  |
     |                                |---------------------------->|
     |                                |     name, email, picture    |
     |                                |<----------------------------|
     |   302 home, profile in session |                             |
     |<-------------------------------|                             |
```

Three ideas to take away:

- **The app never sees the password.** It is typed on `accounts.google.com`.
- **PKCE** makes a stolen authorization code useless. We send only
  `BASE64URL(SHA256(verifier))` through the browser and reveal the `verifier`
  itself only on the server-to-server token call. An attacker who grabs the
  `code` cannot produce a matching verifier.
- **`state`** stops callback CSRF. It is a random value we generate, save in the
  session, and compare when Google sends the browser back.

---

## 1. Get Google credentials

1. Go to <https://console.cloud.google.com/>.
2. Create a project (or pick an existing one) from the project dropdown at the top.
3. In the left menu: **APIs & Services → OAuth consent screen**.
   - User type: **External**.
   - Fill in app name, your email as support email and developer contact. Save.
   - Under **Audience / Test users**, add the Google account you will log in
     with. (While the app is in "Testing", only listed test users can sign in.)
4. Left menu: **APIs & Services → Credentials**.
5. **Create Credentials → OAuth client ID**.
6. Application type: **Web application**. Give it any name.
7. Under **Authorized redirect URIs**, click **Add URI** and paste exactly:

   ```
   http://127.0.0.1:8000/oauth/callback/
   ```

   This must match `GOOGLE_REDIRECT_URI` in `config/settings.py` character for
   character — including `http`, the port, and the trailing slash.
   Note: `localhost` and `127.0.0.1` are *different* to Google. Use
   `127.0.0.1` in your browser too.
8. Click **Create**. Copy the **Client ID** and **Client secret**.

### Put them in your environment

```bash
export GOOGLE_CLIENT_ID=1234567890-abcdefg.apps.googleusercontent.com
export GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxx
```

(Environment variables, not source code — secrets should never be committed.
`config/settings.py` falls back to obvious placeholders if they are unset, and
the app will show a friendly error instead of a confusing 500.)

---

## 2. Run it

```bash
cd 03_oauth_django

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate           # creates the session table
python manage.py runserver
```

Open <http://127.0.0.1:8000/> (use `127.0.0.1`, not `localhost`) and click
**Login with Google**.

---

## 3. What to watch

Do this slowly the first time — every step is observable.

1. **The redirect to Google.** After clicking the button, read the address bar
   before the page loads. Find in it:
   - `client_id=` — our public app identifier.
   - `scope=openid+email+profile` — exactly what we are asking for, no more.
   - `code_challenge=` and `code_challenge_method=S256` — the *hash* of our
     secret. The secret itself is nowhere in this URL.
   - `state=` — the random anti-CSRF value.

2. **The consent screen.** This page is served by Google, on Google's domain,
   with Google's TLS certificate. Your password goes here and nowhere else.

3. **Coming back.** The address bar becomes
   `http://127.0.0.1:8000/oauth/callback/?code=4/0Ab...&state=...`.
   That code is one-time and expires in minutes. On its own it is not a login.

4. **The token exchange you cannot see in the browser** — and that is the
   point. `oauth_callback` in `config/views.py` POSTs `code` +
   `code_verifier` + `client_secret` straight to Google from the server. Add a
   `print(token_data)` there if you want to watch the `access_token` arrive.

5. **Your profile appears.** Fetched by our server from the userinfo endpoint
   using `Authorization: Bearer <token>`.

6. **The PKCE panel.** Below the profile the page prints the three values from
   the login you just did — `code_verifier`, `code_challenge`, `code` — so you
   can see them side by side instead of imagining them. The point to make out
   loud: the challenge and the code both travelled through the browser and are
   effectively public; the verifier did not. That gap is the whole mechanism.

   *(Printing these is a teaching device only — `views.py` keeps them in the
   session under `pkce_trace` purely for this page. Never do this in a real
   app.)*

Then ask yourself:

- At which point did this app learn your password? (Never.)
- If someone shoulder-surfed the `?code=` out of the address bar and replayed
  it, what would they need that they do not have? (The `code_verifier` — PKCE.)
- If an attacker tricked your browser into hitting `/oauth/callback/` with
  *their* code, what stops it? (The `state` check, plus the missing verifier.)

Try breaking it on purpose: change `"S256"` to `"plain"` in `login_google`, or
send a wrong `code_verifier`, and watch Google reject the token exchange.

---

## Files

| File | What is in it |
|---|---|
| `config/settings.py` | Google endpoints, client id/secret, redirect URI |
| `config/urls.py` | the four routes |
| `config/views.py` | **the whole OAuth flow, heavily commented** |
| `templates/home.html` | login button / profile / plain-English explainer |

---

## In production

Do not hand-roll this. Use [`django-allauth`](https://docs.allauth.org/), which
handles PKCE, state, token refresh, ID-token verification, account linking and
dozens of providers for you. This project exists so you understand what
`django-allauth` is doing on your behalf.
