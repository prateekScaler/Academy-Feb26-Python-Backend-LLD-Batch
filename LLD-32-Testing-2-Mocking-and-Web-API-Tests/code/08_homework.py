"""
08 — HOMEWORK: you write the tests (mocking & evals)
====================================================

The code under test is COMPLETE and CORRECT — you only write the tests.
Every exercise is a `pytest.skip(...)` stub: delete the skip line and write
the real test. Go from all-skipped to all-green.

    pytest -v 08_homework.py     ->  s s s ...   then   . . . (all PASSED)

Skills (this class):
  * inject a hand-written double / fake        (model: file 01, 06)
  * monkeypatch a function / env var           (model: file 02)
  * Mock: return_value, side_effect            (model: file 03)
  * patch.object where the name is looked up   (model: file 04)
  * spy: assert_called_once_with, not_called   (model: file 05)
  * evals: grade + golden-set pass rate        (model: file 07)

Needs:  pip install pytest
"""

import os
import sys
import random
from unittest.mock import Mock, patch
import pytest

THIS = sys.modules[__name__]


# ═══════════════════════ the code under test ═══════════════════════

class RefundError(Exception):
    pass


class RefundService:
    """Refund an order, then email a confirmation. A failed refund sends
    no email and returns None."""
    def __init__(self, gateway, mailer):
        self.gateway = gateway
        self.mailer = mailer

    def refund(self, amount_paise: int, email: str):
        try:
            receipt = self.gateway.refund(amount_paise)
        except RefundError:
            return None
        self.mailer.send(to=email, subject="Refund processed")
        return receipt


class InMemoryLedger:
    """A FAKE ledger — a real implementation backed by a list."""
    def __init__(self):
        self.entries: list[tuple[str, int]] = []
    def record(self, kind: str, amount_paise: int) -> None:
        self.entries.append((kind, amount_paise))
    def total(self, kind: str) -> int:
        return sum(a for k, a in self.entries if k == kind)


def region_tax_rate() -> float:
    raise RuntimeError("real call to a tax-rate service")


def gross_paise(net_paise: int) -> int:
    return round(net_paise * (1 + region_tax_rate()))


def coupon_code() -> str:
    return random.choice(["SAVE10", "SAVE20", "FREESHIP"])


def summarize(llm, text: str) -> str:
    return llm.complete(f"Summarize: {text}").strip()


REQUIRED = ["order", "1499"]
def grade(summary: str) -> float:
    t = summary.lower()
    return sum(1 for r in REQUIRED if r in t) / len(REQUIRED)


def stub_model(text: str, seed: int) -> str:
    rng = random.Random(seed)
    good = ["Refund order 1499 done.", "Order refunded: 1499.", "1499 refund on the order."]
    return rng.choice(good + good + good + ["Refund completed for the customer."])


# ═════════════════════════ the exercises ═════════════════════════

# ── Part 1 · doubles & injection (files 01, 06) ──

def test_ex01_refund_returns_the_gateways_receipt():
    # Inject a Mock (or hand-written fake) gateway whose refund() returns
    # "rcpt_7"; a Mock mailer. Assert RefundService(...).refund(...) == "rcpt_7".
    pytest.skip("TODO ex01")


def test_ex02_ledger_fake_records_the_refund_amount():
    # Use the InMemoryLedger fake directly: record("refund", 1499),
    # record("refund", 500), assert total("refund") == 1999.
    pytest.skip("TODO ex02")


# ── Part 2 · monkeypatch (file 02) ──

def test_ex03_monkeypatch_the_tax_rate(monkeypatch):
    # region_tax_rate() raises. monkeypatch.setattr it to return 0.18,
    # then assert gross_paise(1000) == 1180.
    pytest.skip("TODO ex03")


def test_ex04_monkeypatch_random_for_a_stable_coupon(monkeypatch):
    # coupon_code() uses random.choice. Pin it so the result is deterministic,
    # then assert it.
    pytest.skip("TODO ex04")


# ── Part 3 · Mock return_value / side_effect (file 03) ──

def test_ex05_side_effect_makes_the_refund_fail():
    # Give a Mock gateway .refund.side_effect = RefundError. Assert the
    # service returns None AND the mailer was NOT called (assert_not_called).
    pytest.skip("TODO ex05")


# ── Part 4 · patch.object, where it's looked up (file 04) ──

def test_ex06_patch_object_the_tax_rate():
    # Same as ex03 but with patch.object(THIS, "region_tax_rate", ...)
    # as a context manager. Assert gross_paise(1000) == 1180.
    pytest.skip("TODO ex06")


# ── Part 5 · spying (file 05) ──

def test_ex07_refund_emails_the_customer_once():
    # Mock gateway + mailer. After a successful refund, assert the mailer
    # was called exactly once with to=<email>, subject="Refund processed".
    pytest.skip("TODO ex07")


# ── Part 6 · evals (file 07) ──

def test_ex08_unit_test_summarize_with_a_mocked_llm():
    # Mock the llm: .complete.return_value = "  Order 1499 refunded.  ".
    # Assert summarize(llm, "...") strips the whitespace, AND assert the
    # text was passed into the prompt (inspect llm.complete.call_args).
    pytest.skip("TODO ex08")


def test_ex09_grader_scores_a_good_and_a_bad_summary():
    # Assert grade("Order 1499 refunded.") == 1.0 and grade("Done.") == 0.0.
    pytest.skip("TODO ex09")


def test_ex10_summarizer_pass_rate_over_the_golden_set():
    # Score stub_model on seeds 0..19, assert the pass rate (score == 1.0)
    # is at least 0.8.
    pytest.skip("TODO ex10")


if __name__ == "__main__":
    try:
        import pytest as _pt
    except ImportError:
        raise SystemExit("This is a pytest test file. Install pytest first:  pip install pytest")
    raise SystemExit(_pt.main([__file__, "-v", "-p", "no:cacheprovider"]))
