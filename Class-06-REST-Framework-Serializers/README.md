# Class 6: REST Framework & Serializers

## Pre-Class Quiz: Test Your Class 5 Knowledge

### Question 1: Migration Safety
Your `MenuItem` model has 10,000 rows in production. You add this field:
```python
category = models.ForeignKey(Category, on_delete=models.CASCADE)
```
**What happens when you run `makemigrations`?**

<details>
<summary>Answer</summary>

**B) Django asks for a default value because existing rows need a `category_id`**

When adding a NOT NULL field to a table with existing rows, Django must know what value to put in that column. Safe approach: Add `null=True` first, migrate, backfill data, then remove `null=True`.
</details>

---

### Question 2: Adding Fields
**You added `is_featured = models.BooleanField()` to MenuItem. What happens on `makemigrations`?**

<details>
<summary>Answer</summary>

**B) Django asks for a default value (existing rows need a value)**

Fix: Add `default=False` to avoid the prompt.
</details>

---

### Question 3: QuerySets
```python
MenuItem.objects.filter(price__lte=10, is_available=True)
```
**What does this return?**

<details>
<summary>Answer</summary>

**B) Items where price ≤ 10 AND is_available = True**

Multiple conditions in `filter()` are combined with AND. `__lte` = less than or equal.
</details>

---

### Question 4: Why Separate Frontend?
**Django can render HTML templates. So why do modern apps often have a separate frontend (React, Vue, mobile app) fetching data from the backend?**

<details>
<summary>Answer</summary>

**C) Multiple clients (web, iOS, Android) can share the same backend data**

**The shift happened ~2010-2015** with smartphones and SPAs.

**Before:** Server renders HTML → Browser displays it. But...
- Mobile apps can't use HTML — they need raw data
- Every page refresh reloads everything — slow UX
- Frontend/backend teams tightly coupled

**Now:** Backend sends **data (JSON)** → Any client renders it however it wants.

This is why we need proper data APIs!
</details>

---

## Learning Objectives

By the end of this class, you will:

1. Understand why APIs return JSON instead of HTML
2. Know REST principles (resources, HTTP methods, statelessness, status codes)
3. Build a basic REST API with @api_view
4. Understand why Serializers are needed
5. Create Serializers to convert models to JSON
6. Build API endpoints with ViewSets
7. Use Routers for automatic URL generation

---

## Why APIs?

HTML views work for browsers, but what about:
- Mobile apps (iOS, Android)
- React/Vue frontends
- Third-party integrations

**Solution:** Return JSON data that any client can consume.

---

## What is REST?

REST (REpresentational State Transfer) is a design philosophy:

| Principle | Description |
|-----------|-------------|
| **Resource URLs** | URLs are nouns: `/api/menu-items/` not `/getMenuItems` |
| **HTTP Methods** | GET=Read, POST=Create, PUT=Update, DELETE=Delete |
| **Stateless** | Each request contains all needed info |
| **Status Codes** | 200=OK, 201=Created, 400=Bad Request, 404=Not Found |

---

## HTTP Methods (CRUD)

| Method | CRUD | Example URL | Purpose |
|--------|------|-------------|---------|
| GET | Read | `/api/menu-items/` | List all |
| GET | Read | `/api/menu-items/5/` | Get one |
| POST | Create | `/api/menu-items/` | Create new |
| PUT | Update | `/api/menu-items/5/` | Replace |
| PATCH | Update | `/api/menu-items/5/` | Partial update |
| DELETE | Delete | `/api/menu-items/5/` | Delete |

---

## Statelessness Explained

In REST, the server doesn't remember anything about previous requests.

**Stateful (NOT REST):**
```
Client: "Login as Prateek"
Server: "OK, I remember you" (stores session)
Client: "Show my orders"
Server: (looks up session) → Returns orders
```

**Stateless (REST):**
```
Client: "Show my orders" + Token: xyz123
Server: (validates token) → Returns orders
        (stores nothing!)
```

**Why Stateless?**
- Any server can handle any request (easy scaling)
- Server crash doesn't affect users
- Simple load balancing

---

## Step 1: Install Django REST Framework

```bash
pip install djangorestframework
```

Add to `settings.py`:
```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'menu',
]
```

---

## Step 2: Build Basic REST API (Manual Way)

```python
# menu/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
def menu_items_api(request):
    items = MenuItem.objects.filter(is_available=True)

    # Manual conversion - tedious!
    items_list = []
    for item in items:
        items_list.append({
            "id": item.id,
            "name": item.name,
            "price": str(item.price),  # Decimal → string
            "category": item.category.name,
        })

    return Response(items_list)
```

**Pain points:**
- Manual field-by-field conversion
- `Decimal` isn't JSON serializable — need `str(item.price)`
- 20 fields = 20 lines of repetitive code
- No validation for POST/PUT

**Solution:** Serializers!

---

## Step 3: Serializers

Serializers convert Python objects ↔ JSON:

```python
# menu/serializers.py

from rest_framework import serializers
from .models import MenuItem, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'is_available', 'category', 'category_name']
```

**Now the view becomes:**
```python
@api_view(['GET'])
def menu_items_api(request):
    items = MenuItem.objects.all()
    serializer = MenuItemSerializer(items, many=True)
    return Response(serializer.data)  # That's it!
```

---

## Step 4: ViewSets

ViewSets provide full CRUD with minimal code:

```python
# menu/views.py

from rest_framework import viewsets
from .models import MenuItem, Category
from .serializers import MenuItemSerializer, CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
```

---

## Step 5: URL Configuration

```python
# menu/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('categories', views.CategoryViewSet)
router.register('menu-items', views.MenuItemViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
```

This auto-generates:
- `/api/categories/` (GET, POST)
- `/api/categories/1/` (GET, PUT, PATCH, DELETE)
- `/api/menu-items/` (GET, POST)
- `/api/menu-items/1/` (GET, PUT, PATCH, DELETE)

---

## Testing APIs

**1. Browser (Browsable API):**
Visit `http://127.0.0.1:8000/menu/api/menu-items/`

**2. curl:**
```bash
curl http://127.0.0.1:8000/menu/api/menu-items/
curl -X POST http://127.0.0.1:8000/menu/api/menu-items/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Pizza", "price": "12.99", "category": 1}'
```

**3. httpie:**
```bash
http GET :8000/menu/api/menu-items/
http POST :8000/menu/api/menu-items/ name="Pizza" price="12.99" category=1
```

---

## Quick Commands

```bash
# Install DRF
pip install djangorestframework

# Add to settings.py INSTALLED_APPS
'rest_framework',

# Run server
python manage.py runserver

# Test API
curl http://127.0.0.1:8000/menu/api/menu-items/
```

---

## Files Created Today

| File | Purpose |
|------|---------|
| `menu/serializers.py` | Define model ↔ JSON conversion |
| `menu/views.py` | API endpoints (ViewSets) |
| `menu/urls.py` | Router configuration |
| `settings.py` | Added 'rest_framework' |

---

## Teaching Flow

```
REST Concepts → Build Basic API → Feel the Pain → Serializers → ViewSets
```

---

*Class 6 - REST Framework & Serializers*
