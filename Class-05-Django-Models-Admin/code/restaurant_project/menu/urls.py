# menu/urls.py

from django.urls import path
from . import views  # Relative import - keeps app portable!

app_name = 'menu'

urlpatterns = [
    # Basic pages
    path('', views.home, name='home'),
    path('list/', views.menu_list, name='menu_list'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('categories/', views.categories, name='categories'),

    # API endpoint
    path('api/', views.menu_json, name='menu_json'),

    # Search
    path('search/', views.search, name='search'),
]

# =============================================================================
# TEST URLS:
#
# /menu/                  - Home page
# /menu/list/             - All menu items (hardcoded!)
# /menu/item/1/           - Item detail (inefficient lookup!)
# /menu/item/99/          - 404 - not found
# /menu/categories/       - Categories with counts
# /menu/api/              - JSON response
# /menu/search/?q=pasta   - Search items
#
# After Class 5 (Models), the data will come from the DATABASE!
# =============================================================================
