"""
LLD-18 · Adapter · Example 8 — Containing a third-party SDK behind one file.

Run:  python3 08_third_party_sdk_adapter.py

The most useful real-world use of Adapter: keep all knowledge of a vendor's
SDK inside ONE file. The rest of the codebase only knows about your
in-house Target interface. If the vendor changes — switches API style,
gets acquired, you replace them — you change one file.

Here we have two competing analytics vendors. The rest of our code calls
`Analytics.track(...)`; both vendors' weird APIs are hidden behind adapters.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


# ====================================================================
# Target — the in-house interface (the only thing the rest of the
#          codebase imports)
# ====================================================================
@dataclass(frozen=True)
class Event:
    user_id: str
    name: str
    props: dict[str, Any]


class Analytics(ABC):
    @abstractmethod
    def track(self, event: Event) -> None: ...

    @abstractmethod
    def identify(self, user_id: str, traits: dict[str, Any]) -> None: ...


# ====================================================================
# Adaptee A — pretend this is Mixpanel's Python SDK
# ====================================================================
class MixpanelLikeSDK:
    """Method names: people_set, events_send. Args: user → distinct_id."""

    def __init__(self, project_token: str) -> None:
        self.token = project_token
        self.sent: list[tuple[str, dict]] = []

    def events_send(self, distinct_id: str, event_name: str, payload: dict) -> None:
        self.sent.append(("events_send", {"distinct_id": distinct_id, "event": event_name, **payload}))

    def people_set(self, distinct_id: str, properties: dict) -> None:
        self.sent.append(("people_set", {"distinct_id": distinct_id, **properties}))


# ====================================================================
# Adaptee B — pretend this is Amplitude's HTTP-style SDK
# ====================================================================
class AmplitudeLikeSDK:
    """One generic POST endpoint, JSON body. Different vocabulary."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.posted: list[dict] = []

    def post(self, endpoint: str, body: dict) -> None:
        self.posted.append({"endpoint": endpoint, "body": body})


# ====================================================================
# Adapters — make both SDKs speak our Analytics interface
# ====================================================================
class MixpanelAdapter(Analytics):
    def __init__(self, project_token: str) -> None:
        self._client = MixpanelLikeSDK(project_token)

    def track(self, event: Event) -> None:
        self._client.events_send(event.user_id, event.name, event.props)

    def identify(self, user_id: str, traits: dict[str, Any]) -> None:
        self._client.people_set(user_id, traits)


class AmplitudeAdapter(Analytics):
    def __init__(self, api_key: str) -> None:
        self._client = AmplitudeLikeSDK(api_key)

    def track(self, event: Event) -> None:
        self._client.post(
            endpoint="/2/httpapi",
            body={
                "type": "event",
                "user_id": event.user_id,
                "event_type": event.name,
                "event_properties": event.props,
            },
        )

    def identify(self, user_id: str, traits: dict[str, Any]) -> None:
        self._client.post(
            endpoint="/identify",
            body={"user_id": user_id, "user_properties": traits},
        )


# ====================================================================
# Client code — knows ONLY about Analytics
# ====================================================================
def signup_flow(analytics: Analytics, user_id: str, email: str) -> None:
    analytics.identify(user_id, {"email": email, "plan": "free"})
    analytics.track(Event(user_id, "signup_completed", {"source": "landing"}))
    analytics.track(Event(user_id, "first_view", {"page": "/dashboard"}))


if __name__ == "__main__":
    # The whole rest of the codebase just calls signup_flow(analytics, ...).
    # We can swap the vendor here in ONE line. Nothing else changes.

    print("--- Using Mixpanel ---")
    mx = MixpanelAdapter("mxp_tok_xxx")
    signup_flow(mx, "u_42", "ada@scaler.com")
    for call in mx._client.sent:
        print("  ", call)

    print("\n--- Using Amplitude (swapped with one line change) ---")
    am = AmplitudeAdapter("amp_key_xxx")
    signup_flow(am, "u_42", "ada@scaler.com")
    for call in am._client.posted:
        print("  ", call)

    print("\nThe `signup_flow` function is identical in both cases.")
    print("The vendor specifics live ENTIRELY in the adapter files.")
