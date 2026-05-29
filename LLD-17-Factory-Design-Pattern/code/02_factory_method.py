"""
02 - Factory Method
===================

Each concrete type gets its OWN creator subclass. Adding a new type =
adding a new class. NO edits to existing creators. OCP restored.

Pro: Open/Closed compliance.  New channels slot in cleanly.
Con: More classes (5 channels -> 5 creators). The "string -> creator"
     lookup must live somewhere (often a tiny registry dict at the edge).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Products (same hierarchy as file 01)
# ---------------------------------------------------------------------------

class Notification(ABC):
    @abstractmethod
    def send(self, message: str) -> None: ...


@dataclass
class EmailNotification(Notification):
    to: str
    smtp_host: str

    def send(self, msg):
        print(f"[email] {self.to} via {self.smtp_host}: {msg}")


@dataclass
class SMSNotification(Notification):
    phone: str

    def send(self, msg):
        print(f"[sms] {self.phone}: {msg}")


@dataclass
class PushNotification(Notification):
    device_id: str

    def send(self, msg):
        print(f"[push] dev={self.device_id}: {msg}")


# Added later - notice that NO existing class below changes when this lands
@dataclass
class DiscordNotification(Notification):
    webhook_url: str
    user_handle: str

    def send(self, msg):
        print(f"[discord] @{self.user_handle}: {msg}")


# ---------------------------------------------------------------------------
# The abstract Creator with the factory method
# ---------------------------------------------------------------------------

class NotificationCreator(ABC):
    """Abstract creator. Subclasses decide which Notification to make."""

    @abstractmethod
    def create_notification(self, user) -> Notification: ...

    # A template method that uses the factory method internally.
    # Same shape across all subclasses, but each builds a different product.
    def notify(self, user, message: str) -> None:
        n = self.create_notification(user)
        n.send(message)


# ---------------------------------------------------------------------------
# Concrete creators - one per type
# ---------------------------------------------------------------------------

class EmailCreator(NotificationCreator):
    def create_notification(self, user):
        return EmailNotification(to=user.email, smtp_host="smtp.example.com")


class SMSCreator(NotificationCreator):
    def create_notification(self, user):
        return SMSNotification(phone=user.phone)


class PushCreator(NotificationCreator):
    def create_notification(self, user):
        return PushNotification(device_id=user.device_id)


# NEW creator added later - zero changes to the three above
class DiscordCreator(NotificationCreator):
    def create_notification(self, user):
        return DiscordNotification(
            webhook_url="https://discord.com/api/webhooks/...",
            user_handle=user.discord_handle,
        )


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

@dataclass
class User:
    email: str
    phone: str
    device_id: str
    discord_handle: str


def demo():
    user = User("alice@x.com", "555-0100", "dev-42", "alice#1234")

    # The "which creator?" choice happens at the edge - typically driven by
    # user preferences, a config table, or an env variable.
    for creator in (
        EmailCreator(),
        SMSCreator(),
        PushCreator(),
        DiscordCreator(),
    ):
        creator.notify(user, f"Welcome via {type(creator).__name__}!")

    # Tiny registry at the composition root if you want string->creator
    registry: dict[str, NotificationCreator] = {
        "email":   EmailCreator(),
        "sms":     SMSCreator(),
        "push":    PushCreator(),
        "discord": DiscordCreator(),
    }
    print("\n--- via registry ---")
    registry[user_preferred := "discord"].notify(user, "From the registry path!")


if __name__ == "__main__":
    demo()
