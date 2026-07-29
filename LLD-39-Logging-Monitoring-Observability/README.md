# LLD-39 — Logging & Monitoring: Logs, Metrics, Traces & Alerts

> **Module 4, session 9.** Last class you made the system *survive* failures (timeouts, retries, breakers). This class you make it *tell you* about them. A resilient system that fails silently is a time bomb: fallbacks serve stale data, retries mask a dying database, and everything looks fine while the incident grows. Today: **logs** (what happened), **metrics** (how much / how fast), **traces** (where the time went), and **alerts** (wake a human when it matters).

**How to use this class:** open `index.html` for the interactive page — 24 diagrams, 14 scenario quizzes (each one placed *before* its topic: think first, then the concept lands as the answer), and a runnable-demo runbook. Everything is beginner-first. Runnable demos live in [`code/`](code/): two need nothing but `python3`; two need a 30-second venv (structlog + Django).

---

## The problem: the outage you couldn't see
Your LLD-38 circuit breaker tripped at 3:07 AM and protected the system beautifully… and nobody knew until customers tweeted at 9. Without telemetry your system is a **black box**: which service? which query? since when? — you're left with ssh and guesswork.

- **Observability** = the ability to ask *new questions of a running system without shipping new code*. Instrument once; query at 3 AM.
- **Monitoring** = watching known numbers against known thresholds. You need both: monitoring catches the fire, observability finds where it started.

