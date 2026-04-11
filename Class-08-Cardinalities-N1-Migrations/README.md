# Class 8: Cardinalities, N+1 Problem & Migrations

> Quick revision guide for Django database relationships, performance optimization, and schema evolution.

---

## Mind Map: Class Overview

```
                    ┌─────────────────────────────────────┐
                    │     CLASS 8: DATABASE MASTERY       │
                    └─────────────────────────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        ▼                            ▼                            ▼
┌───────────────┐          ┌─────────────────┐          ┌─────────────────┐
│ RELATIONSHIPS │          │   N+1 PROBLEM   │          │   MIGRATIONS    │
│ (Cardinality) │          │ (Performance)   │          │ (Schema Evolve) │
└───────┬───────┘          └────────┬────────┘          └────────┬────────┘
        │                           │                            │
   ┌────┼────┐              ┌───────┼───────┐            ┌───────┼───────┐
   │    │    │              │               │            │               │
   ▼    ▼    ▼              ▼               ▼            ▼               ▼
  1:1  1:N  M:N      select_related  prefetch_related  makemigrations  migrate
```

---

## 1. Database Relationships (Cardinalities)

### Quick Reference Table

| Relationship | Django Field | Where to Define | Example |
|-------------|--------------|-----------------|---------|
| **One-to-One** | `OneToOneField` | Dependent/child model | `OrderInvoice` → `Order` |
| **One-to-Many** | `ForeignKey` | **MANY side!** | `MenuItem` → `Category` |
| **Many-to-Many** | `ManyToManyField` | Either model | `MenuItem` ↔ `Tag` |
| **M2M + extra fields** | `ManyToManyField` + `through` | Explicit through model | `Order` ↔ `MenuItem` via `OrderItem` |

### Golden Rules

```
┌─────────────────────────────────────────────────────────────────┐
│  RULE 1: ForeignKey ALWAYS goes on the "MANY" side             │
│  RULE 2: OneToOneField goes in the "dependent" model           │
│  RULE 3: Use through model when you need extra relationship data│
└─────────────────────────────────────────────────────────────────┘
```

### Code Patterns

#### One-to-One (1:1)
```python
class OrderInvoice(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='invoice'  # order.invoice
    )
```

#### One-to-Many (1:N) - ForeignKey
```python
class MenuItem(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='items'  # category.items.all()
    )
```

#### Many-to-Many with Through Model
```python
class Order(models.Model):
    menu_items = models.ManyToManyField(
        'menu.MenuItem',
        through='OrderItem',
        related_name='orders'
    )

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey('menu.MenuItem', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
```

### on_delete Options

| Option | Behavior |
|--------|----------|
| `CASCADE` | Delete children when parent deleted |
| `PROTECT` | Prevent deletion if children exist |
| `SET_NULL` | Set FK to NULL (requires `null=True`) |
| `SET_DEFAULT` | Set FK to default value |

---

## 2. The N+1 Problem

### What is N+1?

```
❌ BAD: Accessing related objects in a loop
──────────────────────────────────────────
items = MenuItem.objects.all()        # Query 1
for item in items:
    print(item.category.name)         # Query 2, 3, 4... per item!

With 100 items = 101 queries! (1 + N)
```

### Detection Methods

| Method | How |
|--------|-----|
| Django Debug Toolbar | Shows SQL panel with query count |
| Query Logging | Enable in `settings.py` LOGGING config |
| Pattern Recognition | Many similar queries with different IDs |

---

## 3. Solving N+1: select_related vs prefetch_related

### Decision Matrix

```
┌─────────────────────────────────────────────────────────────────┐
│                    WHICH METHOD TO USE?                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  select_related()          │  prefetch_related()               │
│  ─────────────────         │  ──────────────────               │
│  • SQL JOIN                │  • Separate queries + Python      │
│  • Single query            │  • 2+ queries                     │
│  • For: FK, O2O (forward)  │  • For: M2M, Reverse FK           │
│                                                                 │
│  Memory trick:                                                  │
│  S-elect = S-QL = S-ingle objects                              │
│  P-refetch = P-ython = P-lural objects                         │
└─────────────────────────────────────────────────────────────────┘
```

### Quick Reference

| Relationship | Direction | Use |
|-------------|-----------|-----|
| ForeignKey | Forward (`item.category`) | `select_related` |
| ForeignKey | Reverse (`category.items`) | `prefetch_related` |
| OneToOne | Either direction | `select_related` |
| ManyToMany | Either direction | `prefetch_related` |

### Code Examples

