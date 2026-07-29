"""
LLD-39 | Logging & Monitoring -- Demo 1: logging_basics.py
=========================================================

A guided tour of Python's built-in `logging` module, told as 7 chapters.

    Run it:   python3 logging_basics.py      (stdlib only -- no installs!)

Why do we even need a logging MODULE? Isn't print() enough?
Run the file. Each chapter answers one piece of that question.

The big mental model to keep in your head the whole time:

    Logger  --->  Handler(s)  --->  Formatter  --->  Destination
    "who is       "where does      "what does       (console, file,
     talking"      it go"           a line look      network, ...)
                                    like"

    ...and LEVELS are the volume knob that filters what gets through.
"""

import contextvars
import logging
import os
import sys

# ---------------------------------------------------------------------------
# IMPORTANT: never trust the "current working directory" in real services.
# A cron job, a systemd unit and your terminal all start your script from
# DIFFERENT directories. So we anchor every file path to the script itself.
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
DEMO_LOG_PATH = os.path.join(HERE, "demo.log")

# Fresh run, fresh log file -- delete leftovers from a previous run.
if os.path.exists(DEMO_LOG_PATH):
    os.remove(DEMO_LOG_PATH)


def banner(title: str) -> None:
    """Plain-ASCII chapter banner (no emojis -- logs must survive dumb terminals)."""
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


# ===========================================================================
# CHAPTER 1 -- Why print() fails in production
# ===========================================================================
banner("CHAPTER 1: why print() fails in production")

# This is how most of us start debugging:
print("starting payment")
print("something went wrong!!")
print("payment done??")

print("""
Look at those three lines. Now imagine 50,000 of them per minute and answer:
  - WHEN did each happen?            (no timestamp)
  - HOW BAD is "something went wrong"? A typo? Money lost?   (no severity)
  - WHICH module said it?            (no source name)
  - Can I turn the noisy ones off without editing code?      (no off-switch)
  - Can I grep only the errors?      (no level to grep by)
print() answers NONE of these. The logging module answers ALL of them.
""")


# ===========================================================================
# CHAPTER 2 -- The anatomy: Logger -> Handler -> Formatter -> Level
# ===========================================================================
banner("CHAPTER 2: the anatomy -- Logger -> Handler -> Formatter")

# 1) A LOGGER is the object your code talks to. Convention: name it after
#    the module, so every line automatically says who produced it.
logger = logging.getLogger("shop.payments")
logger.setLevel(logging.DEBUG)      # the logger's own volume knob
logger.propagate = False            # keep this demo self-contained

# 2) A HANDLER decides WHERE log records go. StreamHandler => console.
console = logging.StreamHandler(sys.stdout)

# 3) A FORMATTER decides WHAT each line looks like. These %(...)s fields
#    are filled in from the LogRecord automatically -- for free, every line.
fmt = logging.Formatter("%(asctime)s %(levelname)-8s %(name)s - %(message)s")
console.setFormatter(fmt)

# Wire them together: logger -> handler (a logger can have MANY handlers)
logger.addHandler(console)

logger.info("payment started for order #4021")
logger.warning("payment gateway slow (took 2.3s)")

print("\nSame effort as print(), but every line now carries")
print("timestamp + severity + source. That is the whole trade.")


# ===========================================================================
# CHAPTER 3 -- The five levels (and the off-switch print() never had)
# ===========================================================================
banner("CHAPTER 3: the five levels -- DEBUG/INFO/WARNING/ERROR/CRITICAL")

lvl = logging.getLogger("shop.levels")
lvl.setLevel(logging.DEBUG)                 # first pass: let EVERYTHING through
lvl.propagate = False
h = logging.StreamHandler(sys.stdout)
h.setFormatter(logging.Formatter("%(levelname)-8s | %(message)s"))
lvl.addHandler(h)

print("-- with level=DEBUG (development mode) --")
lvl.debug("DEBUG:    cart contents = [book, pen]  (chatty detail, dev only)")
lvl.info("INFO:     order #4021 placed            (normal business events)")
lvl.warning("WARNING:  retrying gateway, attempt 2/3 (odd, but self-healed)")
lvl.error("ERROR:    payment failed for #4021      (a request DIED, act soon)")
lvl.critical("CRITICAL: cannot reach database        (whole service down, page!)")

