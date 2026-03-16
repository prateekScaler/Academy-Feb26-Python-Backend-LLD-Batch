#!/usr/bin/env python
"""
Seed script for Class 8: Cardinalities, N+1 Problem & Migrations Demo

Usage:
    python manage.py shell < seed_data.py
    OR
    python seed_data.py  (if DJANGO_SETTINGS_MODULE is not set, it will be configured)

This script:
1. Creates Categories, MenuItems (Food & Beverage with multi-table inheritance)
2. Creates Orders with OrderItems (through model demo)
3. Creates sample OrderInvoices (OneToOne demo)

After running, use demo_n1_problem.py to demonstrate N+1 issues and solutions!
"""

import os
import django
import random

if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurantproject.settings')
    django.setup()

from decimal import Decimal
from menu.models import Category, MenuItem
from orders.models import Order, OrderItem, OrderInvoice

# Check if Tag model exists (after Class 8 additions)
try:
    from menu.models import Tag
    HAS_TAGS = True
    print("✓ Tag model found (simple ManyToMany)")
except ImportError:
    HAS_TAGS = False
    print("○ Tag model not found yet")

# Check if Food and Beverage models exist (after multi-table inheritance)
try:
    from menu.models import Food, Beverage
    HAS_INHERITANCE = True
    print("✓ Food and Beverage models found (multi-table inheritance)")
except ImportError:
    HAS_INHERITANCE = False
    print("○ Using simple MenuItem model (no inheritance yet)")

# =============================================================================
# CLEAR EXISTING DATA
# =============================================================================
print("\nClearing existing data...")
OrderInvoice.objects.all().delete()
OrderItem.objects.all().delete()
Order.objects.all().delete()
if HAS_INHERITANCE:
    Food.objects.all().delete()
    Beverage.objects.all().delete()
MenuItem.objects.all().delete()
Category.objects.all().delete()
if HAS_TAGS:
    Tag.objects.all().delete()

# =============================================================================
# TAGS - Simple ManyToMany Demo (Class 8)
# =============================================================================
tags = {}
if HAS_TAGS:
    print("Creating tags...")
    tags['spicy'] = Tag.objects.create(name="Spicy", color="#ef4444")
    tags['vegan'] = Tag.objects.create(name="Vegan", color="#22c55e")
    tags['vegetarian'] = Tag.objects.create(name="Vegetarian", color="#84cc16")
    tags['gluten_free'] = Tag.objects.create(name="Gluten-Free", color="#f59e0b")
    tags['chef_special'] = Tag.objects.create(name="Chef's Special", color="#8b5cf6")
    tags['bestseller'] = Tag.objects.create(name="Bestseller", color="#ec4899")
    tags['healthy'] = Tag.objects.create(name="Healthy", color="#14b8a6")
    print(f"  ✓ Tags created: {Tag.objects.count()}")

# =============================================================================
# CATEGORIES - Indian Restaurant
# =============================================================================
print("Creating categories...")

starters = Category.objects.create(
    name="Starters",
    description="Crispy snacks and appetizers to begin your meal"
)
tandoor = Category.objects.create(
    name="Tandoor",
    description="Clay oven specialties - kebabs and tikkas"
)
curries = Category.objects.create(
    name="Main Course",
    description="Rich gravies and curries"
)
breads = Category.objects.create(
    name="Breads",
    description="Fresh from the tandoor - naan, roti, paratha"
)
rice = Category.objects.create(
    name="Rice & Biryani",
    description="Fragrant rice dishes and dum biryanis"
)
desserts = Category.objects.create(
    name="Desserts",
    description="Traditional Indian sweets and desserts"
)
beverages_cat = Category.objects.create(
    name="Beverages",
    description="Refreshing drinks - lassi, chaas, chai"
)

print(f"  ✓ Categories created: {Category.objects.count()}")

# =============================================================================
# MENU ITEMS - Indian Food & Beverages
# =============================================================================
print("Creating menu items...")

# Dictionary to store created items for easy reference when creating orders
menu_items = {}

