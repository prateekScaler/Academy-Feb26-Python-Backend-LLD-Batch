# menu/urls.py

from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    # Basic pages (returning text/HTML)
    path('', views.home, name='home'),
    path('list/', views.menu_list, name='menu_list'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('categories/', views.categories, name='categories'),

    # Basic JSON API (manual serialization - the problem!)
    path('api/', views.menu_json, name='menu_json'),
]

# =============================================================================
# CURRENT STATE (After Class 5):
#
# /menu/                  - Home page
# /menu/list/             - All menu items (from database!)
# /menu/item/1/           - Item detail
# /menu/categories/       - Categories with counts
# /menu/api/              - JSON response (manual serialization)
#
# WHAT WE'LL ADD IN CLASS 6 (REST API):
#
# /menu/api/categories/           - GET (list), POST (create)
# /menu/api/categories/1/         - GET, PUT, PATCH, DELETE
# /menu/api/menu-items/           - GET (list), POST (create)
# /menu/api/menu-items/1/         - GET, PUT, PATCH, DELETE
#
# All with automatic serialization, validation, and browsable API!
# =============================================================================