# Now the magic: ONE line of config silences the chatty stuff. No code edits.
lvl.setLevel(logging.INFO)
print("\n-- same code, but level=INFO (production mode) --")
lvl.debug("DEBUG:    cart contents = [book, pen]   <-- this line VANISHES")
lvl.info("INFO:     order #4022 placed")

print("\nNotice: the DEBUG line disappeared. That is the off-switch.")


# ===========================================================================
# CHAPTER 4 -- Two handlers, two audiences (console vs file)
# ===========================================================================
banner("CHAPTER 4: two handlers -- console gets INFO+, demo.log gets DEBUG+")

# Real setups do exactly this: humans watching the console see the summary,
# while the file (or log agent) keeps the full forensic detail for later.
dual = logging.getLogger("shop.dual")
dual.setLevel(logging.DEBUG)        # logger lets everything pass DOWN to handlers
dual.propagate = False

console_h = logging.StreamHandler(sys.stdout)
console_h.setLevel(logging.INFO)    # console: only INFO and above
console_h.setFormatter(logging.Formatter("CONSOLE %(levelname)-8s %(message)s"))

file_h = logging.FileHandler(DEMO_LOG_PATH)   # explicit path -- NOT cwd-relative!
file_h.setLevel(logging.DEBUG)      # file: everything, including DEBUG
file_h.setFormatter(
    logging.Formatter("%(asctime)s %(levelname)-8s %(name)s - %(message)s")
)

dual.addHandler(console_h)
dual.addHandler(file_h)

dual.debug("loading inventory cache (247 items)")      # file only
dual.debug("user 88 session validated")                # file only
dual.info("order #4023 placed, total = 499.00 INR")    # both
dual.error("refund webhook returned HTTP 503")         # both

file_h.flush()
print("\nThe two DEBUG lines above did NOT hit your console.")
print(f"But look inside {os.path.basename(DEMO_LOG_PATH)} -- nothing was lost:\n")
with open(DEMO_LOG_PATH, "r", encoding="utf-8") as f:
    for line in f.readlines()[-4:]:
        print("   demo.log | " + line.rstrip())


# ===========================================================================
# CHAPTER 5 -- logger.exception(): tracebacks for free
# ===========================================================================
banner("CHAPTER 5: logger.exception() -- the traceback rides along for free")

exc_log = logging.getLogger("shop.errors")
exc_log.setLevel(logging.DEBUG)
exc_log.propagate = False
eh = logging.StreamHandler(sys.stdout)
eh.setFormatter(logging.Formatter("%(levelname)-8s %(name)s - %(message)s"))
exc_log.addHandler(eh)

try:
    items, coupons = 5, 0
    per_coupon = items / coupons          # boom: ZeroDivisionError
except ZeroDivisionError:
    # logger.exception() == logger.error() + the FULL traceback, automatically.
    # No need to pass the exception object; it reads the one being handled.
    exc_log.exception("discount calculation blew up (items=%s, coupons=%s)", 5, 0)

print("\nOne call captured message + stack trace. In prod, that traceback")
print("is the difference between a 5-minute fix and a 3-hour guessing game.")


# ===========================================================================
# CHAPTER 6 -- Correlation IDs: grep one request's WHOLE story
# ===========================================================================
banner("CHAPTER 6: correlation IDs -- tag every line with the request it belongs to")

