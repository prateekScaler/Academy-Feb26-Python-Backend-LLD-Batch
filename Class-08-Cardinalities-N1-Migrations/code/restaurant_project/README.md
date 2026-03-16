# Restaurant Project - Class 8 Demo

This is the practice project for Class 8: Cardinalities, N+1 Problem & Migrations.

## Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install django djangorestframework

# Run migrations
python manage.py migrate

# Seed sample data
python seed_data.py

# Run the N+1 demo
python demo_n1_problem.py

# Start the development server
python manage.py runserver
```

## Key Concepts Demonstrated

### 1. Cardinalities (Relationships)

| Relationship | Django Field | Example |
|-------------|--------------|---------|
| One-to-One | `OneToOneField` | Order ↔ Invoice |
| One-to-Many | `ForeignKey` | Category → MenuItems |
| Many-to-Many (Simple) | `ManyToManyField` | MenuItem ↔ Tag |
| Many-to-Many (Through) | `ManyToManyField` + `through` | Order ↔ MenuItem via OrderItem |

### 2. N+1 Problem

See `demo_n1_problem.py` for live demonstration:
- **Problem**: Accessing related objects in a loop causes N+1 queries
- **Solution**: Use `select_related()` for FK/O2O, `prefetch_related()` for M2M/reverse

### 3. Custom QuerySets

See `orders/models.py` for `OrderQuerySet`:
- Chainable methods: `Order.objects.pending().today().with_items()`
- Built-in optimizations: `with_items()` solves N+1

### 4. Proxy Models

See `orders/models.py` for `RecentOrder` and `ArchivedOrder`:
- Same table, different default QuerySet
- Useful for Django Admin separate sections

## Project Structure

```
restaurant_project/
├── core/                 # Abstract base models
│   └── models.py        # TimestampedModel
├── menu/                 # Menu app
│   ├── models.py        # Category, MenuItem, Tag, Food, Beverage
│   └── migrations/
├── orders/               # Orders app
│   ├── models.py        # Order, OrderItem, OrderInvoice, Proxy models
│   └── migrations/
├── demo_n1_problem.py   # Interactive N+1 demonstration
└── seed_data.py         # Sample data generator
```
