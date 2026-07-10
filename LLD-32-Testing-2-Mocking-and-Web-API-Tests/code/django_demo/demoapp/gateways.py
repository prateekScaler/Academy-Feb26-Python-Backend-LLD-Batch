"""The external boundary. In a real app this talks to Stripe over the network;
in tests we `patch` `demoapp.views.stripe_gateway` so it never runs."""


class StripeGateway:
    def charge(self, amount_paise: int) -> str:
        raise RuntimeError("real network call to Stripe — never hit in a test")


stripe_gateway = StripeGateway()
