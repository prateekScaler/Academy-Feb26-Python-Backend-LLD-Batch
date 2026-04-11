# Class 8A: N+1 Problem Live Demo & Migrations

## Topics Covered

### 1. Q Objects Review (from Class 7)
- OR conditions: `Q(a=1) | Q(b=2)`
- NOT conditions: `~Q(status='cancelled')`
- Complex combinations: `(Q(a=1) | Q(b=2)) & Q(c=3)`

### 2. N+1 Problem
- What is N+1 and why it kills performance
- Detecting N+1 with `connection.queries`
- Query count analysis (1 + N pattern)

### 3. select_related
- SQL JOIN for ForeignKey and OneToOne
- Forward direction only (item → category)
- One query instead of N+1

### 4. prefetch_related
- Separate queries + Python matching
- For Reverse FK (category → items)
- For ManyToMany (item ↔ tags)
- Chain lookups: `prefetch_related('items__menu_item__category')`

### 5. Why select_related Fails for Reverse FK
- JOIN creates duplicate parent rows
- Django's "one row = one object" design
- The "one" side can tag along, the "many" side cannot

### 6. Migrations
- `makemigrations` - Create migration from model changes
- `migrate` - Apply migrations
- `sqlmigrate` - Preview SQL without running
- `showmigrations` - Check migration status
- `--fake` - Mark as applied without running SQL
- Data migrations with `makemigrations --empty`

## Quick Reference

| Relationship | Direction | Use |
|-------------|-----------|-----|
| ForeignKey | Forward (item.category) | `select_related` |
| ForeignKey | Reverse (category.items) | `prefetch_related` |
| OneToOne | Either direction | `select_related` |
| ManyToMany | Either direction | `prefetch_related` |

## Demo Setup

```bash
cd Class-08A-N1-Demo-Migrations/code
python3 -m venv venv
source venv/bin/activate
pip install django djangorestframework
python manage.py migrate
python seed_data.py
python manage.py shell
```

## Key Commands for Demo

```python
from django.db import connection, reset_queries
from django.conf import settings
settings.DEBUG = True

def show_queries():
    count = len(connection.queries)
    print(f"Total Queries: {count}")
    if count > 0:
        print(f"Sample: {connection.queries[0]['sql'][:100]}...")

from menu.models import MenuItem, Category, Tag
from orders.models import Order, OrderItem

# Reset before each test
reset_queries()
```

## Files

- `index.html` - Interactive slides with quizzes
- `code/` - Demo Django project with models and seed data
