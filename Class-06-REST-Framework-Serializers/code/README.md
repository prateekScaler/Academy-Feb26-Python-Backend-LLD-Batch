# Restaurant Project - Class 6 Starting Point

This is the project state BEFORE adding Django REST Framework.

## Current State

- ✅ Models: Category, MenuItem (from Class 5)
- ✅ Admin: Registered with list_display, filters
- ✅ Views: Using models, returning text/basic JSON
- ❌ DRF: Not installed yet
- ❌ Serializers: Not created yet

## Setup

```bash
cd restaurant_project
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install django
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Add Sample Data

1. Go to http://127.0.0.1:8000/admin/
2. Add Categories: Appetizers, Main Course, Desserts
3. Add Menu Items

## Current Endpoints

| URL | Response |
|-----|----------|
| /menu/ | Welcome page (text) |
| /menu/list/ | Menu list (text) |
| /menu/item/1/ | Item detail (text) |
| /menu/categories/ | Categories (text) |
| /menu/api/ | JSON (manual serialization) |

## The Problem

Look at `menu/views.py` - the `menu_json()` function manually converts each field to JSON. This is:
- Tedious for many fields
- No validation for POST/PUT
- No standard CRUD patterns

## What We'll Add (Class 6)

1. `pip install djangorestframework`
2. Create `menu/serializers.py`
3. Create ViewSets in `menu/views.py`
4. Add Router in `menu/urls.py`
5. Full REST API at `/menu/api/`
