# Class 5: Django Models & Admin

## Pre-Class Quiz: Test Your Class 4 Knowledge

### Question 1: URL Pattern Ordering

```python
urlpatterns = [
    path('products/<str:name>/', views.product_by_name),
    path('products/featured/', views.featured_products),
]
```

**What happens when you visit `/products/featured/`?**

<details>
<summary>Answer</summary>

**B) `product_by_name` view is called with `name="featured"`**

Django checks URL patterns **in order**. The first pattern `<str:name>` matches "featured" as a string.

**Fix:** Put specific patterns before generic ones.
</details>

---

### Question 2: include() Purpose

```python
path('menu/', include('menu.urls')),
```

**What does `include()` do?**

<details>
<summary>Answer</summary>

**B) Delegates URL matching to the app's urls.py**

It tells Django: "For URLs starting with `menu/`, look at `menu/urls.py` for the rest."
</details>

---

### Question 3: Relative Imports

```python
from restaurantproject.menu import views  # Line A
from . import views                        # Line B
```

**Which is correct?**

<details>
<summary>Answer</summary>

**B) Line B — relative imports keep apps portable**

If you rename the project or reuse the app, Line A breaks. Line B always works.
</details>

---

### Question 4: Project vs App

**What is the relationship between a Django project and app?**

<details>
<summary>Answer</summary>

**B) A project is the entire website; apps are reusable components within it**

- **Project** = config (settings, root URLs)
- **App** = feature (menu, orders, users)
</details>

---

### Question 5: Why Multiple Apps

**Why split a Django project into multiple apps?**

<details>
<summary>Answer</summary>

**C) Separation of concerns — each app handles one feature, easier to maintain**

Instagram has separate apps for posts, stories, reels, messaging.
</details>

---

### Question 6: URL Parameters

```python
# urls.py
path('order/<int:order_id>/', views.order_detail)

# views.py
def order_detail(request):
    return HttpResponse(f"Order #{order_id}")
```

**What's wrong?**

<details>
<summary>Answer</summary>

**B) The view is missing the `order_id` parameter**

Fix: `def order_detail(request, order_id):`
</details>

---

## Learning Objectives

By the end of this class, you will:

1. Understand what Django Models are and why we need them
2. Create models with different field types
3. Understand Primary Keys, Meta class, and `__str__`
4. Use Django migrations (including rollbacks)
5. Use Django Admin to manage data
6. Import data via CSV using django-import-export
7. Query data using Django Shell and QuerySets

---

## What is a Model?

A **Model** is a Python class that represents a database table.

```
Python Class  ←→  Database Table
Attribute     ←→  Column
Instance      ←→  Row
```

---

## Defining Models

```python
# menu/models.py

from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='items'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (${self.price})"
```

### Field Types

| Field | Purpose | Example |
|-------|---------|---------|
| `CharField(max_length=100)` | Short text | `"Pasta Alfredo"` |
| `TextField()` | Long text | `"A creamy pasta..."` |
| `DecimalField(max_digits=6, decimal_places=2)` | Money | `15.99` |
| `BooleanField(default=True)` | True/False | `True` |
| `DateTimeField(auto_now_add=True)` | Created timestamp | Auto-set once |
| `DateTimeField(auto_now=True)` | Updated timestamp | Auto-updates |
| `ForeignKey(...)` | Relationship | Links to Category |

### Primary Key

Django auto-adds an `id` field:

```python
# You don't write this — Django adds it automatically:
id = models.BigAutoField(primary_key=True)
```

To use UUID instead:
```python
import uuid
id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
```

### class Meta

```python
class Meta:
    verbose_name_plural = "Categories"  # Fixes "Categorys" in admin
    ordering = ['name']                  # Default sort
```

### `__str__` Method

| Without | With |
|---------|------|
| `<MenuItem: MenuItem object (1)>` | `<MenuItem: Pasta Alfredo ($15.99)>` |

