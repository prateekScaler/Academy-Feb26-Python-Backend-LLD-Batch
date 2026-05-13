"""Internationalized error messages in Django.

In production APIs, error messages need to be:
1. Translatable (English, Hindi, French...)
2. Consistent format (error code + human message)
3. Machine-readable (status codes, error codes)
"""


# --- Step 1: Django's translation system ---
# In a real Django project:
# from django.utils.translation import gettext_lazy as _
#
# For this demo, we simulate it:
def _(message):
    """Simulate Django's gettext_lazy."""
    return message


# --- Step 2: Custom exception with i18n message ---
class AppError(Exception):
    """Base error with error code and translatable message."""
    default_message = _("An error occurred")
    error_code = "GENERIC_ERROR"
    status_code = 500

    def __init__(self, message=None, **kwargs):
        self.message = message or self.default_message
        self.details = kwargs
        super().__init__(self.message)

    def to_dict(self):
        """Standardized error response."""
        return {
            "error_code": self.error_code,
            "message": str(self.message),
            "details": self.details,
        }


class NotFoundError(AppError):
    default_message = _("The requested resource was not found")
    error_code = "NOT_FOUND"
    status_code = 404


class InsufficientStockError(AppError):
    # Translatable with placeholders:
    default_message = _("Only %(available)s items in stock, %(requested)s requested")
    error_code = "INSUFFICIENT_STOCK"
    status_code = 400

    def __init__(self, available, requested):
        super().__init__(
            message=self.default_message % {"available": available, "requested": requested},
            available=available,
            requested=requested,
        )


class ValidationError(AppError):
    default_message = _("Validation failed")
    error_code = "VALIDATION_ERROR"
    status_code = 422


# --- Step 3: Use in views ---
def place_order(item_id, quantity):
    """Simulated Django view logic."""
    stock = 5
    if quantity > stock:
        raise InsufficientStockError(available=stock, requested=quantity)
    return {"order_id": 123, "item_id": item_id, "quantity": quantity}


# --- Step 4: Catch and format ---
print("=== API Error Response ===\n")

try:
    place_order(1, 10)
except AppError as e:
    response = e.to_dict()
    print(f"Status: {e.status_code}")
    for key, val in response.items():
        print(f"  {key}: {val}")


# --- Step 5: In Django settings (real project) ---
print("""
--- Django i18n setup ---

# settings.py
LANGUAGE_CODE = 'en'
USE_I18N = True
LOCALE_PATHS = [BASE_DIR / 'locale']
LANGUAGES = [('en', 'English'), ('hi', 'Hindi'), ('fr', 'French')]

# In your code:
from django.utils.translation import gettext_lazy as _

class InsufficientStockError(AppError):
    default_message = _("Only %(available)s items in stock")
    #                  ^ gettext_lazy marks this for translation

# Create translation files:
#   python manage.py makemessages -l hi
#   → Edit locale/hi/LC_MESSAGES/django.po
#   python manage.py compilemessages

# locale/hi/LC_MESSAGES/django.po:
#   msgid "Only %(available)s items in stock"
#   msgstr "केवल %(available)s आइटम स्टॉक में हैं"

# Django auto-selects language based on:
#   1. User's Accept-Language header
#   2. Session/cookie language preference
#   3. LANGUAGE_CODE default
""")
