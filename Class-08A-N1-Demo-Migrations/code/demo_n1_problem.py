#!/usr/bin/env python
"""
=============================================================================
N+1 PROBLEM DEMONSTRATION SCRIPT
Class 8: Cardinalities, N+1 Problem & Migrations
=============================================================================

This script demonstrates the N+1 query problem and its solutions using
select_related and prefetch_related.

HOW TO USE THIS SCRIPT:
-----------------------
1. First run: python seed_data.py  (to populate data)
2. Then run: python manage.py shell
3. Copy-paste sections below into the shell to demonstrate

ALTERNATIVE: Run sections in Django shell directly
    python manage.py shell
    >>> exec(open('demo_n1_problem.py').read())

=============================================================================
"""

import os
import django

if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurantproject.settings')
    django.setup()

# Enable query logging to see all SQL queries
import logging
logging.getLogger('django.db.backends').setLevel(logging.DEBUG)

from django.db import connection, reset_queries
from menu.models import Category, MenuItem
from orders.models import Order, OrderItem

# =============================================================================
# HELPER FUNCTION: Count and display queries
# =============================================================================

def show_queries():
    """Display the number of queries and their SQL."""
    queries = connection.queries
    print(f"\n{'='*60}")
    print(f"TOTAL QUERIES: {len(queries)}")
    print('='*60)
    for i, q in enumerate(queries, 1):
        # Truncate long queries for readability
        sql = q['sql'][:100] + '...' if len(q['sql']) > 100 else q['sql']
        print(f"{i}. {sql}")
    print('='*60 + '\n')


def reset():
    """Reset query log for fresh measurement."""
    reset_queries()
    print("\n[Query log reset]\n")


# =============================================================================
# DEMO 1: Simple N+1 Problem (MenuItem -> Category)
# =============================================================================
"""
SCENARIO: Print each menu item with its category name.

PROBLEM: Accessing item.category.name triggers a new query for each item!

RUN THIS IN DJANGO SHELL:
-------------------------
"""

print("\n" + "="*70)
print("DEMO 1: N+1 Problem - MenuItem accessing Category (ForeignKey forward)")
print("="*70)

# --- BAD: N+1 Problem ---
print("\n--- BAD: N+1 Problem ---")
reset()

items = MenuItem.objects.all()[:10]  # Get first 10 items
for item in items:
    # Each item.category.name triggers a NEW query!
    _ = f"{item.name} - {item.category.name}"

show_queries()
# Expected: 1 (get items) + 10 (get category for each) = 11 queries!


# --- GOOD: Using select_related ---
print("\n--- GOOD: Using select_related() ---")
reset()

items = MenuItem.objects.select_related('category')[:10]
for item in items:
    _ = f"{item.name} - {item.category.name}"  # No extra query!

show_queries()
# Expected: 1 query with JOIN!


# =============================================================================
# DEMO 2: Reverse ForeignKey N+1 Problem (Category -> Items)
# =============================================================================
"""
SCENARIO: Print each category with the count of its items.

PROBLEM: Accessing category.items.all() triggers a new query for each category!

RUN THIS IN DJANGO SHELL:
-------------------------
"""

print("\n" + "="*70)
print("DEMO 2: N+1 Problem - Category accessing Items (ForeignKey reverse)")
print("="*70)

# --- BAD: N+1 Problem ---
print("\n--- BAD: N+1 Problem ---")
reset()

categories = Category.objects.all()
for cat in categories:
    # Each cat.items.all() triggers a NEW query!
    items_list = list(cat.items.all())
    _ = f"{cat.name}: {len(items_list)} items"

show_queries()
# Expected: 1 (get categories) + 7 (get items for each) = 8 queries!


# --- GOOD: Using prefetch_related ---
print("\n--- GOOD: Using prefetch_related() ---")
reset()

categories = Category.objects.prefetch_related('items')
for cat in categories:
    items_list = list(cat.items.all())  # Uses prefetched data!
    _ = f"{cat.name}: {len(items_list)} items"

show_queries()
# Expected: 2 queries (categories + items WHERE category_id IN (...))


# =============================================================================
# DEMO 3: Nested N+1 Problem (Order -> OrderItems -> MenuItem)
# =============================================================================
"""
SCENARIO: Print order details with all items and their names.

PROBLEM: Double-nested N+1!
- order.items.all() = 1 query per order
- item.menu_item.name = 1 query per item

RUN THIS IN DJANGO SHELL:
-------------------------
"""

print("\n" + "="*70)
print("DEMO 3: Nested N+1 - Order -> OrderItems -> MenuItem (Through Model)")
print("="*70)

# --- BAD: Double N+1 Problem ---
print("\n--- BAD: Double N+1 Problem ---")
reset()

