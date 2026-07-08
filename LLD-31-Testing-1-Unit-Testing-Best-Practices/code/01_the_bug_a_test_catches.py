"""
01 — The bug a test catches
===========================

The motivating story. Your food-delivery checkout applies two discounts:
a 10% offer and a Rs 50 coupon. The business rule says:

    percentage on the subtotal FIRST, then the flat coupon
    Rs 500 order  ->  500 x 0.9 - 50  =  Rs 400

During a refactor, someone reorders the two lines:

    (500 - 50) x 0.9  =  Rs 405        <- every discounted order now
                                          overcharges by Rs 5

Nothing crashes. Every screen renders. The PR looks tidy and gets merged.
Support tickets pile up in week three.

Nobody notices — unless a TEST pins the behaviour down. That is what tests
are for: not proving the code works today, but *keeping* it working tomorrow.

(Money is in integer paise — the exactness lesson from file 05.)

Run me:
    pytest -v 01_the_bug_a_test_catches.py
    python3 01_the_bug_a_test_catches.py        # same thing — it hands over to pytest

Needs:  pip install pytest
"""


# ── The CORRECT implementation: percentage first, then the flat coupon ──

def checkout_total(subtotal_paise: int, pct: int, coupon_paise: int) -> int:
    """Business rule: the % offer discounts the SUBTOTAL; the flat coupon
    comes off after. Never below zero. ₹500, 10%, ₹50 → ₹400."""
    after_pct = subtotal_paise - (subtotal_paise * pct) // 100
    return max(0, after_pct - coupon_paise)


# ── The "tidy refactor" (the bug): coupon first, then the percentage ──

def checkout_total_refactored(subtotal_paise: int, pct: int, coupon_paise: int) -> int:
    """What the refactor produced. Looks equivalent. Overcharges."""
    after_coupon = max(0, subtotal_paise - coupon_paise)
    return after_coupon - (after_coupon * pct) // 100     # ₹405, not ₹400


# ─────────────────────────── the tests ───────────────────────────
# One worked example from the business rule, pinned as an assert,
# catches the reorder forever.

def test_percentage_applies_to_subtotal_before_the_flat_coupon():
    # ₹500 order, 10% offer, ₹50 coupon → ₹400.00 exactly
    assert checkout_total(500_00, pct=10, coupon_paise=50_00) == 400_00


def test_discounts_never_push_the_total_below_zero():
    # ₹40 order with a ₹50 coupon is free — not ₹-10
    assert checkout_total(40_00, pct=0, coupon_paise=50_00) == 0


def test_no_discounts_means_no_change():
    assert checkout_total(500_00, pct=0, coupon_paise=0) == 500_00


def test_the_refactored_order_overcharges_which_is_why_the_suite_exists():
    # This test *documents the bug*: applying the coupon first inflates
    # the total by ₹5 on the worked example. If anyone "tidies" the code
    # back into this order, the first test above goes red in seconds —
    # not in production, three weeks later, via angry support tickets.
    correct = checkout_total(500_00, pct=10, coupon_paise=50_00)
    buggy = checkout_total_refactored(500_00, pct=10, coupon_paise=50_00)

    assert buggy == 405_00
    assert buggy - correct == 5_00            # the silent ₹5 overcharge


if __name__ == "__main__":
    # the demo: watch the refactor overcharge
    good = checkout_total(500_00, pct=10, coupon_paise=50_00)
    bad = checkout_total_refactored(500_00, pct=10, coupon_paise=50_00)
    print(f"  correct   : ₹500 · 10% off · ₹50 coupon → ₹{good/100:.2f}")
    print(f"  refactored: ₹500 · 10% off · ₹50 coupon → ₹{bad/100:.2f}   (₹5 overcharge, silently!)")
    print()
    # This file IS a pytest suite — running it directly just hands over to pytest.
    try:
        import pytest
    except ImportError:
        raise SystemExit("This is a pytest test file. Install pytest first:  pip install pytest")
    raise SystemExit(pytest.main([__file__, "-v", "-p", "no:cacheprovider"]))