if HAS_INHERITANCE:
    # -------------------------------------------------------------------------
    # FOOD ITEMS (using Food model with multi-table inheritance)
    # -------------------------------------------------------------------------

    # Starters
    menu_items['samosa'] = Food.objects.create(
        name="Samosa", price=Decimal("49.00"), category=starters,
        description="Crispy pastry filled with spiced potatoes and peas",
        is_vegetarian=True, calories=262
    )
    menu_items['paneer_tikka'] = Food.objects.create(
        name="Paneer Tikka", price=Decimal("199.00"), category=starters,
        description="Marinated cottage cheese grilled in tandoor",
        is_vegetarian=True, calories=320
    )
    menu_items['chicken_65'] = Food.objects.create(
        name="Chicken 65", price=Decimal("249.00"), category=starters,
        description="Spicy deep-fried chicken from Hyderabad",
        is_vegetarian=False, calories=450
    )
    menu_items['onion_bhaji'] = Food.objects.create(
        name="Onion Bhaji", price=Decimal("79.00"), category=starters,
        description="Crispy onion fritters with mint chutney",
        is_vegetarian=True, calories=180
    )
    menu_items['aloo_tikki'] = Food.objects.create(
        name="Aloo Tikki", price=Decimal("69.00"), category=starters,
        description="Spiced potato patties with chutneys",
        is_vegetarian=True, calories=220
    )

    # Tandoor
    menu_items['chicken_tikka'] = Food.objects.create(
        name="Chicken Tikka", price=Decimal("299.00"), category=tandoor,
        description="Boneless chicken marinated in spices and yogurt",
        is_vegetarian=False, calories=280
    )
    menu_items['seekh_kebab'] = Food.objects.create(
        name="Seekh Kebab", price=Decimal("279.00"), category=tandoor,
        description="Minced lamb kebabs with aromatic spices",
        is_vegetarian=False, calories=350
    )
    menu_items['tandoori_chicken'] = Food.objects.create(
        name="Tandoori Chicken", price=Decimal("349.00"), category=tandoor,
        description="Half chicken marinated overnight in yogurt and spices",
        is_vegetarian=False, calories=420
    )
    menu_items['paneer_tikka_masala'] = Food.objects.create(
        name="Paneer Tikka Masala", price=Decimal("249.00"), category=tandoor,
        description="Grilled paneer cubes with bell peppers",
        is_vegetarian=True, calories=380
    )

    # Main Course / Curries
    menu_items['butter_chicken'] = Food.objects.create(
        name="Butter Chicken", price=Decimal("329.00"), category=curries,
        description="Tandoori chicken in rich tomato and butter gravy",
        is_vegetarian=False, calories=490
    )
    menu_items['dal_makhani'] = Food.objects.create(
        name="Dal Makhani", price=Decimal("229.00"), category=curries,
        description="Black lentils slow-cooked with cream and butter",
        is_vegetarian=True, calories=320
    )
    menu_items['paneer_butter_masala'] = Food.objects.create(
        name="Paneer Butter Masala", price=Decimal("269.00"), category=curries,
        description="Cottage cheese in creamy tomato gravy",
        is_vegetarian=True, calories=410
    )
    menu_items['chole_bhature'] = Food.objects.create(
        name="Chole Bhature", price=Decimal("179.00"), category=curries,
        description="Spiced chickpeas with fluffy fried bread",
        is_vegetarian=True, calories=520
    )
    menu_items['palak_paneer'] = Food.objects.create(
        name="Palak Paneer", price=Decimal("249.00"), category=curries,
        description="Cottage cheese in spinach gravy",
        is_vegetarian=True, calories=340
    )
    menu_items['chicken_korma'] = Food.objects.create(
        name="Chicken Korma", price=Decimal("319.00"), category=curries,
        description="Chicken in creamy cashew and yogurt sauce",
        is_vegetarian=False, calories=480
    )

    # Rice & Biryani
    menu_items['chicken_biryani'] = Food.objects.create(
        name="Chicken Biryani", price=Decimal("349.00"), category=rice,
        description="Hyderabadi dum biryani with tender chicken",
        is_vegetarian=False, calories=550
    )
    menu_items['veg_biryani'] = Food.objects.create(
        name="Veg Biryani", price=Decimal("249.00"), category=rice,
        description="Fragrant rice with mixed vegetables and saffron",
        is_vegetarian=True, calories=420
    )
    menu_items['jeera_rice'] = Food.objects.create(
        name="Jeera Rice", price=Decimal("129.00"), category=rice,
        description="Basmati rice tempered with cumin seeds",
        is_vegetarian=True, calories=280
    )

    # Breads
    menu_items['butter_naan'] = Food.objects.create(
        name="Butter Naan", price=Decimal("49.00"), category=breads,
        description="Soft leavened bread brushed with butter",
        is_vegetarian=True, calories=220
    )
    menu_items['garlic_naan'] = Food.objects.create(
        name="Garlic Naan", price=Decimal("59.00"), category=breads,
        description="Naan topped with garlic and coriander",
        is_vegetarian=True, calories=240
    )
    menu_items['laccha_paratha'] = Food.objects.create(
        name="Laccha Paratha", price=Decimal("49.00"), category=breads,
        description="Layered whole wheat flatbread",
        is_vegetarian=True, calories=200
    )
    menu_items['tandoori_roti'] = Food.objects.create(
        name="Tandoori Roti", price=Decimal("29.00"), category=breads,
        description="Whole wheat bread from the clay oven",
        is_vegetarian=True, calories=120
    )

    # Desserts
    menu_items['gulab_jamun'] = Food.objects.create(
        name="Gulab Jamun", price=Decimal("99.00"), category=desserts,
        description="Deep-fried milk dumplings in sugar syrup",
        is_vegetarian=True, calories=380
    )
    menu_items['rasmalai'] = Food.objects.create(
        name="Rasmalai", price=Decimal("129.00"), category=desserts,
        description="Soft paneer patties in saffron milk",
        is_vegetarian=True, calories=290
    )
    menu_items['kulfi'] = Food.objects.create(
        name="Kulfi", price=Decimal("89.00"), category=desserts,
        description="Traditional Indian ice cream with pistachios",
        is_vegetarian=True, calories=250
    )
    menu_items['gajar_halwa'] = Food.objects.create(
        name="Gajar Ka Halwa", price=Decimal("119.00"), category=desserts,
        description="Warm carrot pudding with nuts",
        is_vegetarian=True, calories=350
    )

    # -------------------------------------------------------------------------
    # BEVERAGES (using Beverage model with multi-table inheritance)
    # -------------------------------------------------------------------------
    menu_items['mango_lassi'] = Beverage.objects.create(
        name="Mango Lassi", price=Decimal("99.00"), category=beverages_cat,
        description="Sweet yogurt drink with mango pulp",
        is_alcoholic=False, volume_ml=350
    )
    menu_items['sweet_lassi'] = Beverage.objects.create(
        name="Sweet Lassi", price=Decimal("79.00"), category=beverages_cat,
        description="Traditional sweet yogurt drink",
        is_alcoholic=False, volume_ml=350
    )
    menu_items['salted_lassi'] = Beverage.objects.create(
        name="Salted Lassi", price=Decimal("69.00"), category=beverages_cat,
        description="Savory yogurt drink with cumin",
        is_alcoholic=False, volume_ml=350
    )
    menu_items['masala_chaas'] = Beverage.objects.create(
        name="Masala Chaas", price=Decimal("49.00"), category=beverages_cat,
        description="Spiced buttermilk with mint and cumin",
        is_alcoholic=False, volume_ml=350
    )
    menu_items['masala_chai'] = Beverage.objects.create(
        name="Masala Chai", price=Decimal("39.00"), category=beverages_cat,
        description="Indian spiced tea with ginger and cardamom",
        is_alcoholic=False, volume_ml=150
    )
    menu_items['filter_coffee'] = Beverage.objects.create(
        name="Filter Coffee", price=Decimal("49.00"), category=beverages_cat,
        description="South Indian style filter coffee",
        is_alcoholic=False, volume_ml=150
    )
    menu_items['jaljeera'] = Beverage.objects.create(
        name="Jaljeera", price=Decimal("59.00"), category=beverages_cat,
        description="Tangy cumin-mint cooler",
        is_alcoholic=False, volume_ml=300
    )
    menu_items['aam_panna'] = Beverage.objects.create(
        name="Aam Panna", price=Decimal("69.00"), category=beverages_cat,
        description="Raw mango cooler with mint",
        is_alcoholic=False, volume_ml=300
    )
    menu_items['nimbu_pani'] = Beverage.objects.create(
        name="Nimbu Pani", price=Decimal("39.00"), category=beverages_cat,
        description="Fresh lime water with salt or sugar",
        is_alcoholic=False, volume_ml=300
    )
    menu_items['thandai'] = Beverage.objects.create(
        name="Thandai", price=Decimal("99.00"), category=beverages_cat,
        description="Festive drink with almonds, fennel, and rose",
        is_alcoholic=False, volume_ml=300
    )

    print(f"  ✓ Food items: {Food.objects.count()}")
    print(f"  ✓ Beverages: {Beverage.objects.count()}")

