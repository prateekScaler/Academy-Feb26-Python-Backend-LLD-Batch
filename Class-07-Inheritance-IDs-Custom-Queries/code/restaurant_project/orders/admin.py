# orders/admin.py
"""
Order admin with proxy model registrations.

This demonstrates how proxy models can be used to create
different admin views for the same data.
"""

from datetime import timedelta

from django.contrib import admin
from django.utils import timezone

from .models import Order, RecentOrder, ArchivedOrder, PendingOrder, OrderWithDualId


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Main Order admin - shows all orders."""
    list_display = ['short_id', 'customer_name', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer_name', 'customer_phone', 'id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    list_per_page = 25

    fieldsets = (
        ('Customer Info', {
            'fields': ('customer_name', 'customer_phone', 'customer_email')
        }),
        ('Order Details', {
            'fields': ('status', 'total_amount', 'notes')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def short_id(self, obj):
        """Display truncated UUID for readability."""
        return str(obj.id)[:8] + '...'
    short_id.short_description = 'ID'


@admin.register(RecentOrder)
class RecentOrderAdmin(admin.ModelAdmin):
    """
    Proxy model admin - shows only orders from last 7 days.

    This demonstrates how proxy models create separate admin views
    for the same underlying data.
    """
    list_display = ['short_id', 'customer_name', 'status', 'total_amount', 'created_at']
    list_filter = ['status']
    search_fields = ['customer_name', 'customer_phone']
    ordering = ['-created_at']

    def short_id(self, obj):
        return str(obj.id)[:8] + '...'
    short_id.short_description = 'ID'

    def has_add_permission(self, request):
        # Prevent adding through this view - use main Order admin
        return False


@admin.register(ArchivedOrder)
class ArchivedOrderAdmin(admin.ModelAdmin):
    """
    Proxy model admin - shows only orders older than 30 days.

    Useful for reviewing historical orders and generating reports.
    """
    list_display = ['short_id', 'customer_name', 'status', 'total_amount', 'created_at']
    list_filter = ['status']
    search_fields = ['customer_name', 'customer_phone']
    ordering = ['created_at']  # Oldest first for archives

    def short_id(self, obj):
        return str(obj.id)[:8] + '...'
    short_id.short_description = 'ID'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        # Prevent accidental deletion of archived orders
        return False


@admin.register(PendingOrder)
class PendingOrderAdmin(admin.ModelAdmin):
    """
    Proxy model admin - shows pending orders that need attention.

    Useful for kitchen/front desk to see orders waiting for action.
    """
    list_display = ['short_id', 'customer_name', 'total_amount', 'created_at', 'waiting_time']
    search_fields = ['customer_name', 'customer_phone']
    ordering = ['created_at']  # Oldest first - most urgent at top
    actions = ['confirm_orders', 'cancel_orders']

    def short_id(self, obj):
        return str(obj.id)[:8] + '...'
    short_id.short_description = 'ID'

    def waiting_time(self, obj):
        """Show how long the order has been waiting."""
        delta = timezone.now() - obj.created_at
        minutes = int(delta.total_seconds() / 60)
        if minutes < 60:
            return f"{minutes} min"
        hours = minutes // 60
        return f"{hours}h {minutes % 60}m"
    waiting_time.short_description = 'Waiting'

    def get_queryset(self, request):
        """Filter to show only pending orders."""
        return super().get_queryset(request).filter(status='pending')

    def has_add_permission(self, request):
        return False

    @admin.action(description='Confirm selected orders')
    def confirm_orders(self, request, queryset):
        count = 0
        for order in queryset:
            if order.confirm():
                count += 1
        self.message_user(request, f'{count} orders confirmed.')

    @admin.action(description='Cancel selected orders')
    def cancel_orders(self, request, queryset):
        count = 0
        for order in queryset:
            if order.cancel():
                count += 1
        self.message_user(request, f'{count} orders cancelled.')


@admin.register(OrderWithDualId)
class OrderWithDualIdAdmin(admin.ModelAdmin):
    """
    Admin for Dual ID example model.

    Shows both internal integer ID and external UUID.
    """
    list_display = ['id', 'short_public_id', 'customer_name', 'status', 'total_amount']
    list_filter = ['status']
    search_fields = ['customer_name', 'customer_phone', 'public_id']
    readonly_fields = ['id', 'public_id', 'created_at', 'updated_at']

    def short_public_id(self, obj):
        return str(obj.public_id)[:8] + '...'
    short_public_id.short_description = 'Public ID'