```python
# select_related - SQL JOIN (for FK/O2O forward)
items = MenuItem.objects.select_related('category')
for item in items:
    print(item.category.name)  # No extra query!

# prefetch_related - Separate queries (for reverse/M2M)
categories = Category.objects.prefetch_related('items')
for cat in categories:
    print(cat.items.all())  # Uses prefetched data!
```

---

## 4. Custom QuerySets

### Why Use Them?
- DRY: Define query logic once
- Built-in optimizations
- Chainable methods
- Self-documenting code

### Pattern

```python
class OrderQuerySet(models.QuerySet):
    def with_items(self):
        """Solve N+1 for items"""
        return self.prefetch_related('items__menu_item')

    def pending(self):
        return self.filter(status='pending')

    def active(self):
        return self.exclude(status__in=['cancelled', 'completed'])

class Order(models.Model):
    objects = OrderQuerySet.as_manager()

# Usage - clean and chainable:
Order.objects.pending().with_items()
Order.objects.active().today()
```

### Q Objects for Complex Queries

```python
from django.db.models import Q

# OR condition
Order.objects.filter(Q(status='pending') | Q(status='confirmed'))

# NOT condition
Order.objects.filter(~Q(status='cancelled'))

# Complex: (A OR B) AND C AND NOT D
Order.objects.filter(
    (Q(status='pending') | Q(status='confirmed')) &
    Q(total_price__gte=1000) &
    ~Q(customer_name__icontains='test')
)
```

---

## 5. Migrations

### Workflow

```
models.py → makemigrations → 0002_xxx.py → migrate → Database
   ↓              ↓               ↓            ↓
 Change      Generate file    Migration    Apply to DB
 models                         file
```

### Essential Commands

| Command | Purpose |
|---------|---------|
| `showmigrations` | See migration status |
| `makemigrations` | Generate migration files |
| `sqlmigrate orders 0002` | Preview SQL |
| `migrate` | Apply migrations |
| `migrate orders 0001` | Rollback to specific |
| `migrate orders zero` | Rollback all |

### Fake Migrations

```bash
# Mark as applied WITHOUT running (DB already has changes)
python manage.py migrate orders 0003 --fake

# Mark ALL as applied
python manage.py migrate --fake
```

> **Warning:** Only use `--fake` when DB schema already matches!

### Data Migrations

```python
# Create empty migration
# python manage.py makemigrations orders --empty -n populate_totals

from django.db import migrations

def calculate_totals(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')  # Use apps.get_model!
    for order in Order.objects.filter(total_price__isnull=True):
        order.total_price = sum(i.quantity * i.unit_price for i in order.items.all())
        order.save()

def reverse_totals(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    Order.objects.update(total_price=None)

class Migration(migrations.Migration):
    dependencies = [('orders', '0002_orderitem')]
    operations = [
        migrations.RunPython(calculate_totals, reverse_totals),
    ]
```

### Best Practices

```
✅ DO:
  • Commit migrations to version control
  • Review generated migrations before applying
  • Test on staging first
  • Always provide reverse function for RunPython
  • Use apps.get_model() in data migrations

❌ DON'T:
  • Edit migrations after production deployment
  • Delete deployed migrations
  • Use --fake without understanding consequences

⚠️ CAREFUL:
  • Adding NOT NULL field → add default or null=True first
  • Removing fields → data loss!
  • Renaming fields → Django might create + delete instead
```

---

## Quick Recall Cheat Sheet

```
┌─────────────────────────────────────────────────────────────────┐
│                    MENTAL MODEL SUMMARY                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Relationship type?    → OneToOne / ForeignKey / ManyToMany   │
│   Where does FK go?     → On the MANY side!                    │
│                                                                 │
│   Accessing related     → Watch out for N+1!                   │
│   objects in a loop?                                           │
│                                                                 │
│   Forward FK/O2O?       → select_related (SQL JOIN)            │
│   Reverse FK/M2M?       → prefetch_related (Python)            │
│                                                                 │
│   Schema change?        → makemigrations → migrate             │
│   DB already changed?   → migrate --fake                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Common Field Lookups Reference

| Lookup | SQL | Example |
|--------|-----|---------|
| `__gte` | `>=` | `price__gte=100` |
| `__lte` | `<=` | `price__lte=500` |
| `__range` | `BETWEEN` | `price__range=(100,500)` |
| `__in` | `IN (...)` | `status__in=['a','b']` |
| `__icontains` | `ILIKE %x%` | `name__icontains='paneer'` |
| `__isnull` | `IS NULL` | `total__isnull=True` |

---

**Next Class:** Exception Handling & Middlewares
