# core/models.py
"""
Abstract base models for the restaurant project.

These models don't create database tables - they provide common fields
that other models can inherit.
"""

from django.db import models


class TimestampedModel(models.Model):
    """
    Abstract base model that provides created_at and updated_at fields.

    Usage:
        class Order(TimestampedModel):
            customer_name = models.CharField(max_length=100)
            # created_at and updated_at are inherited automatically!

    Benefits:
        - DRY: Define timestamp fields once, use everywhere
        - Consistency: All models have the same timestamp field names
        - Maintainability: Change timestamp logic in one place
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # KEY! This model won't create a database table


class SoftDeleteModel(models.Model):
    """
    Abstract base model for soft delete functionality.

    Instead of actually deleting records, we mark them as deleted.
    This preserves data for auditing and allows "undelete".

    Usage:
        class Order(SoftDeleteModel):
            customer_name = models.CharField(max_length=100)

        # Soft delete
        order.delete()  # Sets deleted_at, doesn't remove from DB

        # Query only active records
        Order.objects.filter(deleted_at__isnull=True)
    """
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        """Soft delete - set deleted_at instead of removing."""
        from django.utils import timezone
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def hard_delete(self, *args, **kwargs):
        """Actually remove from database."""
        super().delete(*args, **kwargs)

    def restore(self):
        """Restore a soft-deleted record."""
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])

    @property
    def is_deleted(self):
        return self.deleted_at is not None


class BaseModel(TimestampedModel, SoftDeleteModel):
    """
    Combines timestamps and soft delete.

    Usage:
        class Order(BaseModel):
            customer_name = models.CharField(max_length=100)
            # Has: created_at, updated_at, deleted_at
    """

    class Meta:
        abstract = True
