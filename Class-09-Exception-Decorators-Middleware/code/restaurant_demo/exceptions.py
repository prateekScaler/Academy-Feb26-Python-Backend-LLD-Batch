"""
Custom Exception Examples
=========================
Custom exceptions make error handling more semantic and organized.
"""
from rest_framework import status
from rest_framework.exceptions import APIException


# =============================================================================
# DJANGO BUILT-IN EXCEPTIONS (Reference)
# =============================================================================
#
# Model.DoesNotExist      - Object not found in database
# Model.MultipleObjectsReturned - get() returned more than one object
# ValidationError         - Model validation failed
# PermissionDenied        - User doesn't have permission
# SuspiciousOperation     - Security-related issue
# Http404                 - Page not found
#
# =============================================================================


# =============================================================================
# DRF BUILT-IN EXCEPTIONS (Reference)
# =============================================================================
#
# NotFound           - 404 - Resource not found
# ValidationError    - 400 - Invalid data
# PermissionDenied   - 403 - No permission
# NotAuthenticated   - 401 - Auth required
# MethodNotAllowed   - 405 - Wrong HTTP method
# Throttled          - 429 - Rate limit exceeded
#
# =============================================================================


# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================

class MenuItemNotAvailable(APIException):
    """Raised when trying to order an unavailable menu item."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'This menu item is currently not available.'
    default_code = 'menu_item_not_available'


class InsufficientStock(APIException):
    """Raised when order quantity exceeds available stock."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Insufficient stock for this order.'
    default_code = 'insufficient_stock'


class RestaurantClosed(APIException):
    """Raised when trying to place order outside business hours."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Restaurant is currently closed.'
    default_code = 'restaurant_closed'


class InvalidCouponCode(APIException):
    """Raised when coupon code is invalid or expired."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid or expired coupon code.'
    default_code = 'invalid_coupon'


class OrderAlreadyProcessed(APIException):
    """Raised when trying to modify an already processed order."""
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'This order has already been processed and cannot be modified.'
    default_code = 'order_already_processed'


class PaymentFailed(APIException):
    """Raised when payment processing fails."""
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = 'Payment processing failed.'
    default_code = 'payment_failed'


# =============================================================================
# USING CUSTOM EXCEPTIONS
# =============================================================================
#
# In your views:
#
#     from restaurant_demo.exceptions import MenuItemNotAvailable
#
#     def add_to_order(request, item_id):
#         item = MenuItem.objects.get(id=item_id)
#         if not item.is_available:
#             raise MenuItemNotAvailable()  # DRF handles the response
#
#         # Or with custom message:
#         raise MenuItemNotAvailable(detail=f'{item.name} is sold out today')
#
# =============================================================================
