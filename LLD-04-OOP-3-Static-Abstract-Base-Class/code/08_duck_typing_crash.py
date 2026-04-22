"""Duck typing's weakness: crash at runtime."""

class EmailNotification:
    def send(self, msg):
        print(f"EMAIL: {msg}")

class BrokenNotification:
    pass  # Forgot send()!

def notify(notifier, msg):
    notifier.send(msg)

# Works:
notify(EmailNotification(), "Order ready")

# Crashes at RUNTIME — object was created fine, crash comes later:
try:
    notify(BrokenNotification(), "Order ready")
except AttributeError as e:
    print(f"RUNTIME CRASH: {e}")
    print("This could happen in production at 2 AM.")
