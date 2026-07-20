# CSRF, CORS & SameSite — a runnable Django 5 demo

Three ideas people constantly mix up, in one tiny app:

- **CSRF (Cross-Site Request Forgery)** — an attacker's page tricks *your logged-in browser* into sending a state-changing request to your site; Django defends with a secret token that only your own pages can read.
- **CORS (Cross-Origin Resource Sharing)** — a browser rule deciding whether JavaScript running on origin A is allowed to **read** a response from origin B.
- **SameSite cookies** — a cookie flag telling the browser *not to attach the cookie* to requests coming from another site, which kills most CSRF attacks at the source.

## Run it

```bash
cd 01_cors_csrf_django

python3 -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Then open <http://127.0.0.1:8001/>

## What to observe

1. **The form works.** Type a name, click *Submit form* → `✅ CSRF token was valid — form accepted`.

2. **Break the token → 403.** Back on the home page, open DevTools → Elements, find the hidden input
   `<input type="hidden" name="csrfmiddlewaretoken" value="…">` inside the form, delete that element, then submit again.
   Django answers **403 Forbidden** and the view never runs. That single hidden field is the whole CSRF defence.

3. **Same-origin fetch vs cross-origin fetch.**
   - Click `fetch("/api/ping/")` on the demo page → JSON appears. Same origin, CORS not involved.
   - Now save a small HTML file with `fetch("http://127.0.0.1:8001/api/ping/")` and serve it from a *different* origin
     (VS Code Live Server on `http://localhost:5500`, which is in `CORS_ALLOWED_ORIGINS`) → it works, and the response
     carries an `Access-Control-Allow-Origin` header.
   - Serve the same file from an origin that is **not** in the list (e.g. change the port) → the Network tab shows the
     request went out and the server replied **200**, but the console prints a CORS error and your JS gets nothing.
     That is the whole point: the server already did the work; only the *browser* withheld the response.
   - Confirm CORS is not auth: `curl http://127.0.0.1:8001/api/ping/` returns the JSON regardless.

4. **Inspect the cookie flags.** DevTools → Application → Cookies → `http://127.0.0.1:8001`.
   Look at `csrftoken` and (once a session exists) `sessionid`: columns for **HttpOnly**, **SameSite** and **Secure**
   match the values set in `config/settings.py`. Try flipping `SESSION_COOKIE_SAMESITE` to `"None"` and reloading to see
   the column change.

5. **The counter-example.** `POST /api/unsafe-submit/` is decorated `@csrf_exempt` and accepts anything.
   `curl -X POST http://127.0.0.1:8001/api/unsafe-submit/` succeeds with no token. Never ship that on an endpoint that changes state.

## Mental model (memorise this)

| Mechanism | One-line meaning |
|---|---|
| **CSRF token** | Proof that the request came from **YOUR** page — an attacker's page can make your browser send a request, but cannot read your token. |
| **SameSite** | Tells the browser **don't send my cookies on cross-site requests** — no cookie, no forged authenticated action. |
| **CORS** | Decides **who may READ the response** in a browser. It is not authentication and does not stop the request from executing. |

## Files

```
manage.py               entry point
requirements.txt        Django 5 + django-cors-headers
config/settings.py      middleware order, CORS list, cookie flags (all commented)
config/urls.py          4 routes
config/views.py         index, submit, api_ping, unsafe_submit
templates/index.html    form with {% csrf_token %} + a fetch button
```