else:
    # -------------------------------------------------------------------------
    # SIMPLE MENU ITEMS (before multi-table inheritance migration)
    # -------------------------------------------------------------------------
    menu_items['samosa'] = MenuItem.objects.create(
        name="Samosa", price=Decimal("49.00"), category=starters,
        description="Crispy pastry with spiced potatoes"
    )
    menu_items['paneer_tikka'] = MenuItem.objects.create(
        name="Paneer Tikka", price=Decimal("199.00"), category=starters,
        description="Grilled cottage cheese"
    )
    menu_items['chicken_65'] = MenuItem.objects.create(
        name="Chicken 65", price=Decimal("249.00"), category=starters,
        description="Spicy fried chicken"
    )
    menu_items['butter_chicken'] = MenuItem.objects.create(
        name="Butter Chicken", price=Decimal("329.00"), category=curries,
        description="Chicken in tomato butter gravy"
    )
    menu_items['dal_makhani'] = MenuItem.objects.create(
        name="Dal Makhani", price=Decimal("229.00"), category=curries,
        description="Creamy black lentils"
    )
    menu_items['paneer_butter_masala'] = MenuItem.objects.create(
        name="Paneer Butter Masala", price=Decimal("269.00"), category=curries,
        description="Paneer in creamy gravy"
    )
    menu_items['chicken_biryani'] = MenuItem.objects.create(
        name="Chicken Biryani", price=Decimal("349.00"), category=rice,
        description="Hyderabadi dum biryani"
    )
    menu_items['veg_biryani'] = MenuItem.objects.create(
        name="Veg Biryani", price=Decimal("249.00"), category=rice,
        description="Vegetable biryani"
    )
    menu_items['butter_naan'] = MenuItem.objects.create(
        name="Butter Naan", price=Decimal("49.00"), category=breads,
        description="Soft buttered naan"
    )
    menu_items['garlic_naan'] = MenuItem.objects.create(
        name="Garlic Naan", price=Decimal("59.00"), category=breads,
        description="Naan with garlic"
    )
    menu_items['tandoori_roti'] = MenuItem.objects.create(
        name="Tandoori Roti", price=Decimal("29.00"), category=breads,
        description="Whole wheat roti"
    )
    menu_items['gulab_jamun'] = MenuItem.objects.create(
        name="Gulab Jamun", price=Decimal("99.00"), category=desserts,
        description="Sweet milk dumplings"
    )
    menu_items['mango_lassi'] = MenuItem.objects.create(
        name="Mango Lassi", price=Decimal("99.00"), category=beverages_cat,
        description="Sweet mango yogurt drink"
    )
    menu_items['masala_chai'] = MenuItem.objects.create(
        name="Masala Chai", price=Decimal("39.00"), category=beverages_cat,
        description="Indian spiced tea"
    )

    print(f"  ✓ Menu items: {MenuItem.objects.count()}")


