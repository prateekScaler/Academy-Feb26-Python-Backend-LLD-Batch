"""
Menu URL configuration.
Class 9: Exception Handling, Decorators & Middleware Demo
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Exception handling demos
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('item-safe/<int:item_id>/', views.item_detail_safe, name='item_detail_safe'),

    # Decorator demos
    path('timed/', views.timed_view, name='timed_view'),
    path('rate-limited/', views.rate_limited_view, name='rate_limited_view'),

    # API endpoints
    path('api/items/', views.MenuItemListView.as_view(), name='api_items'),
    path('api/items/<int:pk>/', views.MenuItemDetailView.as_view(), name='api_item_detail'),
]
