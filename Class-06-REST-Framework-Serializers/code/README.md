# Restaurant Project - Class 6: REST Framework & Serializers

This project demonstrates Django REST Framework with a focus on Serializers.

## Project Structure

```
restaurant_project/
├── manage.py
├── restaurantproject/          # Project settings
│   ├── settings.py
│   └── urls.py
├── menu/                       # Menu app (from Class 5)
│   ├── models.py              # Category, MenuItem
│   ├── views.py
│   └── urls.py
└── orders/                     # Orders app (NEW - Class 6)
    ├── models.py              # Order model
    ├── serializers.py         # OrderSerializer with validation
    ├── views.py               # @api_view and ViewSet examples
    ├── urls.py                # Router configuration
    └── admin.py
```

## Setup

```bash
cd restaurant_project
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install django djangorestframework
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/orders/` | List all orders |
| POST | `/api/orders/` | Create new order |
| GET | `/api/orders/{id}/` | Get single order |
| PUT | `/api/orders/{id}/` | Full update |
| PATCH | `/api/orders/{id}/` | Partial update |
| DELETE | `/api/orders/{id}/` | Delete order |
| GET | `/api/orders/pending/` | List pending orders only |
| POST | `/api/orders/{id}/confirm/` | Confirm a pending order |

## Testing the API

### Using curl

```bash
# List all orders
curl http://127.0.0.1:8000/api/orders/

# Create an order
curl -X POST http://127.0.0.1:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "John Doe", "customer_phone": "9876543210", "total_amount": "150.00"}'

# Get single order
curl http://127.0.0.1:8000/api/orders/1/

# Update order status
curl -X PATCH http://127.0.0.1:8000/api/orders/1/ \
  -H "Content-Type: application/json" \
  -d '{"status": "confirmed"}'

# Confirm order (custom action)
curl -X POST http://127.0.0.1:8000/api/orders/1/confirm/

# Delete order
curl -X DELETE http://127.0.0.1:8000/api/orders/1/
```

### Using httpie

```bash
# List all orders
http GET :8000/api/orders/

# Create an order
http POST :8000/api/orders/ customer_name="Jane Doe" customer_phone="9876543210" total_amount="200.00"

# Get pending orders
http GET :8000/api/orders/pending/
```

---

# Assignment Questions

Complete these exercises to practice what you learned in Class 6.

## Exercise 1: Add a Menu Item Serializer (Easy)

Create a `MenuItemSerializer` in `menu/serializers.py`:

1. Include fields: `id`, `name`, `description`, `price`, `is_available`, `category`
2. Add a read-only field `category_name` that shows the category's name
3. Make `created_at` and `updated_at` read-only

**Expected output when serializing:**
```json
{
    "id": 1,
    "name": "Margherita Pizza",
    "description": "Classic tomato and mozzarella",
    "price": "12.99",
    "is_available": true,
    "category": 1,
    "category_name": "Main Course"
}
```

---

## Exercise 2: Add Validation (Medium)

Add these validations to your `MenuItemSerializer`:

1. `validate_name`: Name must be at least 3 characters
2. `validate_price`: Price must be greater than 0
3. `validate`: (cross-field) If `is_available` is True, `price` cannot be 0

**Test your validation:**
```bash
# Should fail - name too short
curl -X POST http://127.0.0.1:8000/menu/api/menu-items/ \
  -H "Content-Type: application/json" \
  -d '{"name": "AB", "price": "10.00", "category": 1}'

# Should fail - price is 0
curl -X POST http://127.0.0.1:8000/menu/api/menu-items/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Free Item", "price": "0", "is_available": true, "category": 1}'
```

---

## Exercise 3: Create a MenuItemViewSet (Medium)

In `menu/views.py`, create a `MenuItemViewSet`:

1. Use `ModelViewSet` as the base class
2. Set the queryset and serializer_class
3. Add a custom action `@action(detail=False)` called `available` that returns only available items
4. Add a custom action `@action(detail=True, methods=['post'])` called `toggle_availability` that toggles `is_available`

