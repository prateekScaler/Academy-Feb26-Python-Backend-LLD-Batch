"""
07 — Evals: grading non-deterministic (LLM) outputs
===================================================

The evals deep-dive promised in LLD-31. Two layers, cleanly separated:

  (A) UNIT-test the code AROUND the model with the model MOCKED — the
      prompt building, parsing, fallbacks. Deterministic, fast, free.
  (B) EVAL the model's QUALITY on a GOLDEN SET — grade each output against
      a rubric, and assert the PASS RATE, not any single answer.

Here the "model" is a seeded stub so everything runs offline. Swap it for
a real client and the eval structure is unchanged.

Needs:  pip install pytest
"""

import random
from unittest.mock import Mock
import pytest


# ── the code under test: summarize a support ticket via an LLM ──

REQUIRED_FACTS = ["#4521", "1499", "refund"]
MAX_WORDS = 25


def summarize_ticket(llm, ticket: str) -> str:
    """Build a prompt, call the model, tidy the output. The LLM is injected."""
    prompt = f"Summarize in <= {MAX_WORDS} words, keep IDs and amounts:\n{ticket}"
    return llm.complete(prompt).strip()


# ── layer A: unit tests with the LLM MOCKED (deterministic) ──

def test_summarize_passes_the_ticket_and_trims_whitespace():
    llm = Mock()
    llm.complete.return_value = "  Refund #4521 for 1499.  "
    assert summarize_ticket(llm, "long ticket text...") == "Refund #4521 for 1499."
    # and we can assert the ticket made it into the prompt:
    (prompt,), _ = llm.complete.call_args
    assert "long ticket text" in prompt


# ── layer B: the eval — a rubric grader + a golden set + a pass rate ──

def grade(summary: str) -> float:
    """Rubric score 0..1: keeps the key facts AND stays short."""
    text = summary.lower()
    facts = sum(1 for f in REQUIRED_FACTS if f.lower() in text) / len(REQUIRED_FACTS)
    length_ok = 1.0 if len(summary.split()) <= MAX_WORDS else 0.5
    return facts * length_ok


def judge_is_professional(summary: str) -> bool:
    """A stand-in for an LLM-as-judge: a second, softer quality gate.
    (In production this is another model call; here it's deterministic.)"""
    banned = ["stupid", "lol", "idk"]
    return not any(b in summary.lower() for b in banned)


def stub_model(ticket: str, seed: int) -> str:
    """A seeded 'model' — usually good, occasionally drops an id (like the real thing)."""
    rng = random.Random(seed)
    good = [
        "Refund the duplicate 1499 charge on #4521; email the customer.",
        "#4521 was double-charged (1499). Issue refund and notify by email.",
        "Duplicate payment on #4521 due to gateway timeout - refund 1499.",
    ]
    sloppy = "Gateway timeout caused a duplicate payment; please refund the customer."
    return rng.choice(good + good + good + [sloppy])   # ~1 in 10 is sloppy


def test_grader_itself_is_unit_tested():
    # the grader is code, so it gets ordinary tests — pin it on known outputs
    assert grade("Refund #4521 for 1499.") == 1.0
    assert grade("Gateway timeout; please refund.") < 0.5     # dropped the ids


GOLDEN_TICKETS = [f"ticket seed {i}" for i in range(20)]      # the regression set


def test_summarizer_pass_rate_is_at_least_80_percent():
    scores = [grade(stub_model(t, seed=i)) for i, t in enumerate(GOLDEN_TICKETS)]
    pass_rate = sum(1 for s in scores if s >= 0.7) / len(scores)
    assert pass_rate >= 0.80, f"quality regressed: pass rate {pass_rate:.0%}"


def test_every_output_clears_the_judge_and_length_gate():
    for i, t in enumerate(GOLDEN_TICKETS):
        out = stub_model(t, seed=i)
        assert judge_is_professional(out)
        assert len(out.split()) <= MAX_WORDS


if __name__ == "__main__":
    try:
        import pytest as _pt
    except ImportError:
        raise SystemExit("This is a pytest test file. Install pytest first:  pip install pytest")
    raise SystemExit(_pt.main([__file__, "-v", "-p", "no:cacheprovider"]))
