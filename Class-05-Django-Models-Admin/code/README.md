# Class 5 Code: Django Models & Admin

This folder contains the working code taught in Class 5, building on Class 4.

## What's New in Class 5

```
restaurant_project/
├── manage.py
├── restaurant_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── menu/
    ├── __init__.py
    ├── models.py              # NEW! Database models
    ├── admin.py               # NEW! Admin configuration
    ├── views.py               # UPDATED! Uses models now
    └── urls.py
```

## How to Use This Code

```bash
# 1. Set up project (see Class 4 or start fresh)
mkdir my_restaurant && cd my_restaurant
python3 -m venv venv
source venv/bin/activate
pip install django
django-admin startproject restaurant_project .
python manage.py startapp menu

# 2. Copy the files from this folder

# 3. Run migrations to create database tables
python manage.py makemigrations
python manage.py migrate

# 4. Create a superuser for admin access
python manage.py createsuperuser

# 5. Run the server
python manage.py runserver

# 6. Visit admin at http://127.0.0.1:8000/admin/
```

## Key Files Changed from Class 4

| File | What Changed |
|------|--------------|
| `models.py` | NEW - Category and MenuItem models |
| `admin.py` | NEW - Admin configuration |
| `views.py` | UPDATED - Uses `MenuItem.objects` instead of hardcoded data |

## Test URLs

| URL | Expected Response |
|-----|-------------------|
| http://127.0.0.1:8000/admin/ | Django Admin (login required) |
| http://127.0.0.1:8000/menu/ | Welcome message |
| http://127.0.0.1:8000/menu/list/ | Menu items FROM DATABASE |
| http://127.0.0.1:8000/menu/item/1/ | Item details FROM DATABASE |
| http://127.0.0.1:8000/menu/categories/ | Categories with counts |
| http://127.0.0.1:8000/menu/api/ | JSON response |

## Key Concepts Covered

1. **Defining Models** - `class MenuItem(models.Model)`
2. **Field Types** - CharField, DecimalField, ForeignKey, etc.
3. **Migrations** - `makemigrations` and `migrate`
4. **Django Admin** - `@admin.register()` decorator
5. **QuerySets** - `MenuItem.objects.filter(is_available=True)`
6. **Relationships** - ForeignKey with `related_name`

## Django Shell Examples

```python
python manage.py shell

>>> from menu.models import Category, MenuItem

# Create a category
>>> cat = Category.objects.create(name="Appetizers")

# Create an item
>>> MenuItem.objects.create(name="Garlic Bread", price=6.99, category=cat)

# Query items
>>> MenuItem.objects.filter(is_available=True)
>>> MenuItem.objects.filter(price__lt=10)

# Reverse relationship
>>> cat.items.all()
```

## Next Class (Class 6)

In Class 6, we'll add **Django REST Framework** for proper API endpoints!
