"""
05 — Spying: assert HOW a dependency was called
===============================================

Some behaviour has no return value to check — the point IS the interaction:
"charge exactly once", "send one receipt email", "don't email on failure".
A Mock is also a spy: it remembers every call.

    .assert_called_once_with(...)   exactly one call, with these args
    .assert_not_called()            never called
    .call_count                     how many times
    .call_args                      the last call's args

Needs:  pip install pytest
"""

from unittest.mock import Mock
import pytest


class PaymentError(Exception):
    pass


def checkout(gateway, mailer, amount_paise: int, email: str):
    try:
        receipt = gateway.charge(amount_paise)
    except PaymentError:
        return None                       # failed payment -> no email
    mailer.send(to=email, subject="Your receipt")
    return 45


def test_charges_exactly_once_the_no_double_charge_guarantee():
    gateway, mailer = Mock(), Mock()
    gateway.charge.return_value = "rcpt_1"
    receipt = checkout(gateway, mailer, 500_00, "a@b.com")
    gateway.charge.assert_called_once_with(500_00)
    assert gateway.charge.call_count == 1
    assert receipt == "rcpt_1"


def test_sends_one_receipt_email_with_the_right_args():
    gateway, mailer = Mock(), Mock()
    checkout(gateway, mailer, 500_00, "a@b.com")
    mailer.send.assert_called_once_with(to="a@b.com", subject="Your receipt")


def test_no_email_is_sent_when_the_charge_fails():
    gateway, mailer = Mock(), Mock()
    gateway.charge.side_effect = PaymentError("declined")
    assert checkout(gateway, mailer, 500_00, "a@b.com") is None
    mailer.send.assert_not_called()       # the important negative assertion


if __name__ == "__main__":
    try:
        import pytest as _pt
    except ImportError:
        raise SystemExit("This is a pytest test file. Install pytest first:  pip install pytest")
    raise SystemExit(_pt.main([__file__, "-v", "-p", "no:cacheprovider"]))
