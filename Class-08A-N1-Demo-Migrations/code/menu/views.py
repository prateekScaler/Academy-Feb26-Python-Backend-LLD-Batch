# menu/views.py
# =============================================================================
# AFTER CLASS 5: We're now using Django Models and the database!
#
# But there's a NEW PROBLEM: How do we build APIs?
# - JsonResponse works, but we have to manually build dictionaries
# - No automatic validation
# - No standard way to handle POST/PUT/DELETE
# - Mobile apps and React frontends need proper REST APIs!
#
# SOLUTION: Django REST Framework (Class 6!)
# =============================================================================

from django.http import HttpResponse, JsonResponse
from .models import Category, MenuItem


def home(request):
    """Home page for the menu service."""
    return HttpResponse(
        "Welcome to our Restaurant!\n\n"
        "Available endpoints:\n"
        "- /menu/list/ - View menu (text)\n"
        "- /menu/item/<id>/ - View item details\n"
        "- /menu/categories/ - View categories\n"
        "- /menu/api/ - JSON API (basic)\n"
        "\n"
        "Coming in Class 6: Real REST APIs with DRF!"
    )


def menu_list(request):
    """
    List all available menu items.

    This view uses MODELS now (not hardcoded data).
    But it returns plain text - not ideal for APIs.
    """
    items = MenuItem.objects.filter(is_available=True)

    response = "Our Menu:\n"
    response += "-" * 40 + "\n"
    for item in items:
        response += f"  {item.name}: ${item.price}\n"
        response += f"    Category: {item.category.name}\n\n"

    response += f"\n({items.count()} items available)"
    return HttpResponse(response, content_type="text/plain")


def item_detail(request, item_id):
    """
    Show details for a specific menu item.

    Using models now - O(1) database lookup instead of O(n) list search!
    """
    try:
        item = MenuItem.objects.get(id=item_id)
    except MenuItem.DoesNotExist:
        return HttpResponse(f"Item #{item_id} not found")

    response = f"""
{item.name}
{'=' * len(item.name)}
Price: ${item.price}
Category: {item.category.name}
Available: {'Yes' if item.is_available else 'No'}
Description: {item.description or 'No description'}
"""
    return HttpResponse(response)


def categories(request):
    """List all categories with item counts."""
    cats = Category.objects.all()

    response = "Categories:\n"
    response += "-" * 30 + "\n"

    for cat in cats:
        count = cat.items.count()  # Using related_name='items'
        response += f"  {cat.name}: {count} items\n"

    return HttpResponse(response, content_type="text/plain")


def menu_json(request):
    """
    API endpoint - return menu as JSON.

    PROBLEM: We have to manually build the dictionary!
    - What if MenuItem has 20 fields?
    - What about nested objects (category)?
    - What about validation for POST requests?
    - What about handling PUT/DELETE?

    This is where Django REST Framework (DRF) helps!
    """
    items = MenuItem.objects.filter(is_available=True)

    # Manual serialization - tedious and error-prone!
    items_list = []
    for item in items:
        items_list.append({
            "id": item.id,
            "name": item.name,
            "price": str(item.price),  # Decimal isn't JSON serializable!
            "category": item.category.name,
            "is_available": item.is_available,
        })

    return JsonResponse({
        "count": len(items_list),
        "items": items_list
    })


# =============================================================================
# LIMITATIONS OF CURRENT APPROACH:
#
# 1. Manual JSON conversion - tedious, error-prone
# 2. No validation for incoming data (POST/PUT)
# 3. No standard REST patterns (we'd have to write everything ourselves)
# 4. No authentication/permissions handling
# 5. No pagination, filtering, or search built-in
# 6. Decimal/DateTime types need manual conversion
#
# WHAT WE'LL DO IN CLASS 6:
#
# 1. Install Django REST Framework
# 2. Create Serializers (automatic model → JSON conversion)
# 3. Create ViewSets (automatic CRUD endpoints)
# 4. Use Routers (automatic URL generation)
# 5. Get a beautiful browsable API for free!
# =============================================================================
