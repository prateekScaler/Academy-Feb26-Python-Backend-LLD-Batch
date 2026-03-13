# orders/views.py
"""
Order ViewSet with filtering, searching, and ordering.

Features:
- Full CRUD via ModelViewSet
- Filtering by status (exact match)
- Search across customer_name, phone, notes
- Ordering by created_at, total_amount
- Custom actions using QuerySet methods
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Order
from .serializers import OrderSerializer, OrderListSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Order model with filtering capabilities.

    Endpoints:
        GET    /api/orders/              List all orders
        POST   /api/orders/              Create new order
        GET    /api/orders/{id}/         Get single order
        PUT    /api/orders/{id}/         Update order
        PATCH  /api/orders/{id}/         Partial update
        DELETE /api/orders/{id}/         Delete order

    Filtering:
        GET /api/orders/?status=pending
        GET /api/orders/?search=john
        GET /api/orders/?ordering=-total_amount

    Custom actions:
        GET  /api/orders/pending/         List pending orders
        GET  /api/orders/today/           List today's orders
        GET  /api/orders/needs-attention/ Orders needing action
        POST /api/orders/{id}/confirm/    Confirm an order
        POST /api/orders/{id}/cancel/     Cancel an order
    """

    serializer_class = OrderSerializer

    # Filter backends - enable filtering, search, ordering
    filter_backends = [
        DjangoFilterBackend,      # ?status=pending (exact match)
        filters.SearchFilter,      # ?search=john (partial match)
        filters.OrderingFilter,    # ?ordering=-created_at
    ]

    # Fields that can be filtered (exact match)
    filterset_fields = ['status']

    # Fields to search across (partial match, case-insensitive)
    search_fields = ['customer_name', 'customer_phone', 'notes']

    # Fields that can be used for ordering
    ordering_fields = ['created_at', 'total_amount', 'status']

    # Default ordering
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Return base queryset.
        Override this to add default filtering (e.g., hide cancelled orders).
        """
        return Order.objects.all()

    def get_serializer_class(self):
        """
        Use lighter serializer for list actions.
        """
        if self.action == 'list':
            return OrderListSerializer
        return OrderSerializer

    # =========================================================================
    # Custom Actions using QuerySet methods
    # =========================================================================

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """GET /api/orders/pending/ - List pending orders."""
        orders = Order.objects.pending()
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def today(self, request):
        """GET /api/orders/today/ - List today's orders."""
        orders = Order.objects.today()
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='needs-attention')
    def needs_attention(self, request):
        """GET /api/orders/needs-attention/ - Orders pending > 30 mins."""
        orders = Order.objects.needs_attention()
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='high-value')
    def high_value(self, request):
        """GET /api/orders/high-value/?min=100 - High value orders."""
        min_amount = request.query_params.get('min', 100)
        try:
            min_amount = float(min_amount)
        except ValueError:
            min_amount = 100

        orders = Order.objects.high_value(min_amount=min_amount)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """POST /api/orders/{id}/confirm/ - Confirm a pending order."""
        order = self.get_object()
        if order.confirm():
            serializer = self.get_serializer(order)
            return Response(serializer.data)
        return Response(
            {'error': 'Order cannot be confirmed (not pending)'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """POST /api/orders/{id}/cancel/ - Cancel an order."""
        order = self.get_object()
        if order.cancel():
            serializer = self.get_serializer(order)
            return Response(serializer.data)
        return Response(
            {'error': 'Order cannot be cancelled'},
            status=status.HTTP_400_BAD_REQUEST
        )
