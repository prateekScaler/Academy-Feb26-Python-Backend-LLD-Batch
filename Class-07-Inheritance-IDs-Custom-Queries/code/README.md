# Restaurant Project - Class 7: Inheritance, IDs & Custom Queries

This project demonstrates advanced Django patterns for cleaner, more maintainable code.

## What's New in Class 7

| Feature | Before | After |
|---------|--------|-------|
| Timestamps | Repeated in every model | Inherited from `TimestampedModel` |
| Order IDs | Sequential integers (1, 2, 3...) | UUIDs (can't be guessed) |
| Queries | Repeated filter logic | Custom QuerySet methods |
| Model types | Single model | Multi-table & Proxy inheritance |
| Admin views | One view per model | Multiple views via Proxy models |

## Three Types of Model Inheritance

| Type | Database | Use Case |
|------|----------|----------|
| **Abstract** | No parent table | Share fields (timestamps, audit) |
| **Multi-Table** | Parent + child tables | Food, Beverage extending MenuItem |
| **Proxy** | No new table | RecentOrder, ArchivedOrder views |

## Project Structure

```
restaurant_project/
├── core/                          # Shared base models
│   ├── models.py                  # TimestampedModel, SoftDeleteModel
│   └── ...
├── menu/                          # Multi-table inheritance example
│   ├── models.py                  # MenuItem → Food, Beverage
│   └── ...
├── orders/
│   ├── models.py                  # Order + Proxy models + Dual ID
│   ├── admin.py                   # Proxy model admin registration
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
└── ...
```

## Setup

```bash
cd restaurant_project
python -m venv venv
source venv/bin/activate
pip install django djangorestframework
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Django Shell Examples

### Model Inheritance

```python
# Abstract Inheritance - fields are copied to child tables
from orders.models import Order
order = Order.objects.create(
    customer_name='John',
    customer_phone='1234567890'
)
print(order.created_at)  # Inherited from TimestampedModel!

# Multi-Table Inheritance
from menu.models import Food, Beverage, MenuItem

# Create a food item
pizza = Food.objects.create(
    name='Margherita Pizza',
    price=12.99,
    category=appetizers,
    is_vegetarian=True,
    spice_level=1
)
print(pizza.name)         # From MenuItem
print(pizza.spice_level)  # From Food

# Create a beverage
cola = Beverage.objects.create(
    name='Cola',
    price=2.99,
    category=drinks,
    size_ml=500,
    is_carbonated=True
)
print(cola.name)    # From MenuItem
print(cola.size_ml) # From Beverage

# Query all menu items (includes Food and Beverage)
MenuItem.objects.all()

# Check type of a MenuItem
item = MenuItem.objects.first()
if hasattr(item, 'food'):
    print("This is food:", item.food.spice_level)
elif hasattr(item, 'beverage'):
    print("This is beverage:", item.beverage.size_ml)

# Proxy Models - same data, different view
from orders.models import RecentOrder, ArchivedOrder

# These query the same table with different filters
RecentOrder.objects.all()    # Orders from last 7 days
ArchivedOrder.objects.all()  # Orders older than 30 days
```

### Custom QuerySet Methods

```python
from orders.models import Order
from django.db.models import Q

# Custom QuerySet methods
Order.objects.pending()
Order.objects.active()
Order.objects.today()
Order.objects.high_value(min_amount=500)

# Chain them!
Order.objects.pending().today()
Order.objects.active().high_value()

# Q objects for complex queries
Order.objects.filter(
    Q(status='pending') | Q(status='confirmed')
)

Order.objects.filter(
    ~Q(status='cancelled')  # NOT cancelled
)

# Complex: (pending OR confirmed) AND high value
Order.objects.filter(
    (Q(status='pending') | Q(status='confirmed')) &
    Q(total_amount__gte=100)
)
```

### Dual ID Approach

```python
from orders.models import OrderWithDualId

# Create order with dual IDs
order = OrderWithDualId.objects.create(
    customer_name='Jane',
    customer_phone='9876543210',
    total_amount=75.00
)

print(order.id)         # Integer: 1 (for internal use)
print(order.public_id)  # UUID: 550e8400-... (for API)
```

---

# Assignment Questions

Complete these exercises to practice Class 7 concepts.

## Exercise 1: Abstract Base Models (Easy)

Update your existing models to inherit from `TimestampedModel`:

```python
from core.models import TimestampedModel

class Category(TimestampedModel):
    name = models.CharField(max_length=50)
    # created_at and updated_at are now inherited!

class MenuItem(TimestampedModel):
    name = models.CharField(max_length=100)
    # ...
```

**Question:** Do you need to run migrations after this change if the fields already exist?

**Answer:** No! The database structure is the same. The fields still exist, just defined elsewhere now.

---

## Exercise 2: Multi-Table Inheritance (Medium)

Create `Food` and `Beverage` models that inherit from `MenuItem`:

```python
class Food(MenuItem):
    is_vegetarian = models.BooleanField(default=False)
    spice_level = models.IntegerField(default=0)
    allergens = models.CharField(max_length=200, blank=True)

class Beverage(MenuItem):
    size_ml = models.IntegerField()
    is_carbonated = models.BooleanField(default=False)
    is_alcoholic = models.BooleanField(default=False)
```

**Test it:**
```python
# Create items
Food.objects.create(name='Pizza', price=12.99, category=main, is_vegetarian=True)
Beverage.objects.create(name='Cola', price=2.99, category=drinks, size_ml=500)

# Query
Food.objects.filter(is_vegetarian=True)
Beverage.objects.filter(is_carbonated=True)
MenuItem.objects.all()  # Returns both Food and Beverage
```

**Question:** How many database tables are created for these 3 models?

**Answer:** 3 tables: `menu_menuitem`, `menu_food`, `menu_beverage`. Food and Beverage have foreign keys to MenuItem.

---

## Exercise 3: Proxy Models (Medium)

Create proxy models for different admin views:

```python
class AvailableMenuItem(MenuItem):
    """Shows only available items."""
    class Meta:
        proxy = True
        verbose_name = 'Available Item'

    # In admin, override get_queryset to filter

class OutOfStockItem(MenuItem):
    """Shows only unavailable items."""
    class Meta:
        proxy = True
        verbose_name = 'Out of Stock Item'
```

**Register in admin.py:**
```python
@admin.register(AvailableMenuItem)
class AvailableMenuItemAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_available=True)