**The three pillars:** LOGS answer *"what happened?"* (one line per event) · METRICS answer *"how much / how fast?"* (cheap numbers over time) · TRACES answer *"where did the time go?"* (one request's journey across services). DASHBOARDS + ALERTS sit on top and get a human involved.

## Pillar 1 — Logs (from `print()` to production)
`print()` dies in production: no severity, no context, no off-switch, one destination. Python's `logging` is four Lego pieces: **Logger → Level gate → Handler(s) → Formatter(s)**. One event can hit the console as text *and* a file/aggregator as JSON.

| Level | Means | In prod? |
|---|---|---|
| `DEBUG` | diagnostic detail for developers | OFF — flip on to chase a bug |
| `INFO` | normal business events (`order 991 created`) | ON — your audit trail |
| `WARNING` | surprising but handled (`retry 2/3 after timeout`) | ON — the "keep an eye on this" channel |
| `ERROR` | an operation failed (+ traceback via `log.exception`) | ON — someone looks today |
| `CRITICAL` | the service itself is dying | ON — this should page |

```python
log = logging.getLogger(__name__)
log.info("order %s created by user %s", order_id, user_id)   # lazy %s — no cost when level is off
try:
    charge(card)
except Exception:
    log.exception("charge failed for order %s", order_id)    # traceback attached, free
```

- **Structured (JSON) logs:** production is fifty processes streaming into an aggregator, and the reader is a *query engine* — give it **fields**, not prose. `structlog` binds context once (`request_id`, `user_id`) and stamps every subsequent line.
- **Correlation IDs:** mint a random ID at the edge (or honor incoming `X-Request-ID`), stamp every log line, pass it on every outbound call, echo it in the response. Then `grep ab12` reads one request's whole story across services.
- **Aggregation:** apps log JSON to **stdout** (12-factor); an agent ships it to a store behind one search box. On a bare VM, rotation is your job (`RotatingFileHandler`) or the disk fills. Cost levers: right levels → sampling (keep 1% of boring 200s, 100% of errors) → 7–30 days hot, archive the rest.
- **The ELK stack, letter by letter:** **E**lasticsearch = the database (stores every line + builds the *inverted index*: word → which lines contain it — a book's index at fleet scale); **L**ogstash (today usually lighter Beats/Fluent Bit) = the mover (tail stdout, parse to fields, enrich, ship); **K**ibana = the face (field-query search bar, histograms, dashboards, alerting). Lighter cousin, same roles: Fluent Bit → **Loki** (indexes only labels — cheaper) → Grafana.
- **Why not just Postgres?** `LIKE '%…%'` can't use a B-tree (left wildcard) → scans all 2B rows every search (~40 min). The inverted index turns the same search into a dictionary lookup + a few fetches (~200 ms). The trade: heavier writes + more disk — correct for logs (written once, searched thousands of times). Postgres *can* do it (`tsvector` + GIN); ES is that idea productized, distributed, with Kibana as its face.
- **f-string vs lazy `%s`, the rule:** f-strings *everywhere* — except inside log calls, where lazy `%s` wins: `log.debug("cart %s", cart)` skips the formatting entirely when DEBUG is off, and the constant template lets aggregators group all "cart …" lines as one event. (Exception messages, cache keys, joined loops: f-string / `join` — they're always needed anyway.)
- **The never-log list:** passwords & attempts, session tokens/JWTs, API keys, full card numbers/CVV (PCI), government IDs, health data, PII like emails (GDPR — log `user_id=42`, not the email). Mask at the formatter, never at fifty call sites.
- **The five logging sins:** logging the never-list · ERROR-spam for handled retries · log-and-rethrow at every layer (same traceback ×4) · INFO in a hot loop · prose without fields.

## Pillar 2 — Metrics (the numbers that run the dashboard)
Metrics throw the stories away and keep counts and timings — cheap enough to record every second and alert on. Three shapes: **Counter** (only up: `requests_total`), **Gauge** (up/down: `queue_depth`), **Histogram** (durations → percentiles; the rarer **Summary** pre-computes percentiles but can't aggregate across instances). Start with **RED** per endpoint: **R**ate, **E**rrors, **D**uration — or Google SRE's **Four Golden Signals** (Latency, Traffic, Errors, **Saturation** — the early-warning signal RED misses: pool usage, queue depth).

```promql
rate(http_requests_total[5m])                                   # req/s
rate(http_requests_total{status=~"5.."}[5m])
  / rate(http_requests_total[5m]) * 100                         # error %
histogram_quantile(0.99, rate(http_request_seconds_bucket[5m])) # p99
```
Every Grafana panel and alert rule is one of these expressions with a threshold.

**Percentiles, not averages:** an average of 90ms can hide a p99 of 1.2s — and at ~30 requests per session, "1 in 100 requests slow" ≈ 1 in 4 *sessions* hurt. Dashboards graph p95/p99 because that's where users actually suffer.

**The pull model:** your app exposes `GET /metrics` (via `prometheus-client` / `django-prometheus`); **Prometheus** scrapes every 15s and stores time series; **Grafana** draws; **Alertmanager** pages. Watch label cardinality — never label by `user_id`.

## Pillar 3 — Traces (where did the time go?)
Metrics say checkout p95 jumped; every service's own logs look fine-ish. A **trace** is one request's journey as a tree of timed **spans** — the waterfall shows *which hop* ate the time in one glance. Context travels in the W3C `traceparent` header (the correlation-ID trick, standardized, plus timing); **OpenTelemetry** auto-instruments Django/httpx/psycopg and exports to Jaeger/Tempo/Datadog. Sampling keeps ~1–10% (ideally tail-sampled: always keep slow/error traces).

## Alerts — waking humans, carefully
- **Page on symptoms** users feel (error rate, latency); **ticket the causes** that can wait (disk 82% full, growing 1%/day). Every unactionable page erodes trust — **alert fatigue** has caused more long outages than missing alerts.
- Anatomy of a rule: a user-facing ratio + threshold + **FOR duration** (sustained, not a blip — the anti-flapping clause) + severity routing + a runbook link.
- **Four tests of a good page:** Actionable · Urgent · Clear (context + runbook) · Rare. Track pages/week as a metric; review every page weekly (keep/tune/delete). Real incidents get **blameless postmortems** — blame teaches people to hide what they saw.
- **SLI / SLO / SLA:** **S**ervice **L**evel **I**ndicator (a measured ratio of good events), **O**bjective (your promise about the SLI — internal target), **A**greement (the same promise with a contract and refunds — legal). SLO 99.9%/month ⇒ a 43.8-min **error budget**. Budget nearly burned → freeze risky ships; untouched → ship faster. The speed-vs-safety war, settled by arithmetic (Google SRE).

## The ecosystem (60-second history)
syslog & grep → **ELK** industrialized log search (2010s) → **Prometheus** (SoundCloud 2012, CNCF #2) + **Grafana** became the metrics standard → Dapper (2010) → Zipkin/Jaeger → **OpenTelemetry** (2019 merge; 2nd-most-active CNCF project) unified instrumentation for all three pillars. SaaS: Datadog (all-in-one), Splunk (enterprise logs), **Sentry** (errors — started as a Django plugin), Honeycomb.
**Python toolbelt:** stdlib `logging` · `structlog`/`django-structlog` (JSON + request IDs) · `loguru` · `prometheus-client`/`django-prometheus` · `opentelemetry-*` · `sentry-sdk`.

## Observability in the AI era
An LLM app is a distributed system whose flakiest, priciest dependency happens to think. Everything transfers: logs = each model/tool call as an event (with a new **content-redaction** problem — prompts carry PII); metrics = RED **plus tokens/sec, cost/day, cache-hit rate, eval scores** (teams alert on *cost burn rate* like an error budget); traces = the agent loop as a span waterfall (OTel GenAI conventions; LangSmith/Langfuse); alerts = 429 storms, time-to-first-token, **eval-score drift** — because LLMs fail *plausibly*, not loudly, quality itself becomes a monitored signal.

---

## `code/` — runnable demos

| File | Runs with | Demonstrates |
|---|---|---|
| [`logging_basics.py`](code/logging_basics.py) | `python3` (no installs) | 7 chapters: print → logger/handler/formatter/levels, two destinations, `log.exception` tracebacks, correlation-ID filter, secret masking, lazy `%s` vs f-string |
| [`alert_watcher.py`](code/alert_watcher.py) | `python3` (no installs) | A real sliding-window alert rule (>5% errors FOR 10s → PAGE, recovery → RESOLVED) over a simulated incident |
| [`structured_logging.py`](code/structured_logging.py) | venv + structlog | The same events as text vs JSON; `bind()` context once; a checkout flow with `duration_ms` and a failure |
| [`django_request_logging.py`](code/django_request_logging.py) | venv + Django | Single-file Django app: middleware mints/honors `X-Request-ID`, logs one JSON line per request (method/path/status/duration_ms), echoes the ID; `/ok`, `/slow`, `/boom` |

```bash
cd code
python3 logging_basics.py           # stdlib — the whole logging tour
python3 alert_watcher.py            # stdlib — watch a page fire & resolve

python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt     # structlog + Django
python3 structured_logging.py
python3 django_request_logging.py runserver 127.0.0.1:8039 --noreload
# second terminal:
curl -i localhost:8039/ok           # JSON log line + X-Request-ID header
curl -i -H "X-Request-ID: test-123" localhost:8039/slow    # honored end-to-end
curl -i localhost:8039/boom         # 500: traceback logged, request line still emitted
```
> Verified against Python 3.14, structlog 26.1, Django 6.0. All scripts print ASCII-only, write nothing outside their own directory, and log to stdout (the 12-factor way).

## Homework
1. **Logging tour:** run `logging_basics.py`; set the console handler to DEBUG and feel the noise; write the token-masking line yourself.
2. **JSON logs:** add `cart_size` and one more `duration_ms` to `structured_logging.py`; write (in words) the query that finds failed payments over $100.
3. **Middleware:** curl `django_request_logging.py` with your own `X-Request-ID`; add a view that logs WARNING when `duration_ms > 1000`.
4. **Alert tuning:** in `alert_watcher.py`, try 2%/2s (count the flapping) then 10%/30s (how late is the page?). Write down the trade-off you just felt.
5. **Audit something real:** in any project you've built — which remote calls log nothing on failure? Add one correlation ID and one WARNING you wish you'd had.

**Next class — Containerization:** the service is tested, secure, async, resilient, observable… and runs on *your* machine. Docker: package the app + dependencies + config contract into an image that runs identically everywhere. (The 12-factor config from LLD-38 and today's stdout-logging rule were both quietly preparing you for this.)
