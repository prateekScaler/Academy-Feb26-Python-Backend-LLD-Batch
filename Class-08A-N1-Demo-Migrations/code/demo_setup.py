#!/usr/bin/env python
"""
N+1 Demo Setup Script

This script sets up the environment for demonstrating the N+1 problem.
Run this before the live demo session.

Usage:
    python manage.py shell < demo_setup.py
    OR
    Just copy-paste the setup code into Django shell
"""

import os
import django

if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurantproject.settings')
    django.setup()

from django.db import connection, reset_queries
from django.conf import settings

# Enable DEBUG for query logging
settings.DEBUG = True

print("""
╔══════════════════════════════════════════════════════════════════╗
║               N+1 PROBLEM LIVE DEMO - SETUP READY                 ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  Query Logging: ENABLED                                           ║
║                                                                   ║
║  Helper Functions Available:                                      ║
║  - reset_queries()     : Clear query log before test              ║
║  - show_queries()      : Show count + sample query                ║
║  - show_all_queries()  : Show all queries (detailed)              ║
║  - connection.queries  : Raw list of all queries                  ║
║                                                                   ║
║  Models Available:                                                ║
║  - MenuItem, Category, Tag (from menu.models)                     ║
║  - Order, OrderItem, OrderInvoice (from orders.models)            ║
║                                                                   ║
╚══════════════════════════════════════════════════════════════════╝
""")

# Define helper functions
def show_queries():
    """Show query count and a sample query."""
    count = len(connection.queries)
    print(f"\n{'='*50}")
    print(f"Total Queries: {count}")
    print(f"{'='*50}")
    if count > 0:
        print(f"Sample: {connection.queries[0]['sql'][:100]}...")
    print()

def show_all_queries():
    """Show all queries (for detailed analysis)."""
    print(f"\n{'='*60}")
    print(f"ALL QUERIES: {len(connection.queries)}")
    print(f"{'='*60}")
    for i, q in enumerate(connection.queries, 1):
        sql = q['sql']
        if len(sql) > 100:
            sql = sql[:100] + '...'
        print(f"{i:3}. [{q['time']}s] {sql}")
    print(f"{'='*60}\n")

# Import models
from menu.models import MenuItem, Category
from orders.models import Order, OrderItem, OrderInvoice

# Check if Tag model exists
try:
    from menu.models import Tag
    HAS_TAGS = True
except ImportError:
    HAS_TAGS = False

print("Models imported successfully!")
print(f"  - Categories: {Category.objects.count()}")
print(f"  - Menu Items: {MenuItem.objects.count()}")
print(f"  - Orders: {Order.objects.count()}")
print(f"  - Order Items: {OrderItem.objects.count()}")
if HAS_TAGS:
    print(f"  - Tags: {Tag.objects.count()}")

print("\n" + "="*60)
print("Ready for N+1 demonstration!")
print("="*60)
print("\nStart with: reset_queries()")
