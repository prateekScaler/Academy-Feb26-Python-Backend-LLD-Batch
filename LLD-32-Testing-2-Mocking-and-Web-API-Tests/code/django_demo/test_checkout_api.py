"""
django_db + mocking — where Part 2 meets Part 3.

The checkout endpoint calls Stripe mid-request. We drive the real endpoint with
APIClient (real routing/view/DB) but `patch` the gateway so no card is charged.
"""

import pytest
from unittest.mock import patch
from rest_framework.test import APIClient

from demoapp.models import Order


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
@patch("demoapp.views.stripe_gateway")            # patch WHERE the view looks it up
def test_checkout_charges_and_saves_a_paid_order(mock_gateway, client):
    mock_gateway.charge.return_value = "rcpt_42"          # stub the boundary

    resp = client.post("/api/checkout/", {"cart_id": 7}, format="json")

    assert resp.status_code == 201                        # the HTTP contract
    mock_gateway.charge.assert_called_once_with(500_00)   # we charged once (spy)
    order = Order.objects.get(cart_id=7)                  # the real DB effect
    assert order.status == "PAID"
    assert order.receipt == "rcpt_42"


@pytest.mark.django_db
@patch("demoapp.views.stripe_gateway")
def test_a_failed_charge_does_not_leave_a_paid_order(mock_gateway, client):
    mock_gateway.charge.side_effect = RuntimeError("gateway down")

    with pytest.raises(RuntimeError):
        client.post("/api/checkout/", {"cart_id": 7}, format="json")

    assert Order.objects.count() == 0                     # nothing persisted