# Problem: in a busy server, lines from 100s of concurrent requests INTERLEAVE.
# "Which of these 40 ERROR lines belongs to Rahul's checkout?" -- impossible...
# unless every line carries the id of the request that produced it. Then:
#     grep req-b7f2 app.log        <- the full story of ONE request, in order.
#
# A contextvar holds "the current request's id" safely per-request (it works
# per-thread AND per-async-task, which plain globals do not).
current_request_id = contextvars.ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    """Filters can VETO records -- but they can also ENRICH them.
    This one stamps the current request id onto every record passing through."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = current_request_id.get()
        return True     # True = "let the record through"


req_log = logging.getLogger("shop.requests")
req_log.setLevel(logging.DEBUG)
req_log.propagate = False
rh = logging.StreamHandler(sys.stdout)
# The formatter can now use %(request_id)s because the filter guarantees it.
rh.setFormatter(logging.Formatter("[%(request_id)s] %(levelname)-8s %(message)s"))
rh.addFilter(RequestIdFilter())
req_log.addHandler(rh)


def handle_checkout(request_id: str, user: str, fail: bool) -> None:
    """Pretend this runs once per incoming HTTP request."""
    current_request_id.set(request_id)     # middleware would do this in Django
    req_log.info("checkout started by %s", user)
    req_log.debug("cart validated, 3 items")
    if fail:
        req_log.error("card declined by gateway")
    else:
        req_log.info("payment captured OK")


# Two "requests" -- note how the code above NEVER passes the id to each log
# call, yet every line below is stamped with the right one.
handle_checkout("req-a1c9", user="rahul", fail=False)
handle_checkout("req-b7f2", user="meera", fail=True)

print("\nEvery line carries its request id -- set ONCE per request, attached")
print("automatically to all logs after. `grep req-b7f2` = Meera's whole story.")


# ===========================================================================
# CHAPTER 7 -- Anti-patterns: the two mistakes every beginner ships
# ===========================================================================
banner("CHAPTER 7: anti-patterns -- secrets in logs, and eager f-strings")

anti = logging.getLogger("shop.anti")
anti.setLevel(logging.INFO)            # note: DEBUG is OFF -- that matters below
anti.propagate = False
ah = logging.StreamHandler(sys.stdout)
ah.setFormatter(logging.Formatter("%(levelname)-8s %(message)s"))
anti.addHandler(ah)

# --- Anti-pattern (a): logging secrets --------------------------------------
# Logs get copied everywhere: aggregators, S3 backups, a teammate's laptop,
# sometimes a screenshot in Slack. A token in a log IS a leaked token.
api_token = "sk-live-8f2a9c1d4e7b6a3f9d0c5e8b"

# BAD  (never do this):  anti.info(f"calling gateway with token {api_token}")
# GOOD: mask it -- keep just enough to correlate ("which key was it?").
masked = api_token[:3] + "..." + api_token[-4:]     # sk-...5e8b
anti.info("calling gateway with token %s", masked)
print("        ^ enough to identify WHICH key, useless to an attacker")

# --- Anti-pattern (b): f-strings vs lazy %s formatting ----------------------
# logger.debug(f"...{expensive()}...")  builds the string EVEN IF debug is off,
# because Python evaluates the f-string BEFORE calling .debug().
# logger.debug("... %s ...", expensive_obj) only formats IF the line will emit.


class ExpensiveReport:
    """Pretend str() on this walks the whole database. We count the calls."""
    calls = 0

    def __str__(self) -> str:
        ExpensiveReport.calls += 1
        return "<report: 1,203,999 rows summarized>"


report = ExpensiveReport()

anti.debug(f"nightly report: {report}")     # BAD:  str() runs, line still dropped
eager_cost = ExpensiveReport.calls

anti.debug("nightly report: %s", report)    # GOOD: level is off -> str() never runs
lazy_cost = ExpensiveReport.calls - eager_cost

print(f"DEBUG is disabled, yet the f-string called str() {eager_cost} time(s).")
print(f"The lazy '%s' version called str() {lazy_cost} time(s). That is work")
print("your production server does for log lines NOBODY will ever see.")


# ===========================================================================
banner("THE END -- what to remember")
print("""1. print() has no time, no severity, no source, no off-switch. logging has all.
2. Logger (who) -> Handler (where) -> Formatter (what it looks like).
3. Levels are a volume knob: DEBUG dev-noise ... CRITICAL wake-someone-up.
4. Different handlers can have different levels (console brief, file full).
5. logger.exception() inside `except` = message + traceback, free.
6. A Filter + contextvar stamps a request id on every line -> grep one request.
7. Never log secrets (mask them); prefer lazy '%s' args over f-strings in logs.

Next demo (structured_logging.py): turning these lines into JSON so
MACHINES can query them, not just humans with grep.""")
