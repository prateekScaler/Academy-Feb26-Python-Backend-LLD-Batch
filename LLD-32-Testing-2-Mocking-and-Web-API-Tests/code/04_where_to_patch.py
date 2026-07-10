"""
04 — patch, and the WHERE-to-patch rule
=======================================

`patch` temporarily replaces a name, then restores it — as a decorator or
a context manager. The #1 gotcha:

    Patch the name WHERE IT IS LOOKED UP, not where it is defined.

If `billing.py` does `from rates import get_rate` and calls `get_rate()`,
that name now lives in `billing`'s namespace — so you patch
`"billing.get_rate"`, NOT `"rates.get_rate"`.

The usual form is a string: `patch("billing.get_rate", ...)`. These teaching
files have digit-prefixed names (not importable by string), so we use the
equivalent `patch.object(<module>, "name", ...)` — same idea: replace the
name IN THE MODULE THAT LOOKS IT UP (here, this one).

Needs:  pip install pytest
"""

import sys
from unittest.mock import patch
import pytest

THIS = sys.modules[__name__]        # the module where price_in_inr looks the name up


def fetch_usd_inr_rate() -> float:
    raise RuntimeError("real network call to an FX API")


def price_in_inr(usd: float) -> float:
    return round(usd * fetch_usd_inr_rate(), 2)


def test_patch_as_a_context_manager():
    with patch.object(THIS, "fetch_usd_inr_rate", return_value=83.0):
        assert price_in_inr(10) == 830.0
    # outside the `with`, the real (raising) function is back
    with pytest.raises(RuntimeError):
        price_in_inr(10)


@patch.object(THIS, "fetch_usd_inr_rate", return_value=83.0)
def test_patch_as_a_decorator(mock_rate):
    assert price_in_inr(10) == 830.0
    mock_rate.assert_called_once_with()          # called with no args


@patch.object(THIS, "fetch_usd_inr_rate")
def test_configure_the_injected_mock(mock_rate):
    mock_rate.return_value = 90.0                # set it up inside the test
    assert price_in_inr(2) == 180.0


if __name__ == "__main__":
    try:
        import pytest as _pt
    except ImportError:
        raise SystemExit("This is a pytest test file. Install pytest first:  pip install pytest")
    raise SystemExit(_pt.main([__file__, "-v", "-p", "no:cacheprovider"]))
