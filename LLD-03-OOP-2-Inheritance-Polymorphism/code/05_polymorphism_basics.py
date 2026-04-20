"""
Polymorphism Basics -- Same Interface, Different Behavior
==========================================================
Poly (many) + Morph (forms) = Many Forms

One function call, but different objects respond differently.
This is what makes object-oriented code flexible and extensible.

Run: python 05_polymorphism_basics.py
"""


# ============================================================
# 1. What is Polymorphism?
# ============================================================
print("=" * 60)
print("1. What is Polymorphism?")
print("=" * 60)
print()
print("Poly = Many")
print("Morph = Forms")
print()
print("Real-world example:")
print("  'Start' means different things to different vehicles:")
print("  - Car: turn the key / push button")
print("  - Bicycle: start pedaling")
print("  - Boat: pull the cord")
print()
print("Same WORD ('start'), different ACTIONS depending on the vehicle.")
print("That's polymorphism.")
print()


# ============================================================
# 2. Polymorphism in code -- a simple example
# ============================================================
print("=" * 60)
print("2. Simple Example -- Different Objects, Same Method")
print("=" * 60)
print()


class Cat:
    def speak(self):
        return "Meow!"


class Dog:
    def speak(self):
        return "Woof!"


class Parrot:
    def speak(self):
        return "Polly wants a cracker!"


def make_it_speak(animal):
    """This function doesn't care WHAT the animal is.
    It only cares that it HAS a speak() method."""
    print(f"  {animal.__class__.__name__} says: {animal.speak()}")


animals = [Cat(), Dog(), Parrot()]
for animal in animals:
    make_it_speak(animal)

print()
print("make_it_speak() works with ANY object that has speak().")
print("It doesn't check the type. It just calls the method.")
print()


# ============================================================
# 3. Real-world example: Notification Service
# ============================================================
print("=" * 60)
print("3. Real-World Example: Notification Service")
print("=" * 60)
print()


class EmailNotification:
    def __init__(self, recipient):
        self.recipient = recipient

    def send(self, message):
        return f"[EMAIL] To: {self.recipient} | {message}"


class SMSNotification:
    def __init__(self, phone):
        self.phone = phone

    def send(self, message):
        return f"[SMS] To: {self.phone} | {message}"


class PushNotification:
    def __init__(self, device_id):
        self.device_id = device_id

    def send(self, message):
        return f"[PUSH] Device: {self.device_id} | {message}"


def notify_customer(notification, message):
    """Send a notification -- works with ANY notification type."""
    result = notification.send(message)
    print(f"  {result}")


# All three types work with the SAME function
print("Sending order confirmation via different channels:")
print()

channels = [
    EmailNotification("rahul@example.com"),
    SMSNotification("+91-9876543210"),
    PushNotification("device-abc-123"),
]

for channel in channels:
    notify_customer(channel, "Your order #42 is confirmed!")

print()


# ============================================================
# 4. The magic: adding a new type requires ZERO changes
# ============================================================
print("=" * 60)
print("4. Adding a New Type -- ZERO Changes to Existing Code")
print("=" * 60)
print()


class WhatsAppNotification:
    """Added LATER. We didn't touch EmailNotification, SMSNotification,
    PushNotification, or notify_customer. They all stay the same."""

    def __init__(self, phone):
        self.phone = phone

    def send(self, message):
        return f"[WHATSAPP] To: {self.phone} | {message}"


# Works immediately with the existing function!
whatsapp = WhatsAppNotification("+91-9123456789")
notify_customer(whatsapp, "Your order #42 is confirmed!")

print()
print("We added WhatsAppNotification without changing:")
print("  - EmailNotification      (untouched)")
print("  - SMSNotification        (untouched)")
print("  - PushNotification       (untouched)")
print("  - notify_customer()      (untouched)")
print()
print("This is the power of polymorphism:")
print("  New behavior WITHOUT modifying existing code.")
print()


# ============================================================
# 5. Without polymorphism -- the ugly alternative
# ============================================================
print("=" * 60)
print("5. Without Polymorphism -- The Ugly Alternative")
print("=" * 60)
print()
print("Without polymorphism, you'd write something like this:")
print()
print('  def notify_customer_ugly(channel_type, recipient, message):')
print('      if channel_type == "email":')
print('          # send email...')
print('      elif channel_type == "sms":')
print('          # send sms...')
print('      elif channel_type == "push":')
print('          # send push...')
print('      elif channel_type == "whatsapp":   # must edit THIS function')
print('          # send whatsapp...')
print()
print("Every new channel = edit the function = risk breaking existing code.")
print("With polymorphism, you NEVER touch existing code. Just add a new class.")
