# LLD-35 — code for this class

Two **open-in-a-browser** security demos live here (double-click, no server, all local and harmless):

| File | What it shows |
|---|---|
| `xss_demo.html` | **Cross-Site Scripting** — a fake comments box rendered unsafe (`innerHTML` → an `<img onerror>` payload pops `alert(document.cookie)`) vs safe (`textContent` → inert), and how `HttpOnly` keeps the session cookie out of a stolen `document.cookie`. |
| `csrf_demo.html` | **Cross-Site Request Forgery** — a simulated bank (₹10,000) + an `evil.com` auto-submitting form + a defence selector (None / SameSite=Lax / CSRF token / Bearer). Under *None* the forged transfer steals ₹5,000; each defence blocks it, with the reason shown. |

The runnable **pytest** suites for today's material (JWT and OAuth) were prepared alongside Auth-2, so they live in
**[`../../LLD-34-Authentication-2-JWT-OAuth2/code/`](../../LLD-34-Authentication-2-JWT-OAuth2/code/)** rather than being duplicated:

| File | Concept | Live tool |
|---|---|---|
| `03_jwt_and_jws_deep.py` | JWS build/verify from scratch, tamper detection, `alg=none`, `exp`/`nbf` | [jwt.io](https://jwt.io/) |
| `04_oauth2_authorization_code_flow.py` | the login-with-Google dance + PKCE, simulated end to end | [OAuth Playground](https://www.oauth.com/playground/) |
| `demo_server.py` | live session-vs-JWT demo server (`python3 demo_server.py` → localhost:8034) | — |
| `08_homework.py` | this class's homework: the JWT + PKCE stubs | — |

All four pytest files are **stdlib-only** — zero installs, always green.

```bash
# security demos — just open them
open xss_demo.html csrf_demo.html

# the pytest suites
cd ../../LLD-34-Authentication-2-JWT-OAuth2/code
pytest -q 03_jwt_and_jws_deep.py 04_oauth2_authorization_code_flow.py
python3 demo_server.py
```
