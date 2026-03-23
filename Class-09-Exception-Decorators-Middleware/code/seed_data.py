#!/usr/bin/env python
"""
Seed database with sample data for Class 9 demo.

Usage:
    python seed_data.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_demo.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from menu.models import Category, MenuItem


def seed_data():
    """Create sample categories and menu items."""
    print("Seeding database...")

    # Clear existing data
    MenuItem.objects.all().delete()
    Category.objects.all().delete()

    # Create categories
    appetizers = Category.objects.create(name="Appetizers")
    mains = Category.objects.create(name="Main Courses")
    desserts = Category.objects.create(name="Desserts")
    drinks = Category.objects.create(name="Drinks")

    print(f"Created {Category.objects.count()} categories")

    # Create menu items
    items = [
        # Appetizers
        MenuItem(name="Spring Rolls", price=6.99, category=appetizers,
                 description="Crispy vegetable rolls with dipping sauce"),
        MenuItem(name="Soup of the Day", price=4.99, category=appetizers,
                 description="Ask your server for today's selection"),
        MenuItem(name="Garlic Bread", price=3.99, category=appetizers,
                 description="Toasted with butter and herbs", is_available=False),

        # Main Courses
        MenuItem(name="Grilled Salmon", price=18.99, category=mains,
                 description="Fresh Atlantic salmon with vegetables"),
        MenuItem(name="Chicken Parmesan", price=15.99, category=mains,
                 description="Breaded chicken with marinara sauce"),
        MenuItem(name="Vegetable Stir Fry", price=12.99, category=mains,
                 description="Seasonal vegetables in teriyaki sauce"),

        # Desserts
        MenuItem(name="Chocolate Cake", price=7.99, category=desserts,
                 description="Rich chocolate layer cake"),
        MenuItem(name="Ice Cream", price=4.99, category=desserts,
                 description="Three scoops, choice of flavors"),

        # Drinks
        MenuItem(name="Coffee", price=2.99, category=drinks,
                 description="Fresh brewed"),
        MenuItem(name="Fresh Juice", price=3.99, category=drinks,
                 description="Orange or apple"),
    ]

    MenuItem.objects.bulk_create(items)
    print(f"Created {MenuItem.objects.count()} menu items")

    # Show some stats
    print("\nSample data:")
    for item in MenuItem.objects.all()[:3]:
        status = "Available" if item.is_available else "SOLD OUT"
        print(f"  - {item.name} (${item.price}) - {status}")

    print("\nDone! Try these endpoints:")
    print("  - /menu/item/1/")
    print("  - /menu/item/99999/  (triggers DoesNotExist)")
    print("  - /menu/api/items/")


if __name__ == '__main__':
    seed_data()