# =============================================================================
# ASSIGN TAGS TO MENU ITEMS (Simple ManyToMany Demo)
# =============================================================================
if HAS_TAGS and menu_items:
    print("\nAssigning tags to menu items...")

    # Spicy items
    spicy_items = ['chicken_tikka', 'seekh_kebab', 'chicken_biryani', 'veg_biryani']
    for key in spicy_items:
        if key in menu_items:
            menu_items[key].tags.add(tags['spicy'])

    # Vegetarian items
    veg_items = ['paneer_tikka', 'dal_makhani', 'palak_paneer', 'paneer_butter_masala',
                 'butter_naan', 'garlic_naan', 'tandoori_roti', 'veg_biryani',
                 'gulab_jamun', 'ras_malai', 'mango_lassi', 'sweet_lassi', 'masala_chai']
    for key in veg_items:
        if key in menu_items:
            menu_items[key].tags.add(tags['vegetarian'])

    # Vegan items (subset of vegetarian)
    vegan_items = ['dal_makhani', 'tandoori_roti']
    for key in vegan_items:
        if key in menu_items:
            menu_items[key].tags.add(tags['vegan'])

    # Chef's Special
    chef_special = ['butter_chicken', 'chicken_biryani', 'dal_makhani', 'paneer_tikka']
    for key in chef_special:
        if key in menu_items:
            menu_items[key].tags.add(tags['chef_special'])

    # Bestsellers
    bestsellers = ['butter_chicken', 'butter_naan', 'mango_lassi', 'chicken_biryani']
    for key in bestsellers:
        if key in menu_items:
            menu_items[key].tags.add(tags['bestseller'])

    # Healthy options
    healthy = ['dal_makhani', 'palak_paneer', 'tandoori_roti', 'masala_chai']
    for key in healthy:
        if key in menu_items:
            menu_items[key].tags.add(tags['healthy'])

    print(f"  ✓ Tags assigned to menu items")


