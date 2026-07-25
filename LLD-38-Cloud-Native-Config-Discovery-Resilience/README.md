# LLD-38 — Cloud-Native Patterns: Config, Service Discovery & Resilience

> **Module 4, session 8.** Last class we split work across many processes. Now they have to *live together*. Three problems every distributed system hits: how a service gets its **config** (without leaking secrets), how it **finds** the other services, and how it **survives** when a dependency is slow or down. Ends in runnable Python — a circuit breaker from scratch, plus the real resilience stack.

**How to use this class:** open `index.html` for the interactive page (diagrams, scenario quizzes, and a live demo runbook). Everything is beginner-first. Runnable demos live in [`code/`](code/): a from-scratch circuit breaker and a toy service registry (no installs), plus the production resilience stack and config loader using real libraries.

---

## The problem: one process was easy, many is a different game
The moment your app is more than one process — a web tier, workers, a payments service, third-party APIs — three questions appear that a monolith never had:
1. **How do I get my config?** URLs, keys, timeouts differ per environment. Hardcoding means a redeploy to change a value, and secrets leaking into git.
2. **How do I find the others?** Service B lives at… which IP? It autoscales, restarts, moves hosts. `http://10.0.1.5:8000` is wrong an hour from now.
3. **How do I survive their failures?** When Payments goes *slow* (not even down), every request that touches it holds a thread — the pool saturates and the failure **cascades** to features that never touch payments. A single slow dependency with no timeout can 503 your whole site.

## Pattern 1 — Externalized configuration (12-factor)
*Config is everything that differs between deploys* — it belongs in the **environment**, not the code. The ladder, worst → best:

| Level | Looks like | Why move up |
|---|---|---|
| **Hardcoded** | `DB_URL = "postgres://prod…"` in source | any change is a code change + redeploy; secrets end up in git history forever |
| **Config file** | `settings.yaml` per env | better, but files still get committed; secrets still on disk in the repo |
| **Env vars** | `os.environ["DB_URL"]` | the 12-factor default: same build, different env per deploy; secrets injected at runtime |
| **Config/secrets service** | Vault, AWS SSM/Secrets Manager, Consul | central, versioned, access-controlled, **rotatable** without a redeploy |

- **The secret rule:** a secret never lives in the code or the repo — it comes from the environment (or a secrets manager) at runtime. A local `.env` is fine for dev, but it must be **gitignored**; ship a committed `.env.example` with placeholders.
- **Precedence:** most specific wins — a real env var **>** `.env` file **>** code default. That's exactly how `pydantic-settings` resolves it (see `config_demo.py`).

### Config in the cloud, concretely — who sets the values, and how to override
Same build, different environment. The value is injected from *outside* the container at runtime; the code never changes.

```bash
# Override locally for one run — a real env var beats .env, which beats the default:
DB_URL="postgres://localhost/dev" TIMEOUT_SECONDS=2 python3 config_demo.py

# Docker: inject at run time, nothing baked into the image
docker run -e DB_URL="$DB_URL" -e API_KEY="$API_KEY" myapp:1.0
```

On Kubernetes the platform sets them: non-secret config from a **ConfigMap**, secrets from a **Secret**.

```bash
kubectl create configmap app-config  --from-literal=TIMEOUT_SECONDS=2
kubectl create secret generic app-secrets --from-literal=API_KEY=sk-live-…
```
```yaml
# in the Pod spec — the platform maps these into the container's environment
env:
  - name: TIMEOUT_SECONDS
    valueFrom: { configMapKeyRef: { name: app-config,  key: TIMEOUT_SECONDS } }
  - name: API_KEY
    valueFrom: { secretKeyRef:    { name: app-secrets, key: API_KEY } }
```
The app just reads its `Settings` object — it never knows whether a human, a ConfigMap, or Vault set the value. **The code is identical across dev, staging, and prod; only the environment differs.**

