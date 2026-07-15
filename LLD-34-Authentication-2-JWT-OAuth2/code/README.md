# LLD-34 — runnable examples

Each file is a small, focused pytest suite. The **JWT** and **OAuth** files are
**stdlib only** (`hmac`, `hashlib`, `base64`, `json`, `secrets`) — they run with
zero installs and are always green. The **bcrypt** and **argon2** files use the
real production libraries and **skip politely** if those aren't installed, so the
folder never errors on a fresh machine.

```bash
pip install pytest                 # required for the test files
pip install bcrypt argon2-cffi     # optional — unlocks files 01 & 02

pytest -v 03_jwt_and_jws_deep.py       # run one file
python3 03_jwt_and_jws_deep.py         # same — hands over to pytest
pytest -q 0*.py                        # the whole folder

python3 demo_server.py                 # the LIVE demo — no pytest, no installs
#   → open http://localhost:8034 and click through session vs JWT
```

> Because the files are numbered (not `test_*.py`), name them explicitly or use
> the `0*.py` glob — `pytest .` alone won't collect them.

| File | Concept | Live tool |
|---|---|---|
| `demo_server.py` | **live browser demo** — session (stateful, cookie + server store) vs JWT (stateless, nothing stored) vs tamper-a-token; a zero-install stdlib `http.server`. Adapted from the Aug-25 batch's `session_demo` / `jwt_demo`, collapsed into one file. | localhost:8034 |
| `01_bcrypt_properly.py` | bcrypt in practice: `hashpw`/`checkpw`, the `$2b$12$…` string anatomy, cost factor doubling, the 72-byte cap | [bcrypt-generator.com](https://bcrypt-generator.com/) |
| `02_argon2_and_the_family.py` | the modern family — PBKDF2 / bcrypt / scrypt / **argon2id**; memory-hardness; `check_needs_rehash` | [argon2.online](https://argon2.online/) |
| `03_jwt_and_jws_deep.py` | JWT = a **JWS** (signed, readable); verify, tamper detection, the **`alg=none`** attack, `exp`/`nbf`, access+refresh | [jwt.io](https://jwt.io/) |
| `04_oauth2_authorization_code_flow.py` | "Login with Google" simulated: the four roles, the **Authorization Code + PKCE** flow, single-use codes, stolen-code defence | [OAuth Playground](https://www.oauth.com/playground/) · [Google](https://developers.google.com/oauthplayground) |
| `08_homework.py` | **HOMEWORK** — 9 `pytest.skip` stubs across JWT (roundtrip / readable / tamper / expiry / wrong-secret), bcrypt anatomy, argon2 verify, PKCE. Turn them green. |

**Production note:** real systems use `PyJWT` (`jwt.encode`/`jwt.decode`), `bcrypt`
or `argon2-cffi`, and a library like `authlib` for OAuth. We build the pieces by
hand here only to demystify them — **never hand-roll crypto in production.**