# =============================================================================
# ORDERS WITH ORDER ITEMS (Through Model Demo)
# =============================================================================
print("\nCreating orders with items...")


def create_order_with_items(customer_name, email, status, items_data, notes=""):
    """
    Helper to create an order with its items.

    items_data: list of tuples (item_key, quantity)
    Example: [('butter_chicken', 2), ('butter_naan', 4), ('mango_lassi', 2)]
    """
    # Calculate total from items
    total = Decimal("0.00")
    for item_key, qty in items_data:
        if item_key in menu_items:
            total += menu_items[item_key].price * qty

    # Create order
    order = Order.objects.create(
        customer_name=customer_name,
        customer_email=email,
        status=status,
        total_price=total,
        notes=notes
    )

    # Create order items
    for item_key, qty in items_data:
        if item_key in menu_items:
            item = menu_items[item_key]
            OrderItem.objects.create(
                order=order,
                menu_item=item,
                quantity=qty,
                unit_price=item.price
            )

    return order


# Create orders with different scenarios for N+1 demo

# Order 1: Simple order - 2 items
order1 = create_order_with_items(
    "Arnab Kumar Tripathy", "arnabtripathy96@gmail.com", "completed",
    [('butter_chicken', 1), ('butter_naan', 2), ('mango_lassi', 1)],
    "Extra spicy please"
)

# Order 2: Medium order - 4 items
order2 = create_order_with_items(
    "Jayendra Khole", "kholejyndr@gmail.com", "completed",
    [('chicken_biryani', 2), ('masala_chai', 2)],
    "Office lunch"
)

# Order 3: Large order - 5+ items (good for N+1 demo)
order3 = create_order_with_items(
    "Vipul Mahajan", "vipulma7@gmail.com", "preparing",
    [
        ('paneer_tikka', 2),
        ('dal_makhani', 1),
        ('paneer_butter_masala', 1),
        ('butter_naan', 4),
        ('garlic_naan', 2),
        ('gulab_jamun', 2)
    ],
    "Family dinner - vegetarian"
)

# Order 4: Pending order
order4 = create_order_with_items(
    "Kaarthik Ananth B", "kaarthikananthb@gmail.com", "pending",
    [('chicken_65', 2), ('butter_chicken', 1), ('tandoori_roti', 3)]
)

# Order 5: Pending order
order5 = create_order_with_items(
    "Vivek Bharadwaj", "sunny.vivek28122009@gmail.com", "pending",
    [('veg_biryani', 2), ('masala_chai', 2)]
)

