# orders/models.py
"""
Order models demonstrating:
- ForeignKey (One-to-Many)
- OneToOneField (One-to-One)
- ManyToManyField with through model
- Custom QuerySet with chainable methods
- Proxy models for different views
- Query optimization with prefetch_related

For Class 8: Cardinalities, N+1 Problem & Migrations
"""

from django.db import models
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from core.models import TimestampedModel


# =============================================================================
# CUSTOM QUERYSET
# =============================================================================

class OrderQuerySet(models.QuerySet):
    """
    Custom QuerySet for Order model.
    Encapsulates common query patterns and optimizations.

    Usage:
        Order.objects.pending()
        Order.objects.active().today().with_items()
    """

    def with_items(self):
        """
        Prefetch order items and their menu items.
        CRITICAL: This solves the N+1 problem!

        Without this: 1 + N + M queries
        With this:    3 queries total
        """
        return self.prefetch_related('items__menu_item')

    def with_items_and_category(self):
        """
        Prefetch order items, menu items, AND their categories.
        Use when you need to access item.menu_item.category
        """
        return self.prefetch_related('items__menu_item__category')

    def pending(self):
        """Orders waiting to be prepared."""
        return self.filter(status='pending')

    def preparing(self):
        """Orders currently being prepared."""
        return self.filter(status='preparing')

    def ready(self):
        """Orders ready for pickup/delivery."""
        return self.filter(status='ready')

    def completed(self):
        """Successfully delivered/picked up orders."""
        return self.filter(status='completed')

    def cancelled(self):
        """Cancelled orders."""
        return self.filter(status='cancelled')

    def active(self):
        """Non-cancelled, non-completed orders (need attention)."""
        return self.exclude(status__in=['cancelled', 'completed'])

    def today(self):
        """Orders created today."""
        return self.filter(created_at__date=timezone.now().date())

    def this_week(self):
        """Orders from the last 7 days."""
        week_ago = timezone.now() - timedelta(days=7)
        return self.filter(created_at__gte=week_ago)

    def high_value(self, min_amount=500):
        """Orders with total_price >= min_amount."""
        return self.filter(total_price__gte=min_amount)

    def for_customer(self, email):
        """Orders for a specific customer (case-insensitive email match)."""
        return self.filter(customer_email__iexact=email)

    def needs_attention(self):
        """
        Pending orders that are older than 30 minutes.
        These might need follow-up!
        """
        threshold = timezone.now() - timedelta(minutes=30)
        return self.filter(
            status='pending',
            created_at__lte=threshold
        )


# =============================================================================
# ORDER MODEL
# =============================================================================

class Order(TimestampedModel):
    """
    Restaurant order with customer details and status tracking.

    Relationships demonstrated:
    - ManyToMany with MenuItem through OrderItem (see menu_items field)
    - OneToOne with OrderInvoice (see OrderInvoice model below)
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    mobile_number = models.CharField(max_length=15, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Calculated from order items, or can be set manually"
    )
    notes = models.TextField(blank=True)

    # ManyToMany through OrderItem
    # This allows: order.menu_items.all() to get MenuItems directly
    # For accessing quantity/price, use: order.items.all() to get OrderItems
    menu_items = models.ManyToManyField(
        'menu.MenuItem',
        through='OrderItem',
        related_name='orders'
    )

    # Attach custom QuerySet as the default manager
    objects = OrderQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name} ({self.status})"

    def calculate_total(self):
        """Calculate total from order items."""
        return sum(item.subtotal for item in self.items.all())

    def generate_invoice(self):
        """Generate an invoice for this order if one doesn't exist."""
        if hasattr(self, 'invoice'):
            return self.invoice

        year = timezone.now().year
        invoice_number = f"INV-{year}-{self.id:06d}"

        return OrderInvoice.objects.create(
            order=self,
            invoice_number=invoice_number
        )


# =============================================================================
# ORDER ITEM - Through Model for ManyToMany
# =============================================================================

class OrderItem(models.Model):
    """
    Through model for Order-MenuItem relationship.

    Why a through model instead of simple ManyToMany?
    - We need to store quantity (how many of each item)
    - We need to store unit_price (price at time of order - menu price might change!)

    This creates the relationship:
    Order (1) -------- (N) OrderItem (N) -------- (1) MenuItem
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,  # Delete items when order is deleted
        related_name='items'       # order.items.all()
    )
    menu_item = models.ForeignKey(
        'menu.MenuItem',
        on_delete=models.PROTECT,  # Don't allow deleting menu items that are in orders!
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Price at time of order (may differ from current menu price)"
    )

    class Meta:
        # Prevent duplicate items in same order
        unique_together = ['order', 'menu_item']

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"

    @property
    def subtotal(self):
        """Calculate subtotal for this line item."""
        return Decimal(self.quantity) * self.unit_price


# =============================================================================
# ORDER INVOICE - OneToOne Relationship
# =============================================================================

class OrderInvoice(models.Model):
    """
    Invoice for an order - demonstrates OneToOneField.

    One Order has exactly One Invoice.
    Access: order.invoice (not order.invoice_set!)
    """

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,  # Delete invoice when order is deleted
        related_name='invoice'     # order.invoice and you don't need to do order.OrderInvoice
    )
    invoice_number = models.CharField(
        max_length=20,
        unique=True
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    pdf_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Invoice {self.invoice_number}"


# =============================================================================
# PROXY MODELS - Different Views of Same Table
# =============================================================================

class RecentOrderManager(models.Manager):
    """Manager that filters to only recent orders (last 7 days)."""
    def get_queryset(self):
        week_ago = timezone.now() - timedelta(days=7)
        return super().get_queryset().filter(created_at__gte=week_ago)


class RecentOrder(Order):
    """
    Proxy model for recent orders.
    Same table as Order, but with filtered default queryset.
    Useful for Django Admin separate section.
    """
    objects = RecentOrderManager()

    class Meta:
        proxy = True
        verbose_name = "Recent Order"
        verbose_name_plural = "Recent Orders"


class ArchivedOrderManager(models.Manager):
    """Manager that filters to only archived orders (older than 7 days)."""
    def get_queryset(self):
        week_ago = timezone.now() - timedelta(days=7)
        return super().get_queryset().filter(created_at__lt=week_ago)


class ArchivedOrder(Order):
    """
    Proxy model for archived orders.
    Same table as Order, but filtered to older orders.
    """
    objects = ArchivedOrderManager()

    class Meta:
        proxy = True
        verbose_name = "Archived Order"
        verbose_name_plural = "Archived Orders"
        ordering = ['created_at']  # Oldest first for archives
