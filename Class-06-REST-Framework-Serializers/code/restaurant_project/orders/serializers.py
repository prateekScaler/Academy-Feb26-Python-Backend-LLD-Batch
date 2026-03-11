# orders/serializers.py

from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model.

    Handles:
    - Serialization: Order model → JSON (for GET requests)
    - Deserialization: JSON → Order model (for POST/PUT requests)
    - Validation: Ensures data integrity
    """

    # Read-only computed field
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'customer_name',
            'customer_phone',
            'status',
            'status_display',  # Shows "Pending" instead of "pending"
            'total_amount',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_customer_name(self, value):
        """Customer name must be at least 2 characters."""
        if len(value) < 2:
            raise serializers.ValidationError(
                "Customer name must be at least 2 characters"
            )
        return value

    def validate_customer_phone(self, value):
        """Phone must be at least 10 digits."""
        # Remove any non-digit characters for validation
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

    def validate_status(self, value):
        """
        Prevent invalid status transitions.
        Example: Can't change a 'delivered' order back to 'pending'.
        """
        if self.instance:  # Only on update (instance exists)
            current_status = self.instance.status

            # Can't change delivered orders
            if current_status == 'delivered' and value != 'delivered':
                raise serializers.ValidationError(
                    "Cannot change status of a delivered order"
                )

            # Can't change cancelled orders
            if current_status == 'cancelled' and value != 'cancelled':
                raise serializers.ValidationError(
                    "Cannot change status of a cancelled order"
                )

        return value
