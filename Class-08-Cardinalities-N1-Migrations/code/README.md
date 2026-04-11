# Class 8: Assignments

## Assignment 1: OrderItem Model (Through Model)

Create a through model for Order-MenuItem relationship that tracks quantity and price at time of order.

**Requirements:**
1. Create `OrderItem` model with:
   - ForeignKey to Order (CASCADE on delete)
   - ForeignKey to MenuItem (PROTECT on delete - don't delete menu items that are in orders!)
   - `quantity` (PositiveIntegerField, default=1)
   - `unit_price` (DecimalField - price at time of order)
   - `subtotal` property that returns quantity * unit_price

2. Add unique constraint: same menu item can't appear twice in same order

3. Update Order model to have:
   ```python
   menu_items = models.ManyToManyField(MenuItem, through='OrderItem')
   ```

**Test in shell:**
```python
>>> order = Order.objects.first()
>>> order.items.create(menu_item=MenuItem.objects.first(), quantity=2, unit_price=Decimal('49.00'))
>>> order.items.all()  # Should show OrderItems
>>> order.menu_items.all()  # Should show MenuItems
```

---

## Assignment 2: Optimize N+1 in ViewSet

Your OrderViewSet is slow. Fix the N+1 problem!

**Before (slow):**
```python
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
```

**Your task:**
1. Add `prefetch_related` to load order items efficiently
2. Add `select_related` for any ForeignKey fields
3. Use nested prefetch with `Prefetch` object if needed

**How to verify:**
Enable query logging and check that listing 10 orders takes 2-3 queries, not 30+:
```python
import logging
logging.getLogger('django.db.backends').setLevel(logging.DEBUG)
```

---

## Assignment 3: Custom QuerySet for Order

Create an OrderQuerySet with these methods:

| Method | Description |
|--------|-------------|
| `with_items()` | Prefetch items and menu_items (solves N+1) |
| `pending()` | Filter status='pending' |
| `preparing()` | Filter status='preparing' |
| `active()` | Exclude cancelled and completed |
| `today()` | Filter created_at to today |
| `this_week()` | Filter created_at to last 7 days |
| `high_value(min_amount)` | Filter total_price >= min_amount |
| `for_customer(email)` | Filter by customer_email (case-insensitive) |
| `needs_attention()` | Pending orders > 30 mins old |

**Usage example:**
```python
# Dashboard queries
Order.objects.pending().today().count()
Order.objects.active().high_value(500).with_items()
Order.objects.needs_attention()  # Alert for slow orders
```

---

## Assignment 4: Custom QuerySet for MenuItem

Create a MenuItemQuerySet with these methods:

| Method | Description |
|--------|-------------|
| `available()` | Filter is_available=True |
| `unavailable()` | Filter is_available=False |
| `by_category(category_name)` | Filter by category name |
| `vegetarian()` | Only vegetarian items (if using Food model) |
| `expensive(min_price)` | Filter price >= min_price |
| `cheap(max_price)` | Filter price <= max_price |
| `search(query)` | Search in name and description |
| `with_category()` | select_related for category |

**Usage example:**
```python
MenuItem.objects.available().by_category('Starters')
MenuItem.objects.vegetarian().cheap(100)
MenuItem.objects.search('chicken').with_category()
```

---

## Assignment 5: Data Migration

Write a data migration to populate `total_price` on existing Orders based on their OrderItems.

**Steps:**
1. Create empty migration: `python manage.py makemigrations orders --empty -n calculate_totals`
2. Write forward function to calculate total from items
3. Write reverse function to set back to NULL
4. Test both directions work

**Important:**
- Use `apps.get_model()` not direct imports
- Handle orders with no items (total = 0)
- Always provide reverse function

---

## Assignment 6: OrderInvoice Model (OneToOne)

Create an invoice system for orders.

**Requirements:**
1. Create `OrderInvoice` model with:
   - OneToOneField to Order
   - `invoice_number` (CharField, unique, auto-generated)
   - `generated_at` (DateTimeField, auto_now_add)
   - `pdf_url` (URLField, blank=True)
   - `notes` (TextField, blank=True)

2. Add a method to Order: `generate_invoice()` that creates an invoice if one doesn't exist

3. Invoice number format: `INV-{year}-{order_id:06d}` (e.g., INV-2024-000042)

**Test in shell:**
```python
>>> order = Order.objects.first()
>>> order.generate_invoice()
>>> order.invoice.invoice_number
'INV-2024-000001'
```

---

## Bonus: Query Optimization Challenge

Given this serializer:

```python
class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer_order_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'customer_name', 'status', 'items', 'customer_order_count']

    def get_customer_order_count(self, obj):
        return Order.objects.filter(customer_email=obj.customer_email).count()
```

**Problem:** This has N+1 issues! For 100 orders:
- 1 query for orders
- 100 queries for items
- 100 queries for customer_order_count

**Your task:** Optimize to use only 2-3 queries total.

**Hints:**
- Use `prefetch_related` for items
- Use `annotate` with `Count` and `Subquery` for customer_order_count
- Or use `Prefetch` with custom queryset

---

## Grading Criteria

| Assignment | Points |
|------------|--------|
| 1. OrderItem Model | 15 |
| 2. ViewSet Optimization | 15 |
| 3. Order QuerySet | 20 |
| 4. MenuItem QuerySet | 15 |
| 5. Data Migration | 15 |
| 6. OrderInvoice | 15 |
| Bonus: Query Challenge | +10 |

**Total: 95 points (+10 bonus)**
