# orders/serializers.py
"""
Order serializers demonstrating DRF validation patterns.

This file shows:
- Field-level validation (validate_<field_name>)
- Cross-field/Object-level validation (validate)
- read_only_fields
- SerializerMethodField
- source attribute
"""

from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    """
    Full serializer for Order model with validation examples.

    Validation Flow (when is_valid() is called):
    1. Field type validation (automatic - IntegerField, EmailField, etc.)
    2. validate_<field_name>() methods (per-field custom validation)
    3. validate() method (cross-field/object-level validation)
    """

    # Read-only computed field using SerializerMethodField
    status_display = serializers.SerializerMethodField()

    # Alternative: Use 'source' for simple attribute access
    # status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'customer_name',
            'customer_email',
            'mobile_number',
            'total_price',
            'status',
            'status_display',  # Read-only computed field
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_status_display(self, obj):
        """SerializerMethodField: method name must be get_<field_name>"""
        return obj.get_status_display()

    # =========================================================================
    # FIELD-LEVEL VALIDATION
    # Method name MUST be: validate_<field_name>
    # =========================================================================

    def validate_customer_name(self, value):
        """
        Validate customer_name field.

        IMPORTANT: Method name must EXACTLY match validate_<field_name>
        - validate_customer_name ✓
        - validateCustomerName ✗ (won't be called)
        - check_customer_name ✗ (won't be called)
        """
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Customer name must be at least 2 characters"
            )
        # Always return the (possibly modified) value
        return value.strip().title()  # Normalize: "  john DOE  " -> "John Doe"

    def validate_customer_email(self, value):
        """Validate and normalize email."""
        # Email format is already validated by EmailField
        # We can add additional business rules
        if value.endswith('@test.com'):
            raise serializers.ValidationError(
                "Test emails are not allowed"
            )
        return value.lower()  # Normalize to lowercase

    def validate_mobile_number(self, value):
        """Validate mobile number format."""
        if value:  # Only validate if provided (field is optional)
            digits_only = ''.join(filter(str.isdigit, value))
            if len(digits_only) < 10 or len(digits_only) > 15:
                raise serializers.ValidationError(
                    "Mobile number must be 10-15 digits"
                )
        return value

    def validate_total_price(self, value):
        """Validate total_price is positive."""
        if value < 0:
            raise serializers.ValidationError(
                "Total price cannot be negative"
            )
        if value > 100000:
            raise serializers.ValidationError(
                "Total price exceeds maximum limit of ₹1,00,000"
            )
        return value

    def validate_status(self, value):
        """Validate status transitions (simplified)."""
        # In real app, you'd check current status and validate transitions
        valid_statuses = ['pending', 'preparing', 'ready', 'completed', 'cancelled']
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        return value

    # =========================================================================
    # OBJECT-LEVEL / CROSS-FIELD VALIDATION
    # Use validate() when you need to compare multiple fields
    # =========================================================================

    def validate(self, attrs):
        """
        Cross-field validation.

        Called AFTER all field-level validations pass.
        Use this when validation depends on multiple fields.
        """
        # Example 1: High-value orders need notes
        total_price = attrs.get('total_price', 0)
        notes = attrs.get('notes', '')

        if total_price > 500 and not notes.strip():
            raise serializers.ValidationError({
                'notes': "Notes are required for orders over ₹500"
            })

        # Example 2: Cancelled orders should have a reason in notes
        status = attrs.get('status', 'pending')
        if status == 'cancelled' and not notes.strip():
            raise serializers.ValidationError({
                'notes': "Please provide a reason for cancellation"
            })

        return attrs


class OrderListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views.

    Use different serializers for different actions:
    - List view: fewer fields, faster
    - Detail view: all fields
    """

    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'customer_name',
            'status',
            'status_display',
            'total_price',
            'created_at',
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for creating orders.

    Demonstrates: different serializers for different operations.
    """

    class Meta:
        model = Order
        fields = [
            'customer_name',
            'customer_email',
            'mobile_number',
            'total_price',
            'notes',
        ]
        # Status defaults to 'pending', so not included here


class OrderStatusSerializer(serializers.Serializer):
    """
    Non-model serializer for status update endpoint.

    Demonstrates: serializers don't always need a model!
    """

    status = serializers.ChoiceField(
        choices=['pending', 'preparing', 'ready', 'completed', 'cancelled']
    )
    reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        """Require reason for cancellation."""
        if attrs.get('status') == 'cancelled' and not attrs.get('reason'):
            raise serializers.ValidationError({
                'reason': "Reason is required when cancelling an order"
            })
        return attrs
