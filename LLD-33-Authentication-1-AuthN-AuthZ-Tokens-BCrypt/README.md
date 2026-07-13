# LLD-33 — Authentication, Part 1: History, AuthN vs AuthZ, Passwords & Tokens

> **Module 4, session 3 — the security groundwork.** Two questions every backend answers: *"who are you?"* (authentication) and *"what may you do?"* (authorization). Today: 5,000 years of proving identity, telling the two questions apart, storing passwords so a breach hands over nothing, and handing out tokens. It's the foundation for the User Service you build later in this module — where **testing** (LLD-31/32) and the **Membership/RBAC** shape (LLD-29) meet.

**How to use this class:** open `index.html` for the interactive page (discussion hooks before every concept, click-to-reveal tables, spot-the-bug snippets, a live base64 encoder, 11 quizzes). This README is the same content in prose. Runnable examples live in [`code/`](code/README.md) — pure pytest, **stdlib only** (30 tests green + a 9-stub homework); production uses `bcrypt`/`argon2`/`PyJWT`, but we build the pieces by hand to demystify them. Historical photos are in [`images/history/`](images/history/) (public-domain/CC, Wikimedia Commons).

---

## Step 0 — The fascinating history of authentication

*"Trust, but verify."* The problems never changed in 5,000 years — impostors, leaked secrets, lazy humans — only the technology did. Told as one story:

