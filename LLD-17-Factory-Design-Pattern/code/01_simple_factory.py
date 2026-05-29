"""
01 - Simple Factory
===================

Centralizes the "which concrete class do I instantiate?" choice in one
place. All construction logic + config lives in NotificationFactory.create().

Pro:  DRY restored - call sites become one-liners.
Con:  Adding a new channel still requires editing this file (OCP violation).
      That's what Factory Method (file 02) cures.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Abstract product + concretes
# ---------------------------------------------------------------------------

class Notification(ABC):
    @abstractmethod
    def send(self, message: str) -> None: ...


@dataclass
class EmailNotification(Notification):
    to: str
    smtp_host: str
    smtp_port: int
    user: str
    password: str

    def send(self, msg: str) -> None:
        print(f"[email] {self.to} via {self.smtp_host}:{self.smtp_port}: {msg}")


@dataclass
class SMSNotification(Notification):
    phone: str
    api_key: str
    country_code: str

    def send(self, msg: str) -> None:
        print(f"[sms] {self.country_code}{self.phone}: {msg}")


@dataclass
class PushNotification(Notification):
    device_id: str
    fcm_key: str

    def send(self, msg: str) -> None:
        print(f"[push] device={self.device_id}: {msg}")


# ---------------------------------------------------------------------------
# The Simple Factory - one static method, one if/elif
# ---------------------------------------------------------------------------

# Pretend these come from env vars in real life
_CONFIG = {
    "SMTP_HOST": "smtp.example.com",
    "SMTP_PORT": 587,
    "SMTP_USER": "noreply@example.com",
    "SMTP_PASS": "secret",
    "TWILIO_KEY": "twilio_xyz",
    "FCM_KEY":    "fcm_abc",
}


class NotificationFactory:
    @staticmethod
    def create(channel: str, user) -> Notification:
        if channel == "email":
            return EmailNotification(
                to=user.email,
                smtp_host=_CONFIG["SMTP_HOST"],
                smtp_port=_CONFIG["SMTP_PORT"],
                user=_CONFIG["SMTP_USER"],
                password=_CONFIG["SMTP_PASS"],
            )
        elif channel == "sms":
            return SMSNotification(
                phone=user.phone,
                api_key=_CONFIG["TWILIO_KEY"],
                country_code=user.country_code,
            )
        elif channel == "push":
            return PushNotification(
                device_id=user.device_id,
                fcm_key=_CONFIG["FCM_KEY"],
            )
        raise ValueError(f"unknown channel: {channel!r}")


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

@dataclass
class User:
    email: str
    phone: str
    country_code: str
    device_id: str


def demo():
    user = User(
        email="alice@example.com",
        phone="555-0100",
        country_code="+1",
        device_id="dev-42",
    )

    # Callers are now trivial - no SMTP host, no API key, no config leaks
    for channel in ("email", "sms", "push"):
        NotificationFactory.create(channel, user).send(f"Welcome via {channel}!")

    print("\n--- Unknown channel raises ---")
    try:
        NotificationFactory.create("carrier-pigeon", user)
    except ValueError as e:
        print(f"ValueError: {e}")


if __name__ == "__main__":
    demo()
