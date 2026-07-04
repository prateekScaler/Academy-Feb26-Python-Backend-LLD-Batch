"""
07 — Beyond asserts: grading non-deterministic outputs (an evals teaser)
========================================================================

Everything so far had ONE right answer:   assert actual == expected.

Now imagine the function calls an LLM — "summarize this ticket".
Run it twice, get two different (both fine!) answers. There is no
`expected` to == against. Equality-testing is DEAD here. What replaces it?

    assert  →  GRADE.   score the output against a RUBRIC (0..1),
                        require score ≥ threshold,
                        and require the PASS RATE over many runs ≥ target.

That is an EVAL. Same skeleton as a test — Arrange, Act, Assert — but the
assert is statistical. This file fakes the "model" with a seeded stub so
you can see the machinery with zero API calls. The real thing (rubrics,
LLM-as-judge, regression sets) gets its own session later this module.

Run me:
    python3 07_beyond_asserts_evals_teaser.py
    pytest -v 07_beyond_asserts_evals_teaser.py
"""

# ────────────────────────── run-anywhere shim ──────────────────────────
# In class we use the real `pytest`. This tiny stand-in only exists so the
# file also runs with plain `python3` on a machine without pytest. Skip it.
try:
    import pytest
except ImportError:
    class _Raises:
        def __init__(self, exc): self.exc = exc
        def __enter__(self): return self
        def __exit__(self, t, v, tb):
            assert t is not None and issubclass(t, self.exc), \
                f"expected {self.exc.__name__}, got {t.__name__ if t else 'no error'}"
            self.value = v
            return True
    class _Approx:
        def __init__(self, v, tol): self.v, self.tol = v, tol
        def __eq__(self, o): return abs(o - self.v) <= self.tol
        def __repr__(self): return f"approx({self.v})"
    class _Mark:
        @staticmethod
        def parametrize(names, cases):
            def deco(fn): fn._params = (names, cases); return fn
            return deco
    class pytest:
        mark = _Mark
        @staticmethod
        def raises(exc): return _Raises(exc)
        @staticmethod
        def approx(v, rel=None, abs=None):
            tol = abs if abs is not None else (rel if rel is not None else 1e-6) * max(1.0, v if v >= 0 else -v)
            return _Approx(v, tol)
        @staticmethod
        def fixture(fn=None, **kw):
            def deco(f): f._fixture = True; return f
            return deco(fn) if fn else deco
# ───────────────────────── end shim · lesson begins ─────────────────────


import random

TICKET = ("Customer paid twice for order #4521 after a payment-gateway "
          "timeout. Refund the duplicate charge of Rs 1499 and notify "
          "the customer by email.")

REQUIRED_FACTS = ["4521", "1499", "refund"]      # must survive summarization
MAX_WORDS = 25


def summarize(text: str, seed: int) -> str:
    """A stand-in 'model': non-deterministic (varies by seed), usually
    good, occasionally sloppy — just like the real thing."""
    rng = random.Random(seed)
    styles = [
        "Refund duplicate Rs 1499 charge on order #4521; email the customer.",
        "Order #4521 was double-charged (Rs 1499). Issue refund and email customer.",
        "Double payment on #4521 due to gateway timeout - refund Rs 1499, notify by email.",
        "Customer double-charged. Refund needed for order #4521 amount Rs 1499.",
        "Gateway timeout caused a duplicate payment. Please refund and email the customer.",  # forgot ids!
    ]
    return styles[rng.randrange(len(styles))]


# ── the grader: a rubric, not an equality ──

def grade(summary: str) -> float:
    """Score 0..1: keeps the key facts, stays short."""
    text = summary.lower()
    facts_kept = sum(1 for fact in REQUIRED_FACTS if fact in text)
    fact_score = facts_kept / len(REQUIRED_FACTS)            # 0, ⅓, ⅔, 1
    length_ok = 1.0 if len(summary.split()) <= MAX_WORDS else 0.5
    return fact_score * length_ok


# ─────────────────── the eval (a statistical test) ───────────────────

def test_single_good_output_scores_full_marks():
    # graders need tests too! pin the rubric on a known-good answer
    s = "Refund duplicate Rs 1499 charge on order #4521; email the customer."
    assert grade(s) == 1.0


def test_grader_penalises_a_summary_that_drops_the_facts():
    s = "Gateway timeout caused a duplicate payment. Please refund."
    assert grade(s) < 0.5                       # lost #4521 and 1499


def test_summarizer_pass_rate_is_at_least_80_percent():
    # THE paradigm shift: no equality anywhere. Run many seeds, grade
    # each, threshold the PASS RATE. One sloppy output does not fail
    # the suite — a degraded MODEL does.
    scores = [grade(summarize(TICKET, seed)) for seed in range(20)]
    pass_rate = sum(1 for s in scores if s >= 0.7) / len(scores)

    assert pass_rate >= 0.80, f"pass rate fell to {pass_rate:.0%}"


def test_worst_case_still_produces_something_short():
    # even the sloppy style must respect the hard constraint
    scores_lengths = [len(summarize(TICKET, seed).split()) for seed in range(20)]
    assert max(scores_lengths) <= MAX_WORDS


# ───────────────── standalone runner (python3 file.py) ─────────────────

def _run_standalone():
    import inspect
    g = dict(globals())
    fixtures = {n: f for n, f in g.items() if getattr(f, "_fixture", False)}
    passed = failed = 0
    for name, fn in sorted(g.items()):
        if not (name.startswith("test_") and callable(fn)):
            continue
        names, cases = getattr(fn, "_params", (None, [None]))
        for case in cases:
            kwargs, label, gens = {}, name, []
            if names:
                vals = case if isinstance(case, tuple) else (case,)
                kwargs = dict(zip([s.strip() for s in names.split(",")], vals))
                label = f"{name}[{', '.join(map(repr, vals))}]"
            for p in inspect.signature(fn).parameters:
                if p not in kwargs and p in fixtures:
                    r = fixtures[p]()
                    if inspect.isgenerator(r):
                        gens.append(r); r = next(r)
                    kwargs[p] = r
            try:
                fn(**kwargs); print(f"  PASS  {label}"); passed += 1
            except Exception as e:                              # noqa: BLE001
                print(f"  FAIL  {label}  ->  {e}"); failed += 1
            for gen in gens:
                try: next(gen)
                except StopIteration: pass
    print(f"\n{passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    import sys
    print(__doc__.strip().splitlines()[0])
    print()
    if hasattr(pytest, "main"):
        sys.exit(pytest.main([__file__, "-v", "-p", "no:cacheprovider"]))
    sys.exit(_run_standalone())
