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
    pytest -v 07_beyond_asserts_evals_teaser.py
    python3 07_beyond_asserts_evals_teaser.py        # same thing — it hands over to pytest

Needs:  pip install pytest
"""


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


if __name__ == "__main__":
    # This file IS a pytest suite — running it directly just hands over to pytest.
    try:
        import pytest
    except ImportError:
        raise SystemExit("This is a pytest test file. Install pytest first:  pip install pytest")
    raise SystemExit(pytest.main([__file__, "-v", "-p", "no:cacheprovider"]))