### Why `created_at` and `updated_at`?

- **Debugging:** "When was this created?"
- **Sorting:** Show newest first
- **Analytics:** "How many orders today?"
- **Caching:** "Has this changed?"

### `related_name`

```python
category = models.ForeignKey(Category, related_name='items', ...)

# Without related_name:
category.menuitem_set.all()  # Default

# With related_name='items':
category.items.all()  # Much cleaner!
```

---

## Migrations

```bash
# Create migration files
python manage.py makemigrations menu

# Apply to database
python manage.py migrate

# See migration status
python manage.py showmigrations

# Rollback to specific migration
python manage.py migrate menu 0001
```

### Adding Fields to Existing Tables

When adding a required field, Django asks for a default value. Best practice:

```python
# Add default in the model
spice_level = models.CharField(max_length=20, default='medium')
```

---

## Django Admin

### Setup

```bash
python manage.py createsuperuser
```

```python
# menu/admin.py
from django.contrib import admin
from .models import Category, MenuItem

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'is_available']
    list_filter = ['category', 'is_available']
    search_fields = ['name']
    list_editable = ['price', 'is_available']
```

### Who Uses Admin in Production?

| Who | Uses Admin? | Why |
|-----|-------------|-----|
| End Users | ❌ Never | They use your frontend |
| Content Managers | ✅ Yes | Update menu, prices |
| Support Team | ✅ Yes | Look up orders |
| Developers | ✅ Yes | Debug, test |

---

## CSV Import via Admin

Install: `pip install django-import-export`

```python
# menu/admin.py
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin

class MenuItemResource(resources.ModelResource):
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, field='name')
    )

    class Meta:
        model = MenuItem
        fields = ('name', 'description', 'price', 'is_available', 'category')

@admin.register(MenuItem)
class MenuItemAdmin(ImportExportModelAdmin):
    resource_class = MenuItemResource
    # ...
```

**Sample CSV:**
```csv
name,description,price,is_available,category
Garlic Bread,Fresh baked,6.99,True,Appetizers
Pasta Alfredo,Creamy pasta,15.99,True,Main Course
```

---

## Django Shell

```bash
python manage.py shell
```

```python
from menu.models import Category, MenuItem

# Create
appetizers = Category.objects.create(name="Appetizers")

# Query
MenuItem.objects.all()
MenuItem.objects.filter(is_available=True)
MenuItem.objects.filter(price__lt=10)
MenuItem.objects.get(id=1)

# Relationships
item.category.name          # Forward
category.items.all()        # Reverse (related_name)

# Chaining
MenuItem.objects.filter(category__name="Main Course").order_by('-price')
```

---

## QuerySet Methods

| Method | Purpose |
|--------|---------|
| `all()` | Get all objects |
| `filter()` | Get matching |
| `exclude()` | Get non-matching |
| `get()` | Get single object |
| `count()` | Count results |
| `order_by()` | Sort results |
| `first()` | First match |
| `values()` | Get dictionaries |

## Field Lookups

| Lookup | Example |
|--------|---------|
| `exact` | `name__exact='Pasta'` |
| `icontains` | `name__icontains='pasta'` |
| `gt`, `gte` | `price__gt=10` |
| `lt`, `lte` | `price__lte=20` |
| `in` | `id__in=[1, 2, 3]` |

---

## Quick Commands

```bash
python manage.py makemigrations    # Create migrations
python manage.py migrate           # Apply migrations
python manage.py createsuperuser   # Create admin user
python manage.py shell             # Django shell
python manage.py runserver         # Run server
python manage.py showmigrations    # See migration status
```

---

## Practice Exercises

1. Add `is_featured` boolean to MenuItem
2. Create a `Review` model (rating 1-5, comment, menu_item FK)
3. Import 10 menu items via CSV
4. Query: Find all items under $10 in "Appetizers" category

---

*Class 5 - Django Models & Admin*