| Era | Chapter | The idea it hands forward |
|---|---|---|
| 3500 BCE, Mesopotamia | A merchant "signs" clay by rolling a carved **cylinder seal**; Babylon adds **fingerprints** pressed into contracts | *Something you have* and *something you are* arrive first |
| 1000 BCE, Egypt & Rome | The **signet ring** in wax: unique pattern (identity), shatters if opened (tamper-evidence), can't be disowned (non-repudiation). A Pharaoh's ring was **smashed the day he died** | Egypt invents **key revocation**, 3,000 years before PKI |
| 500–200 BCE, Rome | Allied families split a **tessera hospitalis** in two — descendants prove the alliance by matching halves (Greek *symbolon* → our word "symbol"). At the camp gate: the nightly **watchword** | The third factor — *something you know*. The world's first password, **rotated daily** because spoken secrets leak |
| 1940s, Bletchley Park | **Enigma**'s daily settings = a shared secret; readable German = authentic message. Broken partly because bored operators picked predictable keys | The strongest system, undone by weak human choices — still the #1 cause of breaches |
| 1962, MIT | **CTSS**, the first passworded system. Allan Scherr requests a *printout of the password file* — stored in **plaintext** — and shares it | The first password breach in history: never store the secret readable |
| 1976, Bell Labs | Morris & Thompson's Unix **`crypt`**: use the password as a key, encrypt zeros, repeat 25× (~1 second on 1976 hardware) | **Store a hash** and **make it slow** — both of today's big ideas, five decades early |
| Today | ATM card + PIN (two factors since 1967), Touch ID (Babylon's fingerprint, 4,000 years later), passkeys/FIDO2 (the signet ring reborn) | Full circle |

**The three factors** — every login ever is one (or more) of: **something you know** (watchword → password/PIN), **something you have** (signet ring/tessera → phone, hardware key), **something you are** (fingerprint on clay → Face/Touch ID). Nobody has found a fourth.

**Which factor do you reach for today?**

| Factor | Superpower | Fatal flaw | Reach for it when… |
|---|---|---|---|
| **Know** (password, PIN) | free, works anywhere | guessable, reusable, phishable | the baseline — nearly every account starts here |
| **Have** (phone, hardware key) | can't be guessed from afar; FIDO2 resists fake sites | lost, stolen, left at home | money or admin power — the step-up factor |
| **Are** (fingerprint, face) | nothing to remember or carry | **can't be rotated if it leaks** | fast local unlock of the device holding your other factors |

Scenarios: phone unlock 40×/day → **are**; email on a new laptop → **know + have**; a ₹2,00,000 transfer → **step-up** (add a factor at the moment of risk); a CI server deploying → **have** (a revocable credential — machines can't remember or be fingerprinted). The modern pattern is **combining factors (MFA)**.

## Step 1 — Authentication ≠ Authorization
- **AuthN** — *"who are you?"* — prove identity (password, token, fingerprint). Comes **first**.
- **AuthZ** — *"what may you do?"* — given a known identity, is this action allowed? Comes **after**.
- Not logged in → **401** (misnamed; means *unauthenticated*) → show login. Logged in but not allowed → **403 Forbidden** → access denied; re-logging-in won't help.
- Airport: the passport check is authentication; whether your boarding pass opens the lounge is authorization.
- **AAA:** Authentication (who) · Authorization (what) · Accounting (what did you do — the audit trail).

**Spot the mistake — three real snippets** (each hides a classic blunder):
1. A permission failure returning `Response(status=401)` → the user *is* authenticated; use **403**. Worse than cosmetic: frontends redirect 401 to login, so the editor lands in an **infinite login loop**.
2. `@require_permission` stacked **above** `@require_login` → the top decorator runs first on a request, so the permission check inspects an *anonymous* user. **Authenticate first, then authorize.**
3. An admin-only button in React hiding an unguarded Flask endpoint → `curl -X DELETE /users/7` needs no button. The frontend decides what to *show*; **only the backend decides what to allow**.

## Step 2 — Encoding vs Encryption vs Hashing
Three ELI5 metaphors: encoding = **translating a letter** (anyone with the dictionary reverses it), encryption = **a locked diary** (only the key-holder), hashing = **a meat grinder** (no way back).

| | Reversible? | Key? | Same in → same out? | For |
|---|---|---|---|---|
| **Encoding** (base64) | yes, by anyone | no | yes | representation (transport) — **not security** |
| **Encryption** (AES/Fernet) | yes, with the key | yes | no (with an IV) | data you must read back |
| **Hashing** (SHA-256, bcrypt) | **no** — one-way | no | yes | fingerprints you only compare — **passwords** |

By-hand versions: Pig Latin (encoding), Caesar shift 3 (encryption — reversing needs the key), letter-sum (hashing — CAT=24, but so is TAC: collisions make it one-way).

**How base64 actually works — 3 bytes in, 4 characters out.** Channels like JSON/URLs/email carry only *text*; base64 re-spells any bytes in 64 safe characters (`A–Z a–z 0–9 + /`). 64 = 2⁶, so each character carries exactly **6 bits**:

```
text          M          a          n
bits       01001101   01100001   01101110      = 24 bits
regroup     010011  010110  000101  101110     = four 6-bit chunks
look up       19      22       5      46
result         T       W       F       u      →  "Man" ⇒ "TWFu"
```

Consequences: 3 bytes → 4 chars (**+33% size**); inputs not divisible by 3 get `=` padding (`"Ma"→"TWE="`, `"M"→"TQ=="`); decoding is the same table backwards — **no key anywhere**, hence not security; JWTs use **base64url** (`-`/`_` instead of `+`/`/`). `base64.b64encode(b"secret123")` → `b'c2VjcmV0MTIz'` — "hidden"? not even slightly.

Decision guide: password → **hash** · secret only the recipient reads → **encrypt** · API key you must reuse → **encrypt** · binary in JSON → **encode** · file integrity → **hash**.

## Step 3 — Password storage evolution (each era, and the attack that broke it)
1. **Plaintext** → a breach is instant, total takeover (Facebook 2019: 600M in plaintext, readable by 20,000 employees).
2. **Fast hash (MD5/SHA-1)** → **rainbow tables** + speed (~164B/s MD5). LinkedIn 2012: 117M unsalted SHA-1, 90% cracked in days. No salt ⇒ shared passwords share a hash.
3. **Salted hash** → salt defeats rainbow tables, but SHA-256 at ~22B/s still falls to **GPU brute force** in minutes. *Salting stops tables, not trying.*
4. **Slow + salted (bcrypt / scrypt / argon2)** → deliberately slow, tunable work factor, salt built in. **The answer.**

**The simple math behind "falls in minutes":** a weak 8-char password (a–z + 0–9) is a lock with 8 dials × 36 symbols: 36⁸ ≈ **2.8 trillion** combinations ÷ 22 billion/sec ≈ **128 s ≈ 2 minutes** (worst case; ~1 min average). Salt appears **nowhere** in that math — it's stored in plaintext beside the hash; its job is forcing the attacker to redo the work *per user* (and killing precomputed tables), not slowing one user down. The exponent is the game: 26⁸ → 9.5 s, 26¹² → 50 days, 95¹² → ~780,000 years — **length beats cleverness**. Swap the denominator for bcrypt's ~1,400/s and the same 2.8 trillion takes **~63 years**.

**Are bcrypt/scrypt/argon2 encryption or hashing?** Hashing — technically **password-hashing functions / KDFs**, engineered for *cost* where SHA is engineered for speed: bcrypt = tunable CPU rounds, scrypt = also memory-hard (GPUs starve), argon2 = PHC-2015 winner, the modern default. Fun twist: bcrypt is built *out of* the Blowfish **encryption** cipher — it encrypts a fixed string with your password 64× and *throws the key away*. Exactly Unix `crypt`'s 1976 trick. Litmus test: *could you ever need the original back?* Encryption: yes (that's the key). These: never — that's what makes them hashing.

**Hashing 101 — the doubts every batch has:**
- *"The inventors must secretly keep the un-hash function."* No — hashing **destroys** information rather than hiding it (4 GB in, 32 bytes out); reversal isn't forbidden, it's *impossible*, for the inventors too. Mini-hash: `7+8=15` — now reverse "15". Login never un-hashes; it hashes your **attempt** and compares.
- *"Collisions exist, so it's broken?"* Collisions **must** exist (pigeonhole: infinite inputs, 2²⁵⁶ outputs) — broken means **craftable on demand**: MD5 since 2004, SHA-1 since 2017 (SHAttered). No SHA-256 collision has ever been found.
- *"Deterministic yet irreversible?"* Same steak → same mince; still can't un-grind. Determinism is what makes comparison possible; the per-user variety comes from **salt**, not the function.
- *"Does a bigger input give a bigger hash?"* No — always 256 bits, which itself proves information is discarded.
- *"Change one letter, hash changes a little?"* No — **avalanche**: `sha256("kitten")=58972659…` vs `sha256("kitteN")=ea64c998…`. No "getting warmer" gradient to climb — only brute force remains.

## Step 4 — Why "slow" is the trick
**The asymmetry:** a user logs in once and never feels a 0.3 s hash; an attacker doing billions of guesses can't afford 0.3 s *each*. Cracking `Tr0ub4dor&3`: SHA-256 ~1 hour vs bcrypt (cost 12) ~226 years.
- bcrypt gives **built-in salt**, an **adaptive work factor** (`rounds=12`; +1 doubles the time — raise it as hardware improves), and parallelism resistance.
- Rules: bcrypt (cost ≥ 12) or argon2 · use the library · never MD5/SHA/unsalted · compare **constant-time**.

**What's a constant-time check?** `==` quits at the first mismatching character, so **response time whispers how much of a guess was right** — the safecracker listening for clicks. That turns 16⁶⁴ guesses into 16 × 64, position by position; with enough samples it works against real APIs verifying tokens and webhook signatures. `hmac.compare_digest` compares **every byte, always** — wrong-first-char and wrong-last-char take identical time, and the side-channel goes silent. (`code/03` demonstrates the leak and the fix; `bcrypt.checkpw` does this internally.)

## Step 5 — Tokens (staying logged in)
- **Session (stateful):** server stores a session record; a cookie carries the id; every request is a DB lookup. Revoke = delete the row.
- **Token/JWT (stateless):** a **signed** token holds the claims; the server just verifies the signature — no storage. *Like a movie ticket: proves you paid without phoning the box office.*
- **A JWT = `header.payload.signature`** (base64url). Signature = `HMAC-SHA256(header.payload, SECRET)`.
- **Signed, NOT encrypted** — anyone can base64-decode the payload and read every claim. **Never put a secret** (card, PII) in it; the signature protects *integrity*, not *confidentiality*.

| | Session | JWT |
|---|---|---|
| State | server-side | client holds it |
| Per-request | DB lookup | verify a signature (CPU) |
| Scaling | shared session store | stateless |
| Revocation | trivial (delete) | hard (valid until `exp`) |

- **Access + refresh tokens:** short-lived access token (15–60 min) on every call; long-lived refresh token only to `/refresh` to mint a new one — bounds the "hard to revoke" problem.

## Step 6 — RBAC (from identity to permissions)
Users have **roles**; roles grant **permissions**; check the fine-grained **permission** at each action (`user.can("event:delete")`), never a role name. The role→permission map lives in one place, so a new role or re-assigned permission needs no change at the call sites. It's the LLD-29 **Membership** association generalised.

---

## Which file in `code/` teaches which concept

| Concept | Run this | What it proves |
|---|---|---|
| Step 2 · Encoding/Encryption/Hashing | `code/01_encoding_encryption_hashing.py` | base64 reverses keyless; Fernet demands its key; SHA-256 avalanches and won't go backwards |
| Step 3 · Password eras | `code/02_password_storage_evolution.py` | each era falls in a test — plaintext read off, MD5 rainbow-tabled, unsalted twins exposed; slow+salted survives |
| Step 4 · Slow + safe verification | `code/03_verifying_safely_timing.py` | why `==` leaks via timing and `hmac.compare_digest` doesn't |
| Step 5 · Tokens & JWTs | `code/04_build_a_jwt_from_scratch.py` | hand-build `header.payload.signature`, tamper one char, watch verification fail |
| Step 6 · RBAC | `code/05_rbac.py` | permissions, not role names, at the call site |
| Everything shipped | `code/06_password_service.py` | the register/login service you'd deploy, from files 01–03 |
| Your turn | `code/08_homework.py` | 9 `pytest.skip` stubs — delete each and make it green |

## Battle-test it — hackattic challenges for this class

[hackattic.com](https://hackattic.com/challenges) serves real challenges: `GET` a problem as JSON, compute, `POST` the answer (free account → access token). These five are exactly today's material:

| Challenge | Concept | Weapon |
|---|---|---|
| [Password hashing](https://hackattic.com/challenges/password_hashing) | Steps 2–4 in one shot: base64-decode the salt, then SHA-256 → HMAC → PBKDF2 → scrypt | `code/01` + `code/06` |
| [Jotting JWTs](https://hackattic.com/challenges/jotting_jwts) | Step 5: verify signature and `exp`, reject tampered tokens | `code/04` |
| [Help me unpack](https://hackattic.com/challenges/help_me_unpack) | Step 2: base64 is bytes-as-text; unpack ints/floats | `code/01` + `struct` |
| [Collision course](https://hackattic.com/challenges/collision_course) | Step 3: two messages, one MD5 — why MD5 is dead | `code/02` (era 2) |
| [Brute force ZIP](https://hackattic.com/challenges/brute_force_zip) | Step 4: raw guessing speed — then imagine 0.3 s per try | `code/02` + patience |

## Homework
1. **Warm-up: [`code/08_homework.py`](code/08_homework.py)** — 9 `pytest.skip` stubs across hashing, salting, constant-time compare, JWT (round-trip / tamper / expiry) and RBAC. Turn them green.
2. Add `bcrypt` `register`/`login` to your Module-1 Django project (or LLD-32's `django_demo`); test it with `@pytest.mark.django_db` + `APIClient`.
3. Decode a real JWT from [jwt.io](https://jwt.io) by hand — read the claims, confirm it isn't encrypted.
4. *Stretch:* add an `IsOwner` permission and an RBAC role check to one endpoint.

**Next class — Authentication-2:** JWTs in depth and **OAuth 2** (the "login with Google" dance).
