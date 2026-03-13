# menu/models.py
"""
Multi-Table Inheritance Example

This demonstrates Django's multi-table inheritance where:
- Parent model (MenuItem) has common fields
- Child models (Food, Beverage) have type-specific fields
- Each model gets its own database table
- Child tables have a foreign key to parent table
"""

from django.db import models
from core.models import TimestampedModel


class Category(TimestampedModel):
    """Category for menu items - uses abstract inheritance."""
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class MenuItemQuerySet(models.QuerySet):
    """Custom QuerySet for MenuItem model."""

    def available(self):
        """Get available items only."""
        return self.filter(is_available=True)

    def unavailable(self):
        """Get unavailable items."""
        return self.filter(is_available=False)

    def in_category(self, category_name):
        """Filter by category name (case-insensitive)."""
        return self.filter(category__name__iexact=category_name)

    def price_range(self, min_price=0, max_price=1000):
        """Filter by price range."""
        return self.filter(price__gte=min_price, price__lte=max_price)

    def cheap(self, max_price=10):
        """Items under a certain price."""
        return self.filter(price__lt=max_price)

    def expensive(self, min_price=20):
        """Items over a certain price."""
        return self.filter(price__gt=min_price)

    def search(self, term):
        """Search in name and description."""
        from django.db.models import Q
        return self.filter(
            Q(name__icontains=term) | Q(description__icontains=term)
        )


class MenuItem(TimestampedModel):
    """
    Base menu item - parent class for multi-table inheritance.

    This creates a 'menu_menuitem' table with common fields.
    Food and Beverage will extend this with their own tables.

    Database structure:
        menu_menuitem: id, name, price, is_available, description, category_id
        menu_food: menuitem_ptr_id, is_vegetarian, spice_level, allergens
        menu_beverage: menuitem_ptr_id, size_ml, is_carbonated, caffeine_mg
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='items'
    )

    # Custom QuerySet as manager
    objects = MenuItemQuerySet.as_manager()

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} (${self.price})"


class Food(MenuItem):
    """
    Food item - extends MenuItem with food-specific fields.

    This is MULTI-TABLE INHERITANCE:
    - Creates 'menu_food' table with menuitem_ptr_id foreign key
    - Food instances have all MenuItem fields plus these
    - Querying Food requires JOIN with MenuItem table

    Usage:
        food = Food.objects.create(
            name='Margherita Pizza',
            price=12.99,
            category=pizzas,
            is_vegetarian=True,
            spice_level=1
        )
    """
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    spice_level = models.IntegerField(
        default=0,
        choices=[(i, str(i)) for i in range(6)],  # 0-5
        help_text="0 = Not spicy, 5 = Very spicy"
    )
    allergens = models.CharField(
        max_length=200,
        blank=True,
        help_text="Comma-separated list: gluten, dairy, nuts, etc."
    )
    preparation_time_minutes = models.PositiveIntegerField(
        default=15,
        help_text="Average preparation time in minutes"
    )

    class Meta:
        verbose_name_plural = 'Food items'

    def __str__(self):
        veg = " (V)" if self.is_vegetarian else ""
        return f"{self.name}{veg}"


class Beverage(MenuItem):
    """
    Beverage item - extends MenuItem with drink-specific fields.

    This is MULTI-TABLE INHERITANCE:
    - Creates 'menu_beverage' table with menuitem_ptr_id foreign key
    - Beverage instances have all MenuItem fields plus these

    Usage:
        drink = Beverage.objects.create(
            name='Cola',
            price=2.99,
            category=drinks,
            size_ml=500,
            is_carbonated=True
        )
    """
    SIZE_CHOICES = [
        (250, 'Small (250ml)'),
        (350, 'Medium (350ml)'),
        (500, 'Large (500ml)'),
        (750, 'Extra Large (750ml)'),
    ]

    size_ml = models.IntegerField(choices=SIZE_CHOICES, default=350)
    is_carbonated = models.BooleanField(default=False)
    is_alcoholic = models.BooleanField(default=False)
    caffeine_mg = models.PositiveIntegerField(
        default=0,
        help_text="Caffeine content in mg"
    )
    served_cold = models.BooleanField(
        default=True,
        help_text="True for cold drinks, False for hot"
    )

    def __str__(self):
        return f"{self.name} ({self.size_ml}ml)"


# Example queries with multi-table inheritance:
#
# Get all food items:
#   Food.objects.all()
#
# Get all beverages:
#   Beverage.objects.all()
#
# Get all menu items (including Food and Beverage):
#   MenuItem.objects.all()
#
# Access parent fields from child:
#   food = Food.objects.first()
#   print(food.name)        # From MenuItem
#   print(food.price)       # From MenuItem
#   print(food.spice_level) # From Food
#
# Check if a MenuItem is Food or Beverage:
#   item = MenuItem.objects.first()
#   if hasattr(item, 'food'):
#       print("This is food:", item.food.spice_level)
#   elif hasattr(item, 'beverage'):
#       print("This is beverage:", item.beverage.size_ml)
