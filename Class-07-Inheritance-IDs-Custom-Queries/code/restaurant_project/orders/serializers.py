# orders/serializers.py

from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model.

    Features:
    - Handles UUID serialization automatically
    - Read-only computed fields (status_display)
    - Field-level validation
    """

    # Read-only computed field
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id',  # UUID is serialized as string automatically
            'customer_name',
            'customer_phone',
            'status',
            'status_display',
            'total_amount',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_customer_name(self, value):
        """Customer name must be at least 2 characters."""
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Customer name must be at least 2 characters"
            )
        return value.strip()

    def validate_customer_phone(self, value):
        """Phone must be at least 10 digits."""
        digits_only = ''.join(filter(str.isdigit, value))
        if len(digits_only) < 10:
            raise serializers.ValidationError(
                "Phone number must have at least 10 digits"
            )
        return value

    def validate_total_amount(self, value):
        """Total amount cannot be negative."""
        if value < 0:
            raise serializers.ValidationError(
                "Total amount cannot be negative"
            )
        return value


class OrderListSerializer(serializers.ModelSerializer):
    """
    Lighter serializer for list views (fewer fields = faster).
    """
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = Order
        fields = ['id', 'customer_name', 'status', 'status_display', 'total_amount', 'created_at']
        read_only_fields = ['id', 'created_at']