orders = Order.objects.all()[:5]  # Get 5 orders
for order in orders:
    print(f"\nOrder #{order.id} - {order.customer_name}")
    for item in order.items.all():  # N+1 here!
        print(f"  - {item.quantity}x {item.menu_item.name}")  # Another N+1!

show_queries()
# Expected: 1 + 5 + (many items) = lots of queries!


# --- GOOD: Using prefetch_related with nested path ---
print("\n--- GOOD: Using prefetch_related('items__menu_item') ---")
reset()

orders = Order.objects.prefetch_related('items__menu_item')[:5]
for order in orders:
    print(f"\nOrder #{order.id} - {order.customer_name}")
    for item in order.items.all():  # Uses prefetched data!
        print(f"  - {item.quantity}x {item.menu_item.name}")  # Also prefetched!

show_queries()
# Expected: 3 queries total (orders, items, menu_items)


# =============================================================================
# DEMO 4: Using Custom QuerySet Methods
# =============================================================================
"""
SCENARIO: Use our OrderQuerySet.with_items() method.

BEST PRACTICE: Encapsulate optimizations in QuerySet methods!

RUN THIS IN DJANGO SHELL:
-------------------------
"""

print("\n" + "="*70)
print("DEMO 4: Custom QuerySet - Order.objects.with_items()")
print("="*70)

print("\n--- Using with_items() method ---")
reset()

# with_items() internally calls prefetch_related('items__menu_item')
orders = Order.objects.with_items().pending()
for order in orders:
    print(f"\nOrder #{order.id} - {order.customer_name}")
    for item in order.items.all():
        print(f"  - {item.quantity}x {item.menu_item.name}")

show_queries()


# =============================================================================
# DEMO 5: select_related vs prefetch_related - When to Use Which
# =============================================================================
"""
RULE OF THUMB:
- select_related: ForeignKey/OneToOne FORWARD (uses JOIN)
- prefetch_related: ManyToMany, Reverse FK (uses IN clause + Python)

WHY?
- JOIN is efficient for single related objects
- JOIN creates duplicates for "many" relations (inefficient)
- prefetch_related does separate queries and matches in Python

RUN THIS IN DJANGO SHELL:
-------------------------
"""

print("\n" + "="*70)
print("DEMO 5: select_related vs prefetch_related")
print("="*70)

# --- select_related for ForeignKey forward ---
print("\n--- select_related: MenuItem -> Category (forward FK) ---")
reset()

items = MenuItem.objects.select_related('category').all()[:5]
for item in items:
    _ = item.category.name

show_queries()
print("^ Uses SQL JOIN - single query!")


# --- prefetch_related for reverse FK ---
print("\n--- prefetch_related: Category -> Items (reverse FK) ---")
reset()

categories = Category.objects.prefetch_related('items').all()[:3]
for cat in categories:
    _ = list(cat.items.all())

show_queries()
print("^ Uses IN clause + Python matching - 2 queries!")


# --- Can't use select_related for reverse/many ---
print("\n--- select_related would NOT work for reverse relationships ---")
print("Category.objects.select_related('items')  # WRONG! 'items' is reverse FK")
print("Use prefetch_related for 'many' side relationships")


# =============================================================================
# DEMO 6: Chaining for Complex Queries
# =============================================================================
"""
SCENARIO: Get pending orders from today with all their items and menu items
with categories.

RUN THIS IN DJANGO SHELL:
-------------------------
"""

print("\n" + "="*70)
print("DEMO 6: Chaining Optimizations with Custom QuerySet")
print("="*70)

reset()

# Chain multiple methods!
orders = (Order.objects
          .pending()                          # Filter pending
          .with_items_and_category())         # Prefetch items + menu_item + category

for order in orders:
    print(f"\nOrder #{order.id} - {order.customer_name}")
    for item in order.items.all():
        print(f"  - {item.quantity}x {item.menu_item.name} ({item.menu_item.category.name})")

show_queries()


# =============================================================================
# SUMMARY TABLE
# =============================================================================

print("\n" + "="*70)
print("SUMMARY: Which Optimization to Use")
print("="*70)

summary = """
| Relationship         | Direction          | Use This              |
|---------------------|--------------------|-----------------------|
| ForeignKey          | Forward (item.category) | select_related()    |
| OneToOneField       | Forward (order.invoice) | select_related()    |
| ForeignKey          | Reverse (category.items) | prefetch_related() |
| ManyToManyField     | Either direction        | prefetch_related() |
| OneToOneField       | Reverse               | select_related() works! |

MEMORY TRICK:
- select_related = SQL JOIN = Single objects (FK/O2O forward)
- prefetch_related = Python matching = Plural/many objects
"""

print(summary)

print("\n" + "="*70)
print("END OF DEMO")
print("="*70)
