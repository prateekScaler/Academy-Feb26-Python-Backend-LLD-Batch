# orders/views.py
"""
Order views demonstrating 3 types of DRF views:

1. @api_view (Function-Based) - Simple, one-off endpoints
2. APIView (Class-Based) - More control, manual method handling
3. ModelViewSet (ViewSet) - Full CRUD with automatic routing

When to use which:
┌─────────────────────┬──────────────────────────────────────────┐
│ View Type           │ Use When                                 │
├─────────────────────┼──────────────────────────────────────────┤
│ @api_view           │ Simple endpoints (health, stats)         │
│ APIView             │ Complex logic, manual control            │
│ ModelViewSet        │ Full CRUD operations on a model          │
└─────────────────────┴──────────────────────────────────────────┘
"""

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from .serializers import (
    OrderSerializer,
    OrderListSerializer,
    OrderCreateSerializer,
    OrderStatusSerializer,
)


# =============================================================================
# 1. @api_view - Function-Based Views
# =============================================================================
# Best for: Simple, stateless endpoints that don't map to a model's CRUD
# URL Registration: path('health/', views.health_check)

@api_view(['GET'])
def health_check(request):
    """
    Simple health check endpoint.

    Usage: GET /api/orders/health/

    @api_view decorator:
    - Converts function into DRF view
    - Provides Request/Response objects
    - Handles content negotiation
    """
    return Response({
        'status': 'healthy',
        'service': 'orders'
    })


@api_view(['GET'])
def order_stats(request):
    """
    Order statistics endpoint.

    Usage: GET /api/orders/stats/

    Demonstrates: Aggregating data without CRUD operations
    """
    from django.db.models import Sum, Avg, Count

    stats = Order.objects.aggregate(
        total_orders=Count('id'),
        total_revenue=Sum('total_price'),
        average_order_value=Avg('total_price'),
    )

    # Add status breakdown
    status_counts = {}
    for status_choice, _ in Order.STATUS_CHOICES:
        status_counts[status_choice] = Order.objects.filter(
            status=status_choice
        ).count()

    return Response({
        'total_orders': stats['total_orders'] or 0,
        'total_revenue': float(stats['total_revenue'] or 0),
        'average_order_value': round(float(stats['average_order_value'] or 0), 2),
        'by_status': status_counts,
    })


@api_view(['GET', 'POST'])
def order_list_create(request):
    """
    List and create orders using @api_view.

    Demonstrates: Handling multiple HTTP methods in function view

    Usage:
        GET  /api/orders/fn/     -> List all orders
        POST /api/orders/fn/     -> Create new order
    """
    if request.method == 'GET':
        orders = Order.objects.all()
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =============================================================================
# 2. APIView - Class-Based Views
# =============================================================================
# Best for: More complex logic, when you need instance methods, mixins
# URL Registration: path('orders/', OrderListAPIView.as_view())

class OrderListAPIView(APIView):
    """
    List and create orders using APIView.

    Usage:
        GET  /api/orders/class/     -> List all orders
        POST /api/orders/class/     -> Create new order

    APIView benefits over @api_view:
    - Class attributes for configuration
    - Method handlers (get, post, put, etc.)
    - Can use mixins for common patterns
    - Easier to extend/override behavior
    """

    def get(self, request):
        """GET /api/orders/class/ - List all orders"""
        orders = Order.objects.all()
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        """POST /api/orders/class/ - Create new order"""
        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailAPIView(APIView):
    """
    Retrieve, update, delete a single order using APIView.

    Usage:
        GET    /api/orders/class/<id>/     -> Retrieve
        PUT    /api/orders/class/<id>/     -> Full update
        PATCH  /api/orders/class/<id>/     -> Partial update
        DELETE /api/orders/class/<id>/     -> Delete
    """

    def get_object(self, pk):
        """Helper method to get order or raise 404."""
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return None

    def get(self, request, pk):
        """GET - Retrieve single order"""
        order = self.get_object(pk)
        if order is None:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def put(self, request, pk):
        """PUT - Full update (all fields required)"""
        order = self.get_object(pk)
        if order is None:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = OrderSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """PATCH - Partial update (only provided fields)"""
        order = self.get_object(pk)
        if order is None:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        # partial=True allows partial updates
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """DELETE - Remove order"""
        order = self.get_object(pk)
        if order is None:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# =============================================================================
# 3. ModelViewSet - Full CRUD with Router
# =============================================================================
# Best for: Standard CRUD operations with automatic URL routing
# URL Registration: router.register('orders', OrderViewSet)

class OrderViewSet(viewsets.ModelViewSet):
    """
    Full CRUD ViewSet for Order model.

    Automatically provides:
        GET    /api/orders/           -> list()
        POST   /api/orders/           -> create()
        GET    /api/orders/{id}/      -> retrieve()
        PUT    /api/orders/{id}/      -> update()
        PATCH  /api/orders/{id}/      -> partial_update()
        DELETE /api/orders/{id}/      -> destroy()

    Custom actions (using @action decorator):
        GET    /api/orders/pending/        -> pending()
        POST   /api/orders/{id}/cancel/    -> cancel()
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_serializer_class(self):
        """
        Use different serializers for different actions.

        This is a common pattern:
        - List view: lightweight serializer (faster)
        - Detail/Create: full serializer
        """
        if self.action == 'list':
            return OrderListSerializer
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    # -------------------------------------------------------------------------
    # Custom Actions using @action decorator
    # -------------------------------------------------------------------------

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """
        GET /api/orders/pending/

        detail=False -> Collection action (no pk in URL)
        """
        pending_orders = self.queryset.filter(status='pending')
        serializer = self.get_serializer(pending_orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def today(self, request):
        """GET /api/orders/today/"""
        from django.utils import timezone
        today = timezone.now().date()
        orders = self.queryset.filter(created_at__date=today)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        POST /api/orders/{id}/cancel/

        detail=True -> Instance action (pk required in URL)

        Why POST instead of PATCH?
        - Explicit action endpoint (business logic)
        - Easier to add permissions, logging
        - Encapsulates the "cancel" operation
        """
        order = self.get_object()

        if order.status in ['completed', 'cancelled']:
            return Response(
                {'error': f'Cannot cancel order with status: {order.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = 'cancelled'
        order.save(update_fields=['status', 'updated_at'])

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """POST /api/orders/{id}/confirm/ - Move to 'preparing'"""
        order = self.get_object()

        if order.status != 'pending':
            return Response(
                {'error': 'Only pending orders can be confirmed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = 'preparing'
        order.save(update_fields=['status', 'updated_at'])

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='mark-ready')
    def mark_ready(self, request, pk=None):
        """
        POST /api/orders/{id}/mark-ready/

        url_path: Custom URL path (default would be 'mark_ready')
        """
        order = self.get_object()

        if order.status != 'preparing':
            return Response(
                {'error': 'Only preparing orders can be marked ready'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = 'ready'
        order.save(update_fields=['status', 'updated_at'])

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """POST /api/orders/{id}/complete/ - Mark as completed"""
        order = self.get_object()

        if order.status != 'ready':
            return Response(
                {'error': 'Only ready orders can be completed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = 'completed'
        order.save(update_fields=['status', 'updated_at'])

        serializer = self.get_serializer(order)
        return Response(serializer.data)
