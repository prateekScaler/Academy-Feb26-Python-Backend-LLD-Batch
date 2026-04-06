# Class 14: Hands-On Guide — Pagination, Searching & Sorting

> Step-by-step guide to add pagination, search, and sorting to the restaurant project's menu API. By the end, you'll have a fully functional API like: `GET /menu/items/?search=chicken&ordering=-price&page=1&size=10`

**DRF Docs:** https://www.django-rest-framework.org/api-guide/pagination/

---

## Pre-requisites

- The `restaurant_project` with `core`, `menu`, and `orders` apps working
- Python 3.10+ with virtualenv active
- Data in the database (categories and menu items) — run `seed_data.py` if needed

---

## Part 1: Build the Menu API (From Scratch)

Right now the `menu/views.py` is empty. Let's build a proper API with DRF serializers and generic views.

### Step 1: Create Serializers

Create `menu/serializers.py`:

```python
from rest_framework import serializers
from .models import Category, MenuItem, Food, Beverage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'description', 'price',
            'category', 'category_name',
            'is_available', 'image_url',
            'created_at', 'updated_at',
        ]


class FoodSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Food
        fields = [
            'id', 'name', 'description', 'price',
            'category', 'category_name',
            'is_available', 'image_url',
            'is_vegetarian', 'calories', 'preparation_time_minutes',
            'created_at', 'updated_at',
        ]


class BeverageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Beverage
        fields = [
            'id', 'name', 'description', 'price',
            'category', 'category_name',
            'is_available', 'image_url',
            'is_alcoholic', 'volume_ml', 'served_cold',
            'created_at', 'updated_at',
        ]
```

### Step 2: Create Views (No Pagination Yet)

Open `menu/views.py` and replace with:

```python
from rest_framework import generics
from .models import Category, MenuItem, Food, Beverage
from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
    FoodSerializer,
    BeverageSerializer,
)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuItemListView(generics.ListAPIView):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer


class FoodListView(generics.ListAPIView):
    queryset = Food.objects.select_related('category').all()
    serializer_class = FoodSerializer


class BeverageListView(generics.ListAPIView):
    queryset = Beverage.objects.select_related('category').all()
    serializer_class = BeverageSerializer
```

### Step 3: Add URLs

Open `menu/urls.py` and replace with:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('items/', views.MenuItemListView.as_view(), name='menuitem-list'),
    path('food/', views.FoodListView.as_view(), name='food-list'),
    path('beverages/', views.BeverageListView.as_view(), name='beverage-list'),
]
```

### Step 4: Test It

```bash
python manage.py runserver
```

```bash
# List all menu items
curl http://127.0.0.1:8000/menu/items/ | python -m json.tool

# List food items
curl http://127.0.0.1:8000/menu/food/ | python -m json.tool

# List categories
curl http://127.0.0.1:8000/menu/categories/ | python -m json.tool
```

Right now this returns ALL items with no pagination. Let's fix that.

---

## Part 2: Add Pagination

### Step 5: Global Pagination (settings.py)

Add to `restaurant_project/settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}
```

Restart the server and test:

```bash
curl http://127.0.0.1:8000/menu/items/ | python -m json.tool
```

Response now has `count`, `next`, `previous`, and `results`:

```json
{
    "count": 25,
    "next": "http://127.0.0.1:8000/menu/items/?page=2",
    "previous": null,
    "results": [
        {"id": 1, "name": "Butter Chicken", ...},
        ...
    ]
}
```

```bash
# Page 2
curl "http://127.0.0.1:8000/menu/items/?page=2" | python -m json.tool

# Page 3 (if exists)
curl "http://127.0.0.1:8000/menu/items/?page=3" | python -m json.tool
```

### Step 6: Custom Pagination (Per-View)

Create `menu/pagination.py`:

```python
from rest_framework.pagination import PageNumberPagination


class MenuPagination(PageNumberPagination):
    page_size = 10                    # Default: 10 items per page
    page_size_query_param = 'size'    # Client can override: ?size=20
    max_page_size = 50                # Cap: never more than 50
