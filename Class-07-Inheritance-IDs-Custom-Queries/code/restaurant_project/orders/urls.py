# orders/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'orders'

router = DefaultRouter()
router.register('orders', views.OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]

# =============================================================================
# Generated URLs:
#
# Standard CRUD:
#   GET    /api/orders/              List all orders
#   POST   /api/orders/              Create new order
#   GET    /api/orders/{uuid}/       Get single order
#   PUT    /api/orders/{uuid}/       Update order
#   PATCH  /api/orders/{uuid}/       Partial update
#   DELETE /api/orders/{uuid}/       Delete order
#
# Custom actions:
#   GET    /api/orders/pending/          List pending orders
#   GET    /api/orders/today/            List today's orders
#   GET    /api/orders/needs-attention/  Orders needing action
#   GET    /api/orders/high-value/       High value orders
#   POST   /api/orders/{uuid}/confirm/   Confirm an order
#   POST   /api/orders/{uuid}/cancel/    Cancel an order
#
# Filtering:
#   GET /api/orders/?status=pending
#   GET /api/orders/?search=john
#   GET /api/orders/?ordering=-total_amount
# =============================================================================
