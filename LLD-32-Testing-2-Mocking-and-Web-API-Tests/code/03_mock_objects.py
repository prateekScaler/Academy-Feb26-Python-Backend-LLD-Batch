"""
03 — Mock objects: return_value, side_effect, and assertions
============================================================

`unittest.mock.Mock` (stdlib) is a shape-shifter: any attribute or method
you touch springs into existence and records how it was used. Two dials:
  * .return_value  — what a call hands back
  * .side_effect   — a function to run, an exception to raise, or values to
                     yield on successive calls

Needs:  pip install pytest
"""

from unittest.mock import Mock
import pytest


def send_welcome(mailer, user: dict) -> bool:
    if not user.get("email"):
        raise ValueError("user has no email")
    mailer.send(to=user["email"], subject="Welcome")
    return True


def test_mock_conjures_methods_and_records_calls():
    mailer = Mock()                                  # no real mail server
    assert send_welcome(mailer, {"email": "a@b.com"}) is True
    mailer.send.assert_called_once_with(to="a@b.com", subject="Welcome")


def test_return_value_sets_what_a_call_gives_back():
    gateway = Mock()
    gateway.charge.return_value = "rcpt_9"
    assert gateway.charge(100) == "rcpt_9"


def test_side_effect_makes_a_mock_raise():
    gateway = Mock()
    gateway.charge.side_effect = TimeoutError("gateway down")
    with pytest.raises(TimeoutError):
        gateway.charge(100)


def test_side_effect_can_be_a_sequence_of_values():
    clock = Mock()
    clock.now.side_effect = [1000, 1002, 1005]       # successive calls
    assert [clock.now(), clock.now(), clock.now()] == [1000, 1002, 1005]


if __name__ == "__main__":
    try:
        import pytest as _pt
    except ImportError:
        raise SystemExit("This is a pytest test file. Install pytest first:  pip install pytest")
    raise SystemExit(_pt.main([__file__, "-v", "-p", "no:cacheprovider"]))
