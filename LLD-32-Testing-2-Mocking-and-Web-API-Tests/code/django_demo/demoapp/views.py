from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from demoapp.models import Event, Order
from demoapp.serializers import EventSerializer
from demoapp.gateways import stripe_gateway     # patched in tests


class IsOwner(permissions.BasePermission):
    """Object-level rule: only the event's owner may modify/delete it."""
    def has_object_permission(self, request, view, obj):
        return obj.owner_id == request.user.id


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Event.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)     # owner = the logged-in user


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def checkout(request):
    cart_id = request.data["cart_id"]
    amount_paise = 500_00
    receipt = stripe_gateway.charge(amount_paise)     # <- the boundary we patch
    order = Order.objects.create(
        cart_id=cart_id, amount_paise=amount_paise, receipt=receipt, status="PAID"
    )
    return Response({"order_id": order.id, "receipt": receipt},
                    status=status.HTTP_201_CREATED)