**Register the ViewSet in `menu/urls.py` using a router.**

---

## Exercise 4: Nested Serializer (Hard)

Create a `CategoryDetailSerializer` that includes all menu items in that category:

```python
class CategoryDetailSerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'items']
```

**Expected output:**
```json
{
    "id": 1,
    "name": "Main Course",
    "description": "Main dishes",
    "items": [
        {"id": 1, "name": "Pizza", "price": "12.99", ...},
        {"id": 2, "name": "Pasta", "price": "10.99", ...}
    ]
}
```

---

## Exercise 5: Order Status Workflow (Hard)

Implement a proper status workflow in `OrderSerializer.validate_status()`:

**Valid transitions:**
- `pending` → `confirmed` or `cancelled`
- `confirmed` → `preparing` or `cancelled`
- `preparing` → `ready` or `cancelled`
- `ready` → `delivered`
- `delivered` → (no changes allowed)
- `cancelled` → (no changes allowed)

**Hints:**
```python
VALID_TRANSITIONS = {
    'pending': ['confirmed', 'cancelled'],
    'confirmed': ['preparing', 'cancelled'],
    'preparing': ['ready', 'cancelled'],
    'ready': ['delivered'],
    'delivered': [],
    'cancelled': [],
}
```

---

## Exercise 6: Search and Filter (Medium)

Add filtering capabilities to `OrderViewSet`:

1. Install `django-filter`: `pip install django-filter`
2. Add `'django_filters'` to `INSTALLED_APPS`
3. Add filter backends to the ViewSet:

```python
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class OrderViewSet(viewsets.ModelViewSet):
    # ...
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['customer_name', 'customer_phone']
    ordering_fields = ['created_at', 'total_amount']
```

**Test:**
```bash
# Filter by status
curl "http://127.0.0.1:8000/api/orders/?status=pending"

# Search by customer name
curl "http://127.0.0.1:8000/api/orders/?search=john"

# Order by total_amount descending
curl "http://127.0.0.1:8000/api/orders/?ordering=-total_amount"
```

---

## Bonus Challenge: Write Tests

Create `orders/tests.py` with API tests:

```python
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Order


class OrderAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.order = Order.objects.create(
            customer_name="Test User",
            customer_phone="1234567890",
            total_amount=100.00
        )

    def test_list_orders(self):
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_order(self):
        data = {
            'customer_name': 'New User',
            'customer_phone': '9876543210',
            'total_amount': '50.00'
        }
        response = self.client.post('/api/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_phone_rejected(self):
        data = {
            'customer_name': 'Bad Phone',
            'customer_phone': '123',  # Too short!
            'total_amount': '50.00'
        }
        response = self.client.post('/api/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
```

**Run tests:**
```bash
python manage.py test orders
```

---

## Quick Reference

### Serializer Methods

| Method | Purpose |
|--------|---------|
| `validate_<field>(self, value)` | Validate single field |
| `validate(self, attrs)` | Cross-field validation |
| `create(self, validated_data)` | Custom create logic |
| `update(self, instance, validated_data)` | Custom update logic |

### ViewSet Actions

| Attribute | URL Pattern |
|-----------|-------------|
| `@action(detail=False)` | `/api/orders/action-name/` |
| `@action(detail=True)` | `/api/orders/{id}/action-name/` |

### HTTP Status Codes

| Code | Constant | Meaning |
|------|----------|---------|
| 200 | `HTTP_200_OK` | Success |
| 201 | `HTTP_201_CREATED` | Created |
| 204 | `HTTP_204_NO_CONTENT` | Deleted |
| 400 | `HTTP_400_BAD_REQUEST` | Validation error |
| 404 | `HTTP_404_NOT_FOUND` | Not found |

---

*Class 6 - REST Framework & Serializers*