```

Update `menu/views.py` to use it:

```python
from .pagination import MenuPagination

class MenuItemListView(generics.ListAPIView):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    pagination_class = MenuPagination
```

Test:

```bash
# Default (10 items)
curl http://127.0.0.1:8000/menu/items/ | python -m json.tool

# Custom page size
curl "http://127.0.0.1:8000/menu/items/?size=5" | python -m json.tool

# Page 2 with 5 items per page
curl "http://127.0.0.1:8000/menu/items/?page=2&size=5" | python -m json.tool

# Try requesting too many — capped at 50
curl "http://127.0.0.1:8000/menu/items/?size=999" | python -m json.tool
```

---

## Part 3: Add Search

### Step 7: Enable SearchFilter

Update `menu/views.py`:

```python
from rest_framework import generics, filters
from .models import Category, MenuItem, Food, Beverage
from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
    FoodSerializer,
    BeverageSerializer,
)
from .pagination import MenuPagination


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuItemListView(generics.ListAPIView):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    pagination_class = MenuPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'category__name']


class FoodListView(generics.ListAPIView):
    queryset = Food.objects.select_related('category').all()
    serializer_class = FoodSerializer
    pagination_class = MenuPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'category__name']


class BeverageListView(generics.ListAPIView):
    queryset = Beverage.objects.select_related('category').all()
    serializer_class = BeverageSerializer
    pagination_class = MenuPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
```

Test:

```bash
# Search for "chicken"
curl "http://127.0.0.1:8000/menu/items/?search=chicken" | python -m json.tool

# Search for "paneer"
curl "http://127.0.0.1:8000/menu/items/?search=paneer" | python -m json.tool

# Search in food items
curl "http://127.0.0.1:8000/menu/food/?search=biryani" | python -m json.tool

# Search by category name
curl "http://127.0.0.1:8000/menu/items/?search=dessert" | python -m json.tool

# Search + pagination
curl "http://127.0.0.1:8000/menu/items/?search=chicken&page=1&size=5" | python -m json.tool
```

---

## Part 4: Add Sorting

### Step 8: Enable OrderingFilter

Update `menu/views.py` — add `OrderingFilter` to the existing filter backends:

```python
class MenuItemListView(generics.ListAPIView):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    pagination_class = MenuPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']   # Default: newest first


class FoodListView(generics.ListAPIView):
    queryset = Food.objects.select_related('category').all()
    serializer_class = FoodSerializer
    pagination_class = MenuPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['name', 'price', 'calories', 'preparation_time_minutes', 'created_at']
    ordering = ['name']


class BeverageListView(generics.ListAPIView):
    queryset = Beverage.objects.select_related('category').all()
    serializer_class = BeverageSerializer
    pagination_class = MenuPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'volume_ml', 'created_at']
    ordering = ['name']
```

Test:

```bash
# Sort by price (cheapest first)
curl "http://127.0.0.1:8000/menu/items/?ordering=price" | python -m json.tool

# Sort by price (most expensive first)
curl "http://127.0.0.1:8000/menu/items/?ordering=-price" | python -m json.tool

# Sort alphabetically
curl "http://127.0.0.1:8000/menu/items/?ordering=name" | python -m json.tool

# Sort food by calories
curl "http://127.0.0.1:8000/menu/food/?ordering=calories" | python -m json.tool

# Sort food by preparation time (longest first)
curl "http://127.0.0.1:8000/menu/food/?ordering=-preparation_time_minutes" | python -m json.tool
```

---

## Part 5: Combine Everything

### Step 9: The Full Query

Now all three features work together:

```bash
# Search "chicken", sort by price (cheapest), page 1, 5 per page
curl "http://127.0.0.1:8000/menu/items/?search=chicken&ordering=price&page=1&size=5" | python -m json.tool

# Search "paneer", sort by name A-Z, page 1
curl "http://127.0.0.1:8000/menu/food/?search=paneer&ordering=name" | python -m json.tool

# All items, most expensive first, 3 per page
curl "http://127.0.0.1:8000/menu/items/?ordering=-price&size=3" | python -m json.tool
```

---

## Part 6: Add Filtering with django-filter (Optional)

### Step 10: Install and Configure

```bash
pip install django-filter
```

Add to `settings.py`:

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'django_filters',    # ADD THIS
]
```

