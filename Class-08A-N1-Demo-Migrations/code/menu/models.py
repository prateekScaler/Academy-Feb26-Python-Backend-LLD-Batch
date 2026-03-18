# menu/models.py
"""
Menu models demonstrating:
- Abstract base model inheritance (from core.models.TimestampedModel)
- Multi-table inheritance (Food, Beverage inherit from MenuItem)
- Simple ManyToMany (MenuItem ↔ Tag)
- ForeignKey (MenuItem → Category)

For Class 8: Cardinalities, N+1 Problem & Migrations
"""

from django.db import models

from core.models import TimestampedModel


# =============================================================================
# TAG MODEL - Simple ManyToMany Example
# =============================================================================

class Tag(models.Model):
    """
    Tags for menu items (Spicy, Vegan, Gluten-Free, Chef's Special, etc.)

    Simple ManyToMany: No extra fields needed on the relationship,
    so Django auto-creates the junction table: menu_menuitem_tags
    """
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(
        max_length=7,
        default='#6366f1',
        help_text="Hex color code for display (e.g., #ff0000)"
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(TimestampedModel):
    """A category for menu items."""
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class MenuItem(TimestampedModel):
    """
    A menu item.

    Relationships:
    - ForeignKey to Category (One-to-Many: Category has many MenuItems)
    - ManyToMany with Tag (Simple: no extra fields needed)
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_available = models.BooleanField(default=True)

    # ForeignKey: One-to-Many (Category → MenuItems)
    # ForeignKey goes on the MANY side!
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='items'  # category.items.all() and not category.menuitem_set.all()
    )

    # Simple ManyToMany: Django creates menu_menuitem_tags table
    # No through model needed - just linking items to tags
    tags = models.ManyToManyField(
        Tag,
        related_name='menu_items',
        blank=True  # Items can have no tags
    )

    class Meta:
        # NOTE: Avoid ordering by FK fields like ['category', 'name']
        # It causes Django to JOIN even on .all() queries!
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (₹{self.price})"


class Food(MenuItem):
    """A food menu item."""
    is_vegetarian = models.BooleanField(default=False)
    calories = models.PositiveIntegerField(null=True, blank=True)

class Beverage(MenuItem):
    """A beverage menu item."""
    is_alcoholic = models.BooleanField(default=False)
    volume_ml = models.PositiveIntegerField(null=True, blank=True)
