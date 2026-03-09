# menu/urls.py
# Class 4: App URL Patterns

from django.urls import path
from . import views  # Relative import - "." means current folder

app_name = 'menu'  # Namespace for URL reversing

urlpatterns = [
    # /menu/
    path('', views.home, name='home'),

    # /menu/list/
    path('list/', views.menu_list, name='menu_list'),

    # /menu/item/3/ - captures item_id as integer
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),

    # /menu/about/
    path('about/', views.about, name='about'),

    # /menu/api/ - JSON endpoint
    path('api/', views.menu_json, name='menu_json'),
]