# Order 6: Ready order
order6 = create_order_with_items(
    "Hemanth", "saketh.tukuntla@gmail.com", "ready",
    [('samosa', 4), ('chicken_biryani', 1), ('mango_lassi', 2)]
)

# Order 7: Pending order
order7 = create_order_with_items(
    "Vivek Kumar", "pert.vivek@gmail.com", "pending",
    [('dal_makhani', 1), ('butter_naan', 2)]
)

# Order 8: Preparing order
order8 = create_order_with_items(
    "Phagun Jain", "phagunjain007@gmail.com", "preparing",
    [('paneer_butter_masala', 1), ('garlic_naan', 2), ('mango_lassi', 1)]
)

# Order 9: Pending order
order9 = create_order_with_items(
    "Gobi Karunagaran", "gobikarunagaran@gmail.com", "pending",
    [('butter_chicken', 2), ('chicken_biryani', 1), ('butter_naan', 4)]
)

# Order 10: Large family order - pending
order10 = create_order_with_items(
    "Parithiban", "parithiban1@gmail.com", "pending",
    [
        ('chicken_65', 2),
        ('paneer_tikka', 2),
        ('butter_chicken', 2),
        ('dal_makhani', 1),
        ('chicken_biryani', 2),
        ('butter_naan', 6),
        ('gulab_jamun', 4),
        ('mango_lassi', 4)
    ],
    "Family dinner - 8 people"
)

# Order 11: Office party - preparing
order11 = create_order_with_items(
    "Rahul Naik", "rahulnaik921.421@gmail.com", "preparing",
    [('chicken_biryani', 5), ('veg_biryani', 3), ('masala_chai', 8)],
    "Office party - 10 biryanis total"
)

# Order 12: Simple ready order
order12 = create_order_with_items(
    "Amin Firnash L", "aminfirnash.freelancer@gmail.com", "ready",
    [('samosa', 2), ('masala_chai', 1)]
)

# Order 13: Cancelled order
order13 = create_order_with_items(
    "Kotha Indresh", "kothaindresh44@gmail.com", "cancelled",
    [('butter_chicken', 1), ('butter_naan', 2)],
    "Customer changed mind"
)

# Order 14: Completed order
order14 = create_order_with_items(
    "Srineketh", "sriniketh1225@gmail.com", "completed",
    [('veg_biryani', 1), ('dal_makhani', 1)]
)

# Order 15: Pending order
order15 = create_order_with_items(
    "Rohit Panchal", "rohitxofficial@gmail.com", "pending",
    [('chicken_65', 1), ('chicken_biryani', 1), ('mango_lassi', 1)]
)

print(f"  ✓ Orders created: {Order.objects.count()}")
print(f"  ✓ Order items: {OrderItem.objects.count()}")


# =============================================================================
# CREATE INVOICES FOR COMPLETED ORDERS (OneToOne Demo)
# =============================================================================
print("\nGenerating invoices for completed orders...")

completed_orders = Order.objects.filter(status='completed')
for order in completed_orders:
    order.generate_invoice()

print(f"  ✓ Invoices created: {OrderInvoice.objects.count()}")


# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("  SEED DATA CREATED SUCCESSFULLY!")
print("=" * 70)
print(f"\n  Categories:    {Category.objects.count()}")
print(f"  Menu Items:    {MenuItem.objects.count()}")
if HAS_INHERITANCE:
    print(f"     Food:        {Food.objects.count()}")
    print(f"     Beverage:    {Beverage.objects.count()}")
print(f"\n  Orders:        {Order.objects.count()}")
print(f"     Pending:     {Order.objects.filter(status='pending').count()}")
print(f"     Preparing:   {Order.objects.filter(status='preparing').count()}")
print(f"     Ready:       {Order.objects.filter(status='ready').count()}")
print(f"     Completed:   {Order.objects.filter(status='completed').count()}")
print(f"     Cancelled:   {Order.objects.filter(status='cancelled').count()}")
print(f"\n  Order Items:   {OrderItem.objects.count()}")
print(f"  Invoices:      {OrderInvoice.objects.count()}")
print("=" * 70)
print("\n  Next: Run 'python demo_n1_problem.py' to see the N+1 demo!")
print("=" * 70)
