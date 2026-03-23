"""
Menu Views - Exception Handling, Decorators & Middleware Demo
==============================================================
This file demonstrates all three concepts from Class 9.
"""
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError

from .models import MenuItem, Category
from .serializers import MenuItemSerializer
from restaurant_demo.decorators import timing_decorator, rate_limit, log_request
from restaurant_demo.exceptions import MenuItemNotAvailable


def home(request):
    """Home page showing available demo endpoints."""
    return HttpResponse("""
Class 9 Demo: Exception Handling, Decorators & Middleware
=========================================================

EXCEPTION HANDLING DEMOS:
- /menu/item/1/           - Basic exception handling
- /menu/item/99999/       - Triggers DoesNotExist
- /menu/item-safe/99999/  - Uses get_object_or_404

DECORATOR DEMOS:
- /menu/timed/            - Timing decorator
- /menu/rate-limited/     - Rate limiting (try refreshing 5+ times)

API DEMOS (DRF):
- /menu/api/items/        - List items (check X-Request-Time header)
- /menu/api/items/1/      - Item detail
- /menu/api/items/99999/  - Triggers NotFound exception

Check the console for middleware logs (timing, request logging).
""", content_type='text/plain')


# =============================================================================
# EXCEPTION HANDLING DEMOS
# =============================================================================

def item_detail(request, item_id):
    """
    Basic exception handling with try-except.

    Try:
    - /menu/item/1/      (found)
    - /menu/item/99999/  (not found - handled gracefully)
    """
    try:
        item = MenuItem.objects.get(id=item_id)
    except MenuItem.DoesNotExist:
        return HttpResponse(
            f"Item #{item_id} not found",
            status=404
        )
    except MenuItem.MultipleObjectsReturned:
        # This shouldn't happen with id, but good practice
        return HttpResponse(
            "Multiple items found - database integrity issue",
            status=500
        )

    return HttpResponse(f"""
Item: {item.name}
Price: ${item.price}
Category: {item.category.name}
Available: {'Yes' if item.is_available else 'No'}
""")


def item_detail_safe(request, item_id):
    """
    Using get_object_or_404 shortcut.

    Same result, less code. Raises Http404 if not found.
    """
    item = get_object_or_404(MenuItem, id=item_id)

    return HttpResponse(f"""
Item: {item.name}
Price: ${item.price}
Category: {item.category.name}
Available: {'Yes' if item.is_available else 'No'}
""")


# =============================================================================
# DECORATOR DEMOS
# =============================================================================

@timing_decorator
def timed_view(request):
    """
    View decorated with timing_decorator.

    Check the console output for timing information.
    """
    import time
    time.sleep(0.1)  # Simulate some work
    return HttpResponse("This view is timed. Check console for duration.")


@rate_limit(max_calls=5, period_seconds=60)
def rate_limited_view(request):
    """
    View with rate limiting decorator.

    Try refreshing this page more than 5 times in 60 seconds.
    """
    return HttpResponse(
        "Success! You have remaining calls. "
        "Try refreshing more than 5 times in 60 seconds."
    )


@log_request
@timing_decorator
def stacked_decorators_view(request):
    """
    Example of stacking multiple decorators.

    Execution order:
    1. log_request's BEFORE code
    2. timing_decorator's BEFORE code
    3. This function
    4. timing_decorator's AFTER code
    5. log_request's AFTER code
    """
    return HttpResponse("Multiple decorators in action!")


# =============================================================================
# DRF API VIEWS - EXCEPTION HANDLING WITH REST FRAMEWORK
# =============================================================================

class MenuItemListView(generics.ListAPIView):
    """
    List all menu items.

    DRF handles exceptions automatically:
    - Serialization errors → 400 Bad Request
    - Server errors → 500 Internal Server Error
    """
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer


class MenuItemDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single menu item.

    Try:
    - /menu/api/items/1/      (found)
    - /menu/api/items/99999/  (returns proper JSON 404)
    """
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def retrieve(self, request, *args, **kwargs):
        """Override to show custom exception handling."""
        try:
            instance = self.get_object()
        except Exception:
            # DRF's get_object() raises Http404, but we can use NotFound
            raise NotFound(detail="Menu item not found")

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@api_view(['POST'])
def order_item(request, item_id):
    """
    Example using custom exceptions.

    POST /menu/api/order/1/
    """
    try:
        item = MenuItem.objects.get(id=item_id)
    except MenuItem.DoesNotExist:
        raise NotFound(detail=f"Item #{item_id} not found")

    if not item.is_available:
        # Using our custom exception
        raise MenuItemNotAvailable(
            detail=f"'{item.name}' is currently not available"
        )

    quantity = request.data.get('quantity', 1)
    if quantity < 1:
        raise ValidationError(detail="Quantity must be at least 1")

    return Response({
        'message': f"Ordered {quantity}x {item.name}",
        'total': float(item.price * quantity)
    })
