# menu/views.py

from django.http import HttpResponse, JsonResponse

# =============================================================================
# PROBLEM: All our data is HARDCODED right here in views.py!
#
# Issues with this approach:
# 1. Data is duplicated - if price changes, we update in multiple places
# 2. No persistence - restart server, any "changes" are lost
# 3. No validation - anyone can put anything
# 4. No relationships - how do we link items to categories?
# 5. Can't search, filter, or sort efficiently
# 6. Multiple developers = merge conflicts on this file
#
# SOLUTION: Django Models + Database (Class 5!)
# =============================================================================

# Hardcoded menu data (THIS IS THE PROBLEM!)
MENU_ITEMS = [
    {"id": 1, "name": "Garlic Bread", "price": 6.99, "category": "Appetizers", "available": True},
    {"id": 2, "name": "Bruschetta", "price": 7.99, "category": "Appetizers", "available": True},
    {"id": 3, "name": "Pasta Alfredo", "price": 15.99, "category": "Main Course", "available": True},
    {"id": 4, "name": "Grilled Salmon", "price": 22.99, "category": "Main Course", "available": True},
    {"id": 5, "name": "Margherita Pizza", "price": 14.99, "category": "Main Course", "available": False},
    {"id": 6, "name": "Chocolate Cake", "price": 8.99, "category": "Desserts", "available": True},
    {"id": 7, "name": "Tiramisu", "price": 9.99, "category": "Desserts", "available": True},
]

CATEGORIES = ["Appetizers", "Main Course", "Desserts", "Beverages"]


def home(request):
    """Home page for the menu service."""
    return HttpResponse("Welcome to our Restaurant! Visit /menu/list/ for our menu.")


def menu_list(request):
    """
    List all available menu items.

    PROBLEM: Data is hardcoded above. What if we want to:
    - Add a new item? Edit this file, redeploy.
    - Change a price? Edit this file, redeploy.
    - Let a manager update the menu? They can't - it's code!
    """
    available_items = [item for item in MENU_ITEMS if item["available"]]

    response = "Our Menu:\n"
    response += "-" * 40 + "\n"
    for item in available_items:
        response += f"  {item['name']}: ${item['price']:.2f}\n"
        response += f"    Category: {item['category']}\n\n"

    response += f"\n({len(available_items)} items available)"
    return HttpResponse(response, content_type="text/plain")


def item_detail(request, item_id):
    """
    Show details for a specific menu item.

    PROBLEM: Linear search through a list! O(n) complexity.
    With a database: O(1) lookup by primary key.
    """
    # This is inefficient - imagine 10,000 items!
    item = None
    for menu_item in MENU_ITEMS:
        if menu_item["id"] == item_id:
            item = menu_item
            break

    if item is None:
        return HttpResponse(f"Item #{item_id} not found", status=404)

    response = f"""
{item['name']}
{'=' * len(item['name'])}
Price: ${item['price']:.2f}
Category: {item['category']}
Available: {'Yes' if item['available'] else 'No'}
"""
    return HttpResponse(response, content_type="text/plain")


def categories(request):
    """
    List all categories with item counts.

    PROBLEM: We have to manually count by looping.
    With models: Category.objects.annotate(count=Count('items'))
    """
    response = "Categories:\n"
    response += "-" * 30 + "\n"

    for category in CATEGORIES:
        # Inefficient counting!
        count = len([item for item in MENU_ITEMS if item["category"] == category])
        response += f"  {category}: {count} items\n"

    return HttpResponse(response, content_type="text/plain")


def menu_json(request):
    """
    API endpoint - return menu as JSON.

    PROBLEM: Still using hardcoded data.
    With models + DRF: Automatic serialization, filtering, pagination!
    """
    available_items = [item for item in MENU_ITEMS if item["available"]]
    return JsonResponse({
        "count": len(available_items),
        "items": available_items
    })


def search(request):
    """
    Search menu items by name.

    PROBLEM: Basic string matching, case-sensitive, no fuzzy search.
    With models: MenuItem.objects.filter(name__icontains=query)
    """
    query = request.GET.get("q", "")

    if not query:
        return HttpResponse("Usage: /menu/search/?q=pasta", content_type="text/plain")

    # Case-insensitive search (manual implementation)
    results = [
        item for item in MENU_ITEMS
        if query.lower() in item["name"].lower()
    ]

    if not results:
        return HttpResponse(f"No items found matching '{query}'", content_type="text/plain")

    response = f"Search results for '{query}':\n"
    response += "-" * 40 + "\n"
    for item in results:
        response += f"  {item['name']}: ${item['price']:.2f}\n"

    return HttpResponse(response, content_type="text/plain")


# =============================================================================
# WHAT WE'LL DO IN CLASS 5:
#
# 1. Create models (Category, MenuItem) in models.py
# 2. Run migrations to create database tables
# 3. Use Django Admin to manage data (no code changes!)
# 4. Update these views to use: MenuItem.objects.filter(is_available=True)
# 5. No more hardcoded data!
#
# Benefits:
# - Data persists in database
# - Non-developers can update via Admin
# - Efficient queries (database does the work)
# - Relationships between models (ForeignKey)
# - Validation built-in
# =============================================================================
