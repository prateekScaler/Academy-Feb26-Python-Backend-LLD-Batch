# menu/views.py
# Class 4: Basic Views with HttpResponse

from django.http import HttpResponse, JsonResponse


def home(request):
    """Home page for the restaurant."""
    return HttpResponse("Welcome to our Restaurant!")


def menu_list(request):
    """Display the menu."""
    return HttpResponse("Menu: Pasta $15, Salmon $22, Salad $12")


def item_detail(request, item_id):
    """Show details for a specific item."""
    return HttpResponse(f"Details for item #{item_id}")


def about(request):
    """About page."""
    return HttpResponse("About: We serve great food!")


def menu_json(request):
    """API endpoint - returns JSON."""
    data = {"items": ["Pasta", "Salmon", "Salad"]}
    return JsonResponse(data)
