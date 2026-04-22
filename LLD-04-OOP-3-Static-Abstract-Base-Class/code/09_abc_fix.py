"""ABC catches the bug at CREATION time, not runtime."""
from abc import ABC, abstractmethod

class Notification(ABC):
    @abstractmethod
    def send(self, message):
        pass

class EmailNotification(Notification):
    def send(self, message):
        print(f"EMAIL: {message}")

class BrokenNotification(Notification):
    pass  # Forgot send()!

# Works:
email = EmailNotification()
email.send("Order ready")

# Caught IMMEDIATELY at creation — not later in production:
try:
    broken = BrokenNotification()
except TypeError as e:
    print(f"CREATION ERROR: {e}")
    print("Bug caught before any damage.")
