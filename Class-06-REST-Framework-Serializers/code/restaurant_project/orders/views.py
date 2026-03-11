# orders/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from .models import Order
from .serializers import OrderSerializer


# =============================================================================
# Option 1: Function-Based Views with @api_view
# Good for: Simple endpoints, learning DRF
# =============================================================================

@api_view(['GET', 'POST'])
def order_list(request):
    """
    GET:  List all orders
    POST: Create a new order
    """
    if request.method == 'GET':
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def order_detail(request, pk):
    """
    GET:    Retrieve a single order
    PUT:    Update entire order
    PATCH:  Partial update
    DELETE: Delete order
    """
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response(
            {'error': 'Order not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = OrderSerializer(order, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# =============================================================================
# Option 2: ViewSet (Recommended for full CRUD)
# This single class replaces BOTH functions above!
# =============================================================================

class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Order model - provides full CRUD automatically.

    GET    /api/orders/         → list all orders
    POST   /api/orders/         → create new order
    GET    /api/orders/{id}/    → retrieve single order
    PUT    /api/orders/{id}/    → full update
    PATCH  /api/orders/{id}/    → partial update
    DELETE /api/orders/{id}/    → delete order
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    # Custom action: GET /api/orders/pending/
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending orders."""
        pending_orders = Order.objects.filter(status='pending')
        serializer = self.get_serializer(pending_orders, many=True)
        return Response(serializer.data)

    # Custom action: POST /api/orders/{id}/confirm/
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a pending order."""
        order = self.get_object()
        if order.status != 'pending':
            return Response(
                {'error': 'Only pending orders can be confirmed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.status = 'confirmed'
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)
