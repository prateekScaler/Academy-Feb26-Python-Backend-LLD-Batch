"""
A LIVE, runnable demo of the three ways to "stay logged in" — so you can SEE
the difference between session, token (JWT), and how a cookie is just transport.

Stdlib only. No Django, no installs:

    python3 demo_server.py        # then open http://localhost:8034

(Adapted from the Aug-25 batch's session_demo / jwt_demo, collapsed into one
zero-dependency file for class.)

What to notice while clicking around:
  • SESSION  — the server keeps a dict of who's logged in; you hold only an
               opaque id in a cookie. Logging out = the server forgets you.
               "Revoke" is instant because the state lives on the server.
  • JWT      — the server keeps NOTHING; the signed token itself carries your
               claims. Any server with the secret can verify it. But you can't
               un-issue it — it's valid until it expires.
  • COOKIE   — just an HTTP header the browser stores and auto-resends. It can
               carry EITHER a session id OR a JWT. The cookie is the envelope,
               not the token.
"""
import base64
import hashlib
import hmac
import http.server
import json
import time
import urllib.parse

SECRET = b"demo-secret-not-for-production"
SESSIONS = {}   # session_id -> {"user":..., "created":...}   <-- server-side STATE


# ── JWT helpers (same as 03_jwt_and_jws_deep.py) ────────────────────────────
def _b64(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _b64d(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def make_jwt(user, ttl=30):
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": user, "exp": int(time.time()) + ttl}
    h, p = _b64(json.dumps(header).encode()), _b64(json.dumps(payload).encode())
    sig = hmac.new(SECRET, f"{h}.{p}".encode(), hashlib.sha256).digest()
    return f"{h}.{p}.{_b64(sig)}"


def read_jwt(token):
    h, p, s = token.split(".")
    expected = hmac.new(SECRET, f"{h}.{p}".encode(), hashlib.sha256).digest()
    if not hmac.compare_digest(expected, _b64d(s)):
        raise ValueError("signature mismatch — token forged or altered")
    payload = json.loads(_b64d(p))
    if int(time.time()) >= payload["exp"]:
        raise ValueError("token expired")
    return payload


PAGE = """<!doctype html><meta charset=utf-8><title>Auth demo</title>
<style>body{font-family:system-ui;max-width:760px;margin:30px auto;line-height:1.6}
button{padding:8px 14px;margin:4px 0;cursor:pointer}pre{background:#0f172a;color:#e2e8f0;padding:12px;border-radius:8px;white-space:pre-wrap;word-break:break-all}
h2{margin-top:28px;border-bottom:2px solid #a855f7;padding-bottom:4px;color:#7c3aed}.out{min-height:24px}</style>
<h1>&#128273; Session vs JWT &mdash; live</h1>
<p>Open your browser devtools &rarr; Application &rarr; Cookies to watch what actually gets stored.</p>
<h2>1. Session (stateful) &mdash; server remembers you</h2>
<button onclick="s_login()">POST /session/login (alice)</button>
<button onclick="s_me()">GET /session/me</button>
<button onclick="s_logout()">POST /session/logout</button>
<pre class=out id=s_out>&mdash;</pre>
<h2>2. JWT (stateless) &mdash; the token carries everything</h2>
<button onclick="j_login()">POST /jwt/login (bob)</button>
<button onclick="j_me()">GET /jwt/me (sends the token)</button>
<button onclick="j_tamper()">Tamper the token, then GET /jwt/me</button>
<pre class=out id=j_out>&mdash;</pre>
<p id=j_store></p>
<script>
let JWT=null;
const show=(id,o)=>document.getElementById(id).textContent=typeof o==="string"?o:JSON.stringify(o,null,2);
async function s_login(){const r=await fetch("/session/login",{method:"POST"});show("s_out",await r.json())}
async function s_me(){const r=await fetch("/session/me");show("s_out",await r.json())}
async function s_logout(){const r=await fetch("/session/logout",{method:"POST"});show("s_out",await r.json())}
async function j_login(){const r=await fetch("/jwt/login",{method:"POST"});const d=await r.json();JWT=d.token;show("j_out",d)}
async function j_me(){const r=await fetch("/jwt/me",{headers:{Authorization:"Bearer "+(JWT||"")}});show("j_out",await r.json())}
async function j_tamper(){const p=(JWT||"").split(".");p[1]=p[1].slice(0,-2)+"XX";const r=await fetch("/jwt/me",{headers:{Authorization:"Bearer "+p.join(".")}});show("j_out",await r.json())}
</script>
"""


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass  # quiet

    def _json(self, code, obj, cookie=None):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(body)

    def _cookies(self):
        raw = self.headers.get("Cookie", "")
        return dict(p.strip().split("=", 1) for p in raw.split(";") if "=" in p)

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(PAGE.encode())
        elif self.path == "/session/me":
            sid = self._cookies().get("sid")
            sess = SESSIONS.get(sid)
            if sess:
                self._json(200, {"ok": True, "user": sess["user"],
                                 "note": f"server looked up sid={sid[:8]}... in its store "
                                         f"({len(SESSIONS)} active session(s))"})
            else:
                self._json(401, {"ok": False, "note": "no valid session cookie — the server "
                                 "doesn't recognise you"})
        elif self.path == "/jwt/me":
            auth = self.headers.get("Authorization", "")
            token = auth[7:] if auth.startswith("Bearer ") else ""
            try:
                payload = read_jwt(token)
                self._json(200, {"ok": True, "user": payload["sub"],
                                 "note": "server stored NOTHING — it just re-verified the "
                                         "signature on the token you sent"})
            except ValueError as e:
                self._json(401, {"ok": False, "note": str(e)})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/session/login":
            sid = hashlib.sha256(str(time.time_ns()).encode()).hexdigest()
            SESSIONS[sid] = {"user": "alice", "created": time.time()}
            # HttpOnly so JS can't read it; the id is opaque and meaningless off-server
            self._json(200, {"ok": True, "stored_on_server": "yes — a session row",
                             "you_hold": f"an opaque cookie sid={sid[:8]}...",
                             "active_sessions": len(SESSIONS)},
                       cookie=f"sid={sid}; HttpOnly; Path=/; SameSite=Lax")
        elif self.path == "/session/logout":
            sid = self._cookies().get("sid")
            existed = SESSIONS.pop(sid, None) is not None
            self._json(200, {"ok": True, "revoked": existed,
                             "note": "instant revocation — the server just forgot the session",
                             "active_sessions": len(SESSIONS)},
                       cookie="sid=; Max-Age=0; Path=/")
        elif self.path == "/jwt/login":
            token = make_jwt("bob")
            self._json(200, {"ok": True, "stored_on_server": "no — nothing!",
                             "token": token,
                             "note": "decode the middle part at jwt.io — it's readable; the "
                                     "server keeps no record of it"})
        else:
            self._json(404, {"error": "not found"})


if __name__ == "__main__":
    port = 8034
    print(f"Auth demo running → http://localhost:{port}  (Ctrl-C to stop)")
    http.server.HTTPServer(("", port), H).serve_forever()