@admin.register(OutOfStockItem)
class OutOfStockItemAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_available=False)
```

---

## Exercise 4: Dual ID Approach (Medium)

Add a `public_id` field to MenuItem for API exposure:

```python
import uuid

class MenuItem(TimestampedModel):
    # Internal integer ID (default)
    public_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True
    )
    name = models.CharField(max_length=100)
    # ...
```

**Update ViewSet:**
```python
class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    lookup_field = 'public_id'  # Use UUID in URLs!
```

---

## Exercise 5: Custom QuerySet Methods (Medium)

Create custom QuerySet methods for MenuItem:

```python
class MenuItemQuerySet(models.QuerySet):
    def available(self):
        return self.filter(is_available=True)

    def in_category(self, category_name):
        return self.filter(category__name__iexact=category_name)

    def price_range(self, min_price=0, max_price=1000):
        return self.filter(price__gte=min_price, price__lte=max_price)

    def vegetarian(self):
        """Only works for Food items."""
        return self.filter(food__is_vegetarian=True)

    def search(self, term):
        from django.db.models import Q
        return self.filter(
            Q(name__icontains=term) | Q(description__icontains=term)
        )

class MenuItem(TimestampedModel):
    # ...
    objects = MenuItemQuerySet.as_manager()
```

**Test:**
```python
MenuItem.objects.available()
MenuItem.objects.available().in_category('desserts')
MenuItem.objects.price_range(5, 15).available()
```

---

## Exercise 6: Complex Q Object Queries (Hard)

Write queries using Q objects:

```python
from django.db.models import Q

# 1. Available items that are EITHER cheap (<$10) OR in Appetizers
MenuItem.objects.filter(
    Q(is_available=True) &
    (Q(price__lt=10) | Q(category__name='Appetizers'))
)

# 2. Orders that are (pending OR confirmed) AND NOT from test customers
Order.objects.filter(
    (Q(status='pending') | Q(status='confirmed')) &
    ~Q(customer_name__icontains='test')
)

# 3. High-value pending orders that need attention (> 30 min old)
from django.utils import timezone
from datetime import timedelta

threshold = timezone.now() - timedelta(minutes=30)
Order.objects.filter(
    Q(status='pending') &
    Q(total_amount__gte=100) &
    Q(created_at__lte=threshold)
)
```

---

## Exercise 7: Order Statistics Endpoint (Hard)

Add a custom action to OrderViewSet that returns statistics:

```python
from django.db.models import Count, Sum, Avg
from rest_framework.decorators import action
from rest_framework.response import Response

class OrderViewSet(viewsets.ModelViewSet):
    # ...

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """GET /api/orders/stats/"""
        queryset = self.get_queryset()

        return Response({
            'total_orders': queryset.count(),
            'pending': queryset.pending().count(),
            'today': queryset.today().count(),
            'total_revenue': queryset.completed().aggregate(
                total=Sum('total_amount')
            )['total'] or 0,
            'average_order_value': queryset.completed().aggregate(
                avg=Avg('total_amount')
            )['avg'] or 0,
            'by_status': list(queryset.values('status').annotate(
                count=Count('id')
            )),
        })
```

---

## Quick Reference

### Inheritance Types

| Type | `Meta` Setting | Database |
|------|----------------|----------|
| Abstract | `abstract = True` | No parent table |
| Multi-Table | (default) | Parent + child tables |
| Proxy | `proxy = True` | No new table |

### QuerySet Methods Created

| Method | Returns |
|--------|---------|
| `.pending()` | Orders with status='pending' |
| `.active()` | Non-cancelled, non-delivered |
| `.today()` | Created today |
| `.high_value(min)` | Orders >= min amount |
| `.needs_attention()` | Pending > 30 mins |

### Q Object Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `\|` | OR | `Q(a=1) \| Q(b=2)` |
| `&` | AND | `Q(a=1) & Q(b=2)` |
| `~` | NOT | `~Q(a=1)` |

### Field Lookups

| Lookup | SQL | Example |
|--------|-----|---------|
| `__gte` | `>=` | `price__gte=10` |
| `__lte` | `<=` | `price__lte=20` |
| `__range` | BETWEEN | `price__range=(10, 20)` |
| `__icontains` | ILIKE %...% | `name__icontains='pizza'` |
| `__in` | IN (...) | `status__in=['a', 'b']` |

---

*Class 7 - Inheritance, IDs & Custom Queries*
