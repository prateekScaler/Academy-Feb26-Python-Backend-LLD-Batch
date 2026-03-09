# Class 4 Code: Django Apps, Views & URLs

This folder contains the working code taught in Class 4.

## What's Included

```
restaurant_project/
├── manage.py                    # Django's command-line tool
├── restaurant_project/
│   ├── __init__.py
│   ├── settings.py              # Project settings (INSTALLED_APPS)
│   ├── urls.py                  # Main URL router
│   └── wsgi.py
└── menu/
    ├── __init__.py
    ├── views.py                 # View functions
    └── urls.py                  # App URL patterns
```

## How to Use This Code

```bash
# 1. Create a new project folder
mkdir my_restaurant && cd my_restaurant

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install Django
pip install django

# 4. Create project (or copy these files)
django-admin startproject restaurant_project .
python manage.py startapp menu

# 5. Copy the files from this folder to your project

# 6. Run the server
python manage.py runserver
```

## Test URLs

| URL | Expected Response |
|-----|-------------------|
| http://127.0.0.1:8000/menu/ | Welcome message |
| http://127.0.0.1:8000/menu/list/ | Menu items list |
| http://127.0.0.1:8000/menu/item/1/ | Item #1 details |
| http://127.0.0.1:8000/menu/about/ | About page |
| http://127.0.0.1:8000/menu/api/ | JSON response |

## Key Concepts Covered

1. **Creating a Django App** - `python manage.py startapp menu`
2. **Registering Apps** - Adding to `INSTALLED_APPS`
3. **Writing Views** - Function-based views with `HttpResponse`
4. **URL Routing** - `path()` and `include()`
5. **URL Parameters** - `<int:item_id>`
6. **Relative Imports** - `from . import views`

## Next Class (Class 5)

In Class 5, we'll add **Models** to store data in a database instead of hardcoding it in views!