### Step 11: Create Filters

Create `menu/filters.py`:

```python
import django_filters
from .models import Food, Beverage, MenuItem


class MenuItemFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = django_filters.CharFilter(field_name='category__name', lookup_expr='iexact')

    class Meta:
        model = MenuItem
        fields = ['is_available']


class FoodFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = django_filters.CharFilter(field_name='category__name', lookup_expr='iexact')
    max_calories = django_filters.NumberFilter(field_name='calories', lookup_expr='lte')
    max_prep_time = django_filters.NumberFilter(field_name='preparation_time_minutes', lookup_expr='lte')

    class Meta:
        model = Food
        fields = ['is_available', 'is_vegetarian']


class BeverageFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Beverage
        fields = ['is_available', 'is_alcoholic', 'served_cold']
```

### Step 12: Add to Views

Update `menu/views.py`:

```python
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters
from .models import Category, MenuItem, Food, Beverage
from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
    FoodSerializer,
    BeverageSerializer,
)
from .pagination import MenuPagination
from .filters import MenuItemFilter, FoodFilter, BeverageFilter


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuItemListView(generics.ListAPIView):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    pagination_class = MenuPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MenuItemFilter
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']


class FoodListView(generics.ListAPIView):
    queryset = Food.objects.select_related('category').all()
    serializer_class = FoodSerializer
    pagination_class = MenuPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = FoodFilter
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['name', 'price', 'calories', 'preparation_time_minutes', 'created_at']
    ordering = ['name']


class BeverageListView(generics.ListAPIView):
    queryset = Beverage.objects.select_related('category').all()
    serializer_class = BeverageSerializer
    pagination_class = MenuPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BeverageFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'volume_ml', 'created_at']
    ordering = ['name']
```

Test:

```bash
# Only vegetarian food
curl "http://127.0.0.1:8000/menu/food/?is_vegetarian=true" | python -m json.tool

# Food under Rs.200
curl "http://127.0.0.1:8000/menu/food/?price_max=200" | python -m json.tool

# Vegetarian food under Rs.300, sorted by price
curl "http://127.0.0.1:8000/menu/food/?is_vegetarian=true&price_max=300&ordering=price" | python -m json.tool

# Main course items between Rs.200-400
curl "http://127.0.0.1:8000/menu/items/?category=Main+Course&price_min=200&price_max=400" | python -m json.tool

# Cold beverages, cheapest first
curl "http://127.0.0.1:8000/menu/beverages/?served_cold=true&ordering=price" | python -m json.tool

# THE ULTIMATE QUERY: vegetarian food, under 500 calories, search "paneer", cheapest first, page 1
curl "http://127.0.0.1:8000/menu/food/?is_vegetarian=true&max_calories=500&search=paneer&ordering=price&page=1&size=5" | python -m json.tool
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'django_filters'` | `pip install django-filter` (note: package is `django-filter`, import is `django_filters`) |
| `?search=` returns nothing | Check `search_fields` — make sure the field names match your model |
| `?ordering=calories` gives error | The field must be in `ordering_fields` whitelist |
| Pagination not showing `count`/`next` | Make sure `REST_FRAMEWORK` is set in settings.py and view uses `ListAPIView` |
| `select_related` not working | It only works for ForeignKey/OneToOne. Use `prefetch_related` for ManyToMany |
| All items returned despite pagination | Make sure you're using `generics.ListAPIView`, not a function view with manual `JsonResponse` |

---

## Final File Structure

```
restaurant_project/
└── menu/
    ├── models.py            ← Category, MenuItem, Food, Beverage (unchanged)
    ├── serializers.py       ← NEW: DRF serializers
    ├── views.py             ← UPDATED: ListAPIView with pagination, search, sort, filter
    ├── urls.py              ← UPDATED: 4 endpoints
    ├── pagination.py        ← NEW: Custom pagination class
    └── filters.py           ← NEW: django-filter FilterSets
```
