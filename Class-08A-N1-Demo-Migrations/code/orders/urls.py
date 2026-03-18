# orders/urls.py
"""
URL configuration demonstrating 3 types of DRF views.

URL Pattern Comparison:
┌─────────────────────┬────────────────────────────────────────────────┐
│ View Type           │ URL Registration                               │
├─────────────────────┼────────────────────────────────────────────────┤
│ @api_view           │ path('health/', views.health_check)            │
│ APIView             │ path('class/', OrderListAPIView.as_view())     │
│ ModelViewSet        │ router.register('', OrderViewSet)              │
└─────────────────────┴────────────────────────────────────────────────┘

Available Endpoints:
    @api_view (Function-Based):
        GET  /api/orders/health/     -> Health check
        GET  /api/orders/stats/      -> Order statistics
        GET  /api/orders/fn/         -> List orders (function view)
        POST /api/orders/fn/         -> Create order (function view)

    APIView (Class-Based):
        GET  /api/orders/class/           -> List orders
        POST /api/orders/class/           -> Create order
        GET  /api/orders/class/<id>/      -> Retrieve order
        PUT  /api/orders/class/<id>/      -> Update order
        DELETE /api/orders/class/<id>/    -> Delete order

    ModelViewSet (Router-Based):
        GET    /api/orders/           -> List
        POST   /api/orders/           -> Create
        GET    /api/orders/{id}/      -> Retrieve
        PUT    /api/orders/{id}/      -> Update
        PATCH  /api/orders/{id}/      -> Partial update
        DELETE /api/orders/{id}/      -> Delete
        GET    /api/orders/pending/   -> Custom action
        POST   /api/orders/{id}/cancel/  -> Custom action
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    # @api_view (Function-Based)
    health_check,
    order_stats,
    order_list_create,
    # APIView (Class-Based)
    OrderListAPIView,
    OrderDetailAPIView,
    # ModelViewSet
    OrderViewSet,
)

# Router for ViewSet (automatic URL generation)
router = DefaultRouter()
router.register('', OrderViewSet, basename='order')

urlpatterns = [
    # =========================================================================
    # @api_view endpoints - registered with path() directly
    # =========================================================================
    path('health/', health_check, name='health-check'),
    path('stats/', order_stats, name='order-stats'),
    path('fn/', order_list_create, name='order-fn-list'),

    # =========================================================================
    # APIView endpoints - registered with path() + .as_view()
    # =========================================================================
    path('class/', OrderListAPIView.as_view(), name='order-class-list'),
    path('class/<int:pk>/', OrderDetailAPIView.as_view(), name='order-class-detail'),

    # =========================================================================
    # ViewSet endpoints - registered via router.include()
    # =========================================================================
    path('', include(router.urls)),
]
