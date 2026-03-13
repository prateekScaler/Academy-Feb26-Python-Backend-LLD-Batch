# Class 7: Inheritance, IDs & Custom Queries

## Pre-Class Quiz: Test Your Class 6 Knowledge

### Question 1: Serializer Output
```python
# Django Shell
>>> from orders.models import Order
>>> from orders.serializers import OrderSerializer
>>> order = Order.objects.first()
>>> serializer = OrderSerializer(order)
>>> type(serializer.data)
```
**What does `type(serializer.data)` return?**

<details>
<summary>Answer</summary>

**`<class 'rest_framework.utils.serializer_helpers.ReturnDict'>`** (essentially a dictionary)

When you pass a model instance to a serializer (without `data=`), it **serializes** the object — converting Python objects (Decimal, datetime, UUID) into JSON-compatible types (strings, lists, dicts).

</details>

---

### Question 2: HTTP Method Design
You need to add a "cancel order" feature. The order remains in the database but its status changes to "cancelled".

**Which HTTP method should you use?**
- A) DELETE /api/orders/{id}/
- B) POST /api/orders/{id}/cancel/
- C) PATCH /api/orders/{id}/ with {status: "cancelled"}

<details>
<summary>Answer</summary>

**B) POST /api/orders/{id}/cancel/** is the best choice.

**Understanding HTTP Method Idempotency:**

| Method | Idempotent? | Meaning |
|--------|-------------|---------|
| GET | Yes | Multiple calls return same result |
| PUT | Yes | Multiple calls have same effect as one |
| DELETE | Yes | Resource stays deleted after first call |
| POST | No | Each call may create new side effects |

**Why not the others?**
- **DELETE** implies the resource is removed. Cancelled orders should remain in the database for records.
- **PATCH with status in payload** exposes internal implementation details. What if "cancellation" later requires additional logic (refund, email notification, inventory update)? A dedicated action endpoint:
  - Encapsulates business logic
  - Is more explicit about intent
  - Easier to add permissions/logging
  - Doesn't expose your data model

POST to an action endpoint (like `/cancel/`) is RESTful for state-changing operations that aren't simple CRUD.

</details>

---

### Question 3: ModelViewSet Validation
```python
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['customer_name', 'total_amount', 'discount']
```
**Where do you add validation to ensure `total_amount` is positive?**

<details>
<summary>Answer</summary>

**Field-level validation:** Add a `validate_total_amount` method:

```python
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['customer_name', 'total_amount', 'discount']

    def validate_total_amount(self, value):
        """Field-level validation: validates single field"""
        if value < 0:
            raise serializers.ValidationError("Amount cannot be negative")
        return value
```

**Cross-field validation:** Use `validate()` method for validations involving multiple fields:

```python
    def validate(self, attrs):
        """Object-level validation: validates multiple fields together"""
        total = attrs.get('total_amount', 0)
        discount = attrs.get('discount', 0)
        if discount > total:
            raise serializers.ValidationError({
                'discount': "Discount cannot exceed total amount"
            })
        return attrs
```

DRF automatically calls `validate_<field_name>()` for each field, then `validate()` for the whole object.

</details>

---

### Question 4: @api_view vs ModelViewSet
When would you use `@api_view` instead of `ModelViewSet`?

<details>
<summary>Answer</summary>

**Use `@api_view` for:**
- Simple, one-off endpoints that don't map to a model
- Utility endpoints (health checks, stats, custom actions)
- When you need more control over the response format

**Use `ModelViewSet` for:**
- Full CRUD operations on a model
- When you want automatic URL routing
- Standard REST APIs with filtering, pagination, etc.

**Example `@api_view`:**
```python
# views.py
@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy'})

@api_view(['GET'])
def order_stats(request):
    return Response({
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.pending().count(),
    })
```

**Registering @api_view in urls.py:**
```python
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health-check'),
    path('stats/', views.order_stats, name='order-stats'),
]
```

Unlike ViewSets (which use Routers), `@api_view` functions are registered directly with `path()`.

</details>

---

## Learning Objectives

By the end of this class, you will:

1. Understand all 3 types of Django model inheritance
2. Know when to use UUIDs vs auto-incrementing IDs
3. Implement dual ID approach for better security and performance
4. Write complex queries using Q objects
5. Create custom QuerySet methods and Managers

---

## Part 1: Model Inheritance

Django provides **3 types** of model inheritance, each solving different problems.

### Type 1: Abstract Base Classes

**Problem:** Copy-pasting `created_at` and `updated_at` into every model.

**Solution:**
```python
# core/models.py
class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # No database table created!

# orders/models.py
class Order(TimestampedModel):
    customer_name = models.CharField(max_length=100)
    # created_at and updated_at are inherited!
```

**Key Point:** `abstract = True` means no database table is created. Fields are copied into child models.

**Best Practice:** Put abstract base models in a `core` app that other apps can import from. This keeps shared functionality centralized and avoids circular imports.

```
my_project/
├── core/
│   └── models.py       # TimestampedModel, SoftDeleteModel
├── orders/
│   └── models.py       # from core.models import TimestampedModel
├── menu/
│   └── models.py       # from core.models import TimestampedModel
```

**Use When:** You want to share fields/methods across models without creating a database relationship.

---

### Type 2: Multi-Table Inheritance

**Problem:** Food items and Beverages are both menu items, but have type-specific fields.

**Solution:**
```python
# menu/models.py
class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_available = models.BooleanField(default=True)

class Food(MenuItem):
    is_vegetarian = models.BooleanField(default=False)
    spice_level = models.IntegerField(default=0)  # 0-5
    # Automatically gets: name, price, is_available

class Beverage(MenuItem):
    size_ml = models.IntegerField()
    is_carbonated = models.BooleanField(default=False)
    # Automatically gets: name, price, is_available
```

**Database Structure:**
```
menuitem table:
| id | name    | price | is_available |
|----|---------|-------|--------------|
| 1  | Pizza   | 12.99 | true         |
| 2  | Cola    | 2.99  | true         |

food table:
| menuitem_ptr_id | is_vegetarian | spice_level |
|-----------------|---------------|-------------|
| 1               | false         | 2           |

beverage table:
| menuitem_ptr_id | size_ml | is_carbonated |
|-----------------|---------|---------------|
| 2               | 500     | true          |
```

**Use When:** Child models ARE the parent type and need their own additional fields.

**Trade-off:** Querying requires JOINs. Don't overuse this pattern.

---

### Type 3: Proxy Models

**Problem:** You want different behaviors (methods, default ordering, managers) without changing the database.

**Solution:**
```python
# orders/models.py
class Order(TimestampedModel):
    customer_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

class RecentOrder(Order):
    """Orders from the last 7 days - for dashboard."""
    class Meta:
        proxy = True
        ordering = ['-created_at']

    @classmethod
    def get_queryset(cls):
        from datetime import timedelta
        from django.utils import timezone
        week_ago = timezone.now() - timedelta(days=7)
        return cls.objects.filter(created_at__gte=week_ago)

class ArchivedOrder(Order):
    """Orders older than 30 days - for reports."""
    class Meta:
        proxy = True

    @classmethod
    def get_queryset(cls):
        from datetime import timedelta
        from django.utils import timezone
        month_ago = timezone.now() - timedelta(days=30)
        return cls.objects.filter(created_at__lt=month_ago)
```

**Use in Admin:**
```python
# admin.py
@admin.register(RecentOrder)
class RecentOrderAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'status', 'created_at']

@admin.register(ArchivedOrder)
class ArchivedOrderAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'status', 'created_at']
```

**Use When:** Same data, different behavior. Great for admin views, reports, or different API endpoints.

---

### Inheritance Summary

| Type | Database Tables | Use Case |
|------|-----------------|----------|
| **Abstract** | Only child tables | Share common fields (timestamps, audit fields) |
| **Multi-Table** | Parent + child tables | True "is-a" relationships with extra fields |
| **Proxy** | No new tables | Different behavior/interface for same data |

---

## Part 2: IDs & Primary Keys

### The German Tank Problem

During World War II, Allied statisticians figured out German tank production rates by analyzing serial numbers on captured tanks. Sequential numbers like 1, 2, 3... revealed:
- Total production capacity
- Manufacturing timeline
- Factory output rates

**The same applies to your API!**

```
GET /api/orders/1/     ← First order ever
GET /api/orders/1000/  ← About 1000 orders exist
GET /api/orders/1001/  ← Probably doesn't exist yet
```

An attacker can:
- Enumerate all your resources
- Estimate your business size
- Scrape your entire database

### Solution 1: UUID Primary Key

```python
import uuid
from django.db import models

class Order(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
```

**Result:** `550e8400-e29b-41d4-a716-446655440000` — impossible to guess!

### Solution 2: Dual ID Approach

Keep integer IDs internally (for JOINs and performance), expose UUIDs externally.

```python
class Order(models.Model):
    # Internal integer ID (auto-generated, used for JOINs)
    id = models.BigAutoField(primary_key=True)

    # External UUID (exposed in API)
    public_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True  # Required for API lookups!
    )
```

**Why is public_id indexed?** The UUID needs an index because your API will query by it. But this doesn't defeat the purpose:
- **Integer PK** is used for JOINs between tables (faster, smaller)
- **UUID index** is only for direct lookups (`WHERE public_id = ...`)
- JOINs are the expensive operations; lookups are fast with any index

**In ViewSet:**
```python
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'public_id'  # Use UUID in URLs!
```

**URLs:** `/api/orders/550e8400-e29b-41d4-a716.../` — secure AND performant!

### Solution 3: Prefixed IDs (HashIDs)

Some companies use prefixed IDs for better developer experience:

```json
{
    "object": "mf_purchase",
    "id": "mfp_177177219f634373b01072986d2eea7d"
}
```

These are **Prefixed IDs** (popularized by Stripe). The prefix tells you the resource type at a glance:
- `ord_abc123...` → Order
- `cus_xyz789...` → Customer
- `mfp_177177...` → MF Purchase

**Implementation:**
```python
# Using hashids library
from hashids import Hashids
hashids = Hashids(salt="your-secret-salt", min_length=8)

# Encode: 42 → "X7K9mQ2p"
encoded = hashids.encode(42)

# Decode: "X7K9mQ2p" → 42
decoded = hashids.decode("X7K9mQ2p")[0]

# Add prefix
public_id = f"ord_{encoded}"  # "ord_X7K9mQ2p"
```

**Trade-offs of Prefixed IDs:**
- ✅ Human-readable, self-documenting
- ✅ Easy to identify resource type in logs
- ✅ Shorter than UUIDs
- ⚠️ Reversible (with salt) — not cryptographically secure
- ⚠️ Requires custom encoding/decoding logic
- ⚠️ Need to maintain prefix consistency

### When to Use What?

| ID Type | Use When |
|---------|----------|
| **Auto Integer** | Internal resources, admin-only |
| **UUID** | Public-facing APIs, security matters |
| **Dual ID** | Need both performance AND security |
| **Prefixed ID** | Developer experience, self-documenting APIs |

---

## Part 3: Queries Review & Q Objects

### Field Lookups Review

Before learning Q objects, let's review Django's field lookups:

```python
# Comparison
MenuItem.objects.filter(price__gte=10)    # price >= 10
MenuItem.objects.filter(price__lte=20)    # price <= 20
MenuItem.objects.filter(price__gt=5)      # price > 5
MenuItem.objects.filter(price__lt=15)     # price < 15

# Range
MenuItem.objects.filter(price__range=(10, 20))  # BETWEEN 10 AND 20

# Text matching
MenuItem.objects.filter(name__icontains='pizza')  # Case-insensitive LIKE
MenuItem.objects.filter(name__startswith='Veg')   # Starts with

# Date/Time
Order.objects.filter(created_at__date=today)      # Date part only
Order.objects.filter(created_at__year=2024)       # Year extraction

# List membership
Order.objects.filter(status__in=['pending', 'confirmed'])
```

### The Problem: Chained Filters are AND

```python
# This is AND - both must be true
MenuItem.objects.filter(price__lte=10).filter(category__name='Desserts')
# SQL: WHERE price <= 10 AND category.name = 'Desserts'
```

**Question:** How do we get items that are EITHER cheap OR desserts?

### Solution: Q Objects

```python
from django.db.models import Q

# OR condition
MenuItem.objects.filter(
    Q(price__lte=10) | Q(category__name='Desserts')
)
# SQL: WHERE price <= 10 OR category.name = 'Desserts'

# AND condition (explicit)
MenuItem.objects.filter(
    Q(price__lte=10) & Q(is_available=True)
)

# NOT condition
Order.objects.filter(
    ~Q(status='cancelled')
)
# SQL: WHERE NOT status = 'cancelled'
```

### Complex Query Examples

```python
# Orders that are (pending OR confirmed) AND created today
from django.utils import timezone
today = timezone.now().date()

Order.objects.filter(
    (Q(status='pending') | Q(status='confirmed')) &
    Q(created_at__date=today)
)

# High-value pending orders NOT from "test" customers
Order.objects.filter(
    Q(status='pending') &
    Q(total_amount__gte=100) &
    ~Q(customer_name__icontains='test')
)
```

### Q Object Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `\|` | OR | `Q(a=1) \| Q(b=2)` |
| `&` | AND | `Q(a=1) & Q(b=2)` |
| `~` | NOT | `~Q(a=1)` |

---

## Part 4: Custom QuerySet Methods

### The Problem: Repeated Query Logic

```python
# In views.py
pending_orders = Order.objects.filter(status='pending')

# In another view
pending_orders = Order.objects.filter(status='pending')

# In a third place
pending_orders = Order.objects.filter(status='pending')
```

If the definition of "pending" changes, you have to update everywhere!

### Solution: Custom QuerySet

```python
# orders/models.py
class OrderQuerySet(models.QuerySet):
    """Custom QuerySet methods for Order."""

    def pending(self):
        return self.filter(status='pending')

    def active(self):
        """Orders that aren't cancelled or delivered."""
        return self.exclude(status__in=['cancelled', 'delivered'])

    def today(self):
        from django.utils import timezone
        return self.filter(created_at__date=timezone.now().date())

    def high_value(self, min_amount=100):
        return self.filter(total_amount__gte=min_amount)

    def needs_attention(self):
        """Pending orders older than 30 minutes."""
        from datetime import timedelta
        from django.utils import timezone
        threshold = timezone.now() - timedelta(minutes=30)
        return self.filter(status='pending', created_at__lte=threshold)


class Order(models.Model):
    # ... fields ...

    # Use custom QuerySet as manager
    objects = OrderQuerySet.as_manager()
```

### Usage

```python
# Clean, readable, DRY code!
Order.objects.pending()
Order.objects.active().today()
Order.objects.pending().high_value(min_amount=500)

# Chain with regular filters
Order.objects.pending().filter(customer_name__icontains='john')
```

---

## Quick Reference

### Filter Lookups

| Lookup | SQL | Example |
|--------|-----|---------|
| `__exact` | `= value` | `status__exact='pending'` |
| `__iexact` | `ILIKE value` | `name__iexact='PIZZA'` |
| `__contains` | `LIKE %value%` | `name__contains='pizza'` |
| `__icontains` | `ILIKE %value%` | `name__icontains='pizza'` |
| `__gt`, `__gte` | `>`, `>=` | `price__gte=10` |
| `__lt`, `__lte` | `<`, `<=` | `price__lte=20` |
| `__in` | `IN (...)` | `status__in=['a', 'b']` |
| `__range` | `BETWEEN` | `price__range=(10, 20)` |
| `__date` | Date part | `created_at__date=today` |

### Files Created Today

| File | Purpose |
|------|---------|
| `core/models.py` | Abstract base models (TimestampedModel, SoftDeleteModel) |
| `menu/models.py` | Multi-table inheritance example (Food, Beverage) |
| `orders/models.py` | Custom QuerySet, Proxy models, UUID/Dual ID |

---

## Coming Next: Pagination, Searching & Sorting

In the next class, we'll add:
- API filtering with django-filter
- Search across multiple fields
- Ordering by different columns
- Pagination for large result sets

---

*Class 7 - Inheritance, IDs & Custom Queries*