## Pattern 2 — Service discovery
You can't hardcode an IP when instances autoscale, crash, and get rescheduled. Each instance **registers** itself and **heartbeats**; a client asks the **registry** for a *healthy* address (and load-balances). Miss your heartbeats → dropped from rotation, so traffic never hits a dead instance.
- **Client-side** (Eureka/Consul-aware clients): the client queries the registry and picks an instance itself.
- **Server-side** (a load balancer, or Kubernetes `Service` + kube-proxy): the client calls one stable address; the LB picks.
- **On Kubernetes it's mostly free:** call a DNS name like `payments.default.svc.cluster.local` and k8s routes to a healthy pod. The pattern didn't vanish — it moved into the platform. (`service_registry.py` is a ~60-line toy version.)

## Pattern 3 — Resilience (the big one)
Dependencies *will* be slow or down. Fail **gracefully and locally** instead of cascading. Layer these:
1. **Timeouts** — every network call gets one, so a slow dep costs 2 seconds, not a hung thread. No timeout = the cascading failure above.
2. **Retries + backoff + jitter** — retry transient failures with a growing, randomized delay (straight from LLD-37). Cap the attempts, and **only retry safe/idempotent operations** — auto-retrying a `charge card` double-charges.
3. **Circuit breaker** — wrap the call, count failures. After too many it **trips OPEN**: every call **fails fast** without touching the dependency, giving it room to recover. After a cooldown it goes **HALF-OPEN** and lets *one* trial through — success → CLOSED, failure → OPEN. Like your home's breaker. (`circuit_breaker.py` builds the state machine from scratch.)
4. **Bulkhead** — give each dependency its *own* pool of workers/connections. If Payments goes slow it can only exhaust *its* compartment; Email and everything else keep running. Isolation, not a bigger pool, is the fix for blast radius.
5. **Fallback / graceful degradation** — when a call fails (or the breaker is open), return something useful: a cached value, a default, a "recommendations unavailable" placeholder. A degraded page beats a 500 — but never fall back in a way that hides a *money* error.
6. **Health checks** — **liveness** ("are you alive?" → fail restarts the pod) vs **readiness** ("ready for traffic?" → fail pulls you from the load balancer, doesn't kill you). A slow dependency should fail *readiness*, not liveness.

**The stack together:** wrap every remote call in a *timeout*, add bounded *retries*, put a *circuit breaker* around it, isolate it with a *bulkhead*, and give a *fallback* for when it's all down. That's a resilient client.

**The resilient client, in ~12 lines** (real libraries — the full version is `resilient_client.py`):
```python
import httpx, pybreaker
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type

breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30)  # trips OPEN after 5 fails
client  = httpx.Client(timeout=2.0)                               # every call has a timeout

@breaker                                                          # fail fast when OPEN
@retry(stop=stop_after_attempt(3),                               # bounded retries…
       wait=wait_exponential_jitter(initial=0.2, max=2),         # …backoff + jitter
       retry=retry_if_exception_type(httpx.HTTPError))
def get_price(sku):
    return client.get(f"http://pricing/price/{sku}").json()["price"]

def price_or_fallback(sku):
    try:    return get_price(sku)                                 # timeout+retry+breaker
    except Exception:  return cached_price(sku)                   # graceful degradation
```

---

## The cloud-native ecosystem (what to actually know)
These patterns weren't invented in a vacuum — they were extracted from how Google, Netflix, and AWS ran services at scale, then open-sourced.
- **Orchestration & platform:** **Kubernetes** (2014, born from Google's Borg) is the substrate — it gives you service discovery, health checks, config/secrets, and rollouts as *platform* features. Around it: **Helm** (packaging), **Istio/Linkerd** (service mesh — resilience pushed into a sidecar proxy, so retries/timeouts/breakers happen outside your code).
- **The CNCF** (Cloud Native Computing Foundation, 2015) is the neutral home for these projects: Kubernetes, **Prometheus** (metrics), **Envoy** (proxy), **etcd**, **gRPC**, **OpenTelemetry**.
- **Config & secrets:** HashiCorp **Vault** & **Consul**; **AWS SSM Parameter Store / Secrets Manager**; **etcd**.
- **Resilience heritage:** Netflix **Hystrix** (2012) popularized the circuit breaker; it's retired now, but the *pattern* it taught is everywhere.
- **Python-specific:** `tenacity` (retries), `pybreaker` / `circuitbreaker` (breakers), `httpx` (timeouts, async), `pydantic-settings` (12-factor config); on the platform side the official `kubernetes` client and `python-consul`.

## Why these same patterns matter in the AI era
An LLM/agent app is *just another distributed system with flaky dependencies* — only now the "slow payments service" is a **model endpoint** and the "third-party API" is a **tool call**.
- **Timeouts:** an inference call can hang for 30s+; every model/tool call needs one, or a single stuck request holds a worker — the same cascade as a slow dependency.
- **Retries + backoff + jitter:** provider `429`/`503` rate limits are *transient* — retry with backoff. But generation is expensive; cap attempts and use idempotency keys so a retry doesn't double-charge or double-act.
- **Circuit breaker:** when a provider is degraded, trip OPEN and stop hammering it — fail fast to a fallback instead of burning latency and money on calls that will fail.
- **Fallback / graceful degradation:** primary model down → route to a cheaper/secondary model, a cached answer, or an honest "can't answer right now." A degraded agent beats a hung one.
- **Bulkhead:** give each provider/tool its own concurrency budget, so one slow tool in an agent loop can't starve the rest.
- **Config & secrets:** API keys, model names, and temperatures are 12-factor config — injected per environment, never hardcoded, rotated without a redeploy.

---

## `code/` — runnable demos

| File | Runs with | Demonstrates |
|---|---|---|
| [`circuit_breaker.py`](code/circuit_breaker.py) | `python3` (no installs) | A from-scratch breaker: watch CLOSED → OPEN (fail fast) → HALF-OPEN → CLOSED live |
| [`service_registry.py`](code/service_registry.py) | `python3` (no installs) | A toy registry: register 3 instances, round-robin discover, drop an unhealthy one |
| [`resilient_client.py`](code/resilient_client.py) | venv + libs | The real stack — httpx timeout + tenacity retries + circuit breaker + fallback — through flaky → down → recovered phases |
| [`config_demo.py`](code/config_demo.py) | venv + libs | `pydantic-settings`: `.env` load, OS-env override (precedence), type validation, `SecretStr` |

```bash
cd code
python3 circuit_breaker.py          # stdlib — watch the breaker trip and recover
python3 service_registry.py         # stdlib — round-robin + unhealthy drop

python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt     # pydantic-settings, tenacity, httpx, pybreaker
python3 resilient_client.py         # timeout + retry + breaker + fallback, live
python3 config_demo.py              # env var beats .env beats the default
```
> Verified against Python 3.14, pydantic-settings 2.14, tenacity 9.1, httpx 0.28, pybreaker 1.4. `.env` is gitignored; only `.env.example` (placeholders) is committed.

## Homework
1. **Breaker:** run `circuit_breaker.py`; change `failure_threshold` and `recovery_timeout` and watch it get trigger-happy vs forgiving. Then remove the breaker and watch retries hammer a dead service.
2. **Resilient client:** run `resilient_client.py` through all phases; narrate what each layer (timeout / retry / breaker / fallback) did.
3. **Config:** run `config_demo.py`; set the env var and watch it beat the `.env` value. Confirm `.env` is gitignored.
4. **Think:** pick a service you've built. Which remote calls have *no timeout* right now? That's your first cascading-failure risk — fix one.

**Next class — Logging & Monitoring:** you've made the system resilient — now how do you *see* what it's doing? Structured logs, metrics, traces, and alerts, so you catch the slow dependency *before* it takes you down.
