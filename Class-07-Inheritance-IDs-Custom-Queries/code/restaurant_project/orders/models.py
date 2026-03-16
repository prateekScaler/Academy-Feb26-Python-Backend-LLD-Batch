# orders/models.py
"""
Order model demonstrating:
- UUID primary key (for security)
- Dual ID approach (integer + UUID)
- Inheritance from TimestampedModel (DRY)
- Custom QuerySet methods (reusable queries)
- Proxy models (different views of same data)
"""

import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone

from core.models import TimestampedModel


class OrderQuerySet(models.QuerySet):
    """
    Custom QuerySet methods for Order model.

    Benefits:
    - DRY: Define query logic once, use everywhere
    - Chainable: Order.objects.pending().today().high_value()
    - Testable: Easy to unit test query methods
    - Readable: Self-documenting code

    Usage:
        Order.objects.pending()
        Order.objects.active().today()
        Order.objects.high_value(min_amount=500)
    """

    def pending(self):
        """Get orders with status 'pending'."""
        return self.filter(status='pending')

    def confirmed(self):
        """Get orders with status 'confirmed'."""
        return self.filter(status='confirmed')

    def preparing(self):
        """Get orders being prepared."""
        return self.filter(status='preparing')

    def ready(self):
        """Get orders ready for pickup."""
        return self.filter(status='ready')

    def active(self):
        """Get orders that are still in progress (not cancelled/delivered)."""
        return self.exclude(status__in=['cancelled', 'delivered'])

    def completed(self):
        """Get delivered orders."""
        return self.filter(status='delivered')

    def cancelled(self):
        """Get cancelled orders."""
        return self.filter(status='cancelled')

    def today(self):
        """Get orders created today."""
        return self.filter(created_at__date=timezone.now().date())

    def this_week(self):
        """Get orders from the last 7 days."""
        week_ago = timezone.now() - timedelta(days=7)
        return self.filter(created_at__gte=week_ago)

    def this_month(self):
        """Get orders from the last 30 days."""
        month_ago = timezone.now() - timedelta(days=30)
        return self.filter(created_at__gte=month_ago)

    def older_than(self, days):
        """Get orders older than X days."""
        threshold = timezone.now() - timedelta(days=days)
        return self.filter(created_at__lt=threshold)

    def high_value(self, min_amount=100):
        """Get orders above a certain amount."""
        return self.filter(total_amount__gte=min_amount)

    def low_value(self, max_amount=50):
        """Get orders below a certain amount."""
        return self.filter(total_amount__lte=max_amount)

    def for_customer(self, name):
        """Search orders by customer name (case-insensitive)."""
        return self.filter(customer_name__icontains=name)

    def for_phone(self, phone):
        """Find orders by phone number."""
        return self.filter(customer_phone__icontains=phone)

    def needs_attention(self):
        """Orders that need action (pending for more than 30 minutes)."""
        threshold = timezone.now() - timedelta(minutes=30)
        return self.filter(status='pending', created_at__lte=threshold)


