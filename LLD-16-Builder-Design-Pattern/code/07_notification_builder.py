"""
07 - Notification Builder
=========================

This is the Builder for the 10-parameter Notification class we saw in
the Problem section. Demonstrates "boolean hell" being eliminated by
named fluent setters - the headline example of the whole class.

The original constructor required ALL 10 positional arguments:
    Notification("alice@x.com", "Welcome!", "Hi", True, True, False,
                 True, "high", None, 3)

With Builder, the caller pays only for what they need.
"""

from dataclasses import dataclass


@dataclass
class Notification:
    recipient: str
    subject: str
    body: str
    is_html: bool = False                 # default: plain text
    send_now: bool = True                 # default: immediate
    track_opens: bool = False
    archive_after_send: bool = False
    priority: str = "normal"              # one of: low, normal, high
    schedule_at: str | None = None        # ISO 8601 string, optional
    retry: int = 3                        # default retry count

    def __str__(self):
        flags = []
        if self.is_html:            flags.append("html")
        if not self.send_now:       flags.append(f"scheduled@{self.schedule_at}")
        if self.track_opens:        flags.append("tracked")
        if self.priority != "normal": flags.append(f"priority={self.priority}")
        suffix = f" [{', '.join(flags)}]" if flags else ""
        return f"To: {self.recipient} | Subject: {self.subject}{suffix}"


class NotificationBuilder:
    def __init__(self):
        self._recipient = None
        self._subject = ""
        self._body = ""
        self._is_html = False
        self._send_now = True
        self._track_opens = False
        self._archive_after_send = False
        self._priority = "normal"
        self._schedule_at = None
        self._retry = 3

    # Required fields
    def to(self, recipient):
        self._recipient = recipient
        return self

    def subject(self, text):
        self._subject = text
        return self

    def body(self, text):
        self._body = text
        return self

    # Format toggles
    def html(self):                       # enables HTML formatting
        self._is_html = True
        return self

    def track(self):                      # opt into open tracking
        self._track_opens = True
        return self

    def archive_on_send(self):
        self._archive_after_send = True
        return self

    # Scheduling
    def schedule(self, when):
        """Schedule for a future ISO timestamp instead of sending now."""
        self._send_now = False
        self._schedule_at = when
        return self

    # Priority
    def high_priority(self):  self._priority = "high"; return self
    def low_priority(self):   self._priority = "low";  return self

    # Retry
    def retries(self, n):
        self._retry = n
        return self

    def build(self) -> Notification:
        if not self._recipient:
            raise ValueError("recipient required (use .to(...))")
        if not self._subject:
            raise ValueError("subject required (use .subject(...))")
        return Notification(
            recipient=self._recipient,
            subject=self._subject,
            body=self._body,
            is_html=self._is_html,
            send_now=self._send_now,
            track_opens=self._track_opens,
            archive_after_send=self._archive_after_send,
            priority=self._priority,
            schedule_at=self._schedule_at,
            retry=self._retry,
        )


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo():
    print("--- Simple welcome email (mostly defaults) ---")
    welcome = (NotificationBuilder()
                 .to("alice@x.com")
                 .subject("Welcome!")
                 .body("Hi Alice, glad to have you.")
                 .html()
                 .build())
    print(welcome)

    print("\n--- High-priority alert ---")
    alert = (NotificationBuilder()
               .to("oncall@x.com")
               .subject("PROD ALERT: 5xx spike")
               .body("Error rate at 12% for 5 minutes")
               .high_priority()
               .retries(10)
               .build())
    print(alert)

    print("\n--- Scheduled marketing email with tracking ---")
    promo = (NotificationBuilder()
               .to("user@x.com")
               .subject("Black Friday is coming!")
               .body("Get ready for our biggest sale...")
               .html()
               .track()
               .schedule("2026-11-29T08:00:00Z")
               .archive_on_send()
               .build())
    print(promo)

    print("\n--- Missing recipient raises early ---")
    try:
        NotificationBuilder().subject("test").build()
    except ValueError as e:
        print(f"ValueError: {e}")


if __name__ == "__main__":
    demo()