class Order(TimestampedModel):
    """
    A customer order in the restaurant.

    Features:
    - UUID primary key (can't be guessed by attackers)
    - Inherits created_at/updated_at from TimestampedModel
    - Custom QuerySet methods for common queries

    UUID Primary Key Approach:
        This model uses UUID as the primary key for security.
        See OrderWithDualId below for the dual ID approach.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    # UUID primary key - more secure than sequential integers
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15)
    customer_email = models.EmailField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    notes = models.TextField(blank=True)

    # created_at and updated_at are inherited from TimestampedModel!

    # Use custom QuerySet as the default manager
    objects = OrderQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {str(self.id)[:8]}... - {self.customer_name} ({self.status})"

    def confirm(self):
        """Confirm a pending order."""
        if self.status == 'pending':
            self.status = 'confirmed'
            self.save(update_fields=['status', 'updated_at'])
            return True
        return False

    def start_preparing(self):
        """Start preparing a confirmed order."""
        if self.status == 'confirmed':
            self.status = 'preparing'
            self.save(update_fields=['status', 'updated_at'])
            return True
        return False

    def mark_ready(self):
        """Mark order as ready for pickup."""
        if self.status == 'preparing':
            self.status = 'ready'
            self.save(update_fields=['status', 'updated_at'])
            return True
        return False

    def mark_delivered(self):
        """Mark order as delivered."""
        if self.status == 'ready':
            self.status = 'delivered'
            self.save(update_fields=['status', 'updated_at'])
            return True
        return False

    def cancel(self):
        """Cancel an order (if not already delivered)."""
        if self.status not in ['delivered', 'cancelled']:
            self.status = 'cancelled'
            self.save(update_fields=['status', 'updated_at'])
            return True
        return False


# =============================================================================
# PROXY MODELS - Same data, different behavior
# =============================================================================

class RecentOrderManager(models.Manager):
    """Manager that returns only recent orders (last 7 days)."""

    def get_queryset(self):
        week_ago = timezone.now() - timedelta(days=7)
        return super().get_queryset().filter(created_at__gte=week_ago)


class RecentOrder(Order):
    """
    Proxy model for recent orders (last 7 days).

    Use this in Django Admin for a "Recent Orders" view,
    or for dashboard displays.

    This is PROXY INHERITANCE:
    - No new database table created
    - Same data as Order, different Python class
    - Can have different managers, methods, ordering, etc.
    """

    objects = RecentOrderManager()

    class Meta:
        proxy = True
        ordering = ['-created_at']
        verbose_name = 'Recent Order'
        verbose_name_plural = 'Recent Orders (Last 7 Days)'


class ArchivedOrderManager(models.Manager):
    """Manager that returns only old orders (older than 30 days)."""

    def get_queryset(self):
        month_ago = timezone.now() - timedelta(days=30)
        return super().get_queryset().filter(created_at__lt=month_ago)


class ArchivedOrder(Order):
    """
    Proxy model for archived orders (older than 30 days).

    Use this in Django Admin for an "Archived Orders" view,
    or for generating historical reports.
    """

    objects = ArchivedOrderManager()

    class Meta:
        proxy = True
        ordering = ['created_at']  # Oldest first for archives
        verbose_name = 'Archived Order'
        verbose_name_plural = 'Archived Orders (> 30 Days)'


class PendingOrder(Order):
    """
    Proxy model for pending orders only.

    Useful for a "Needs Action" admin view.
    """

    class Meta:
        proxy = True
        verbose_name = 'Pending Order'
        verbose_name_plural = 'Pending Orders'

    @classmethod
    def needs_action(cls):
        """Get pending orders that need attention (> 30 min old)."""
        threshold = timezone.now() - timedelta(minutes=30)
        return cls.objects.filter(status='pending', created_at__lte=threshold)


# =============================================================================
# DUAL ID APPROACH - Keep integer internally, expose UUID externally
# =============================================================================

class OrderWithDualId(TimestampedModel):
    """
    Example of Dual ID approach.

    This keeps:
    - Integer ID as primary key (for database performance)
    - UUID as public_id (exposed in API for security)

    Benefits:
    - Integer primary keys are faster for JOINs and indexes
    - UUID public_id prevents enumeration attacks
    - Best of both worlds!

    Usage in ViewSet:
        class OrderViewSet(viewsets.ModelViewSet):
            queryset = OrderWithDualId.objects.all()
            serializer_class = OrderSerializer
            lookup_field = 'public_id'  # Use UUID in URLs!

    URLs become: /api/orders/550e8400-e29b-41d4.../
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    # Internal integer ID (auto-generated, used for JOINs)
    # This is Django's default - we're being explicit here
    id = models.BigAutoField(primary_key=True)

    # External UUID (exposed in API)
    public_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True  # Index for fast lookups
    )

    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    class Meta:
        verbose_name = 'Order (Dual ID)'
        verbose_name_plural = 'Orders (Dual ID)'

    def __str__(self):
        return f"Order #{self.id} ({self.public_id})"
