# Class 15: Hands-On Guide — Redis Caching for the Restaurant API

> Step-by-step guide to add Redis caching to the restaurant project. By the end, your menu API responds in ~3ms instead of ~45ms for cached requests.

---

## Step 1: Install Redis

### macOS

```bash
brew install redis
brew services start redis

# Verify it's running
redis-cli ping
# → PONG
```

### Ubuntu/Debian

```bash
sudo apt install redis-server
sudo systemctl start redis

redis-cli ping
# → PONG
```

### Quick Redis Tour

```bash
redis-cli

# Set a key
SET greeting "hello"

# Get it back
GET greeting
# → "hello"

# Set with expiry (10 seconds)
SET temp_key "I disappear" EX 10

# Check TTL
TTL temp_key
# → 8 (seconds remaining)

# Wait 10 seconds...
GET temp_key
# → (nil) — gone!

# Exit
quit
```

---

## Step 2: Install Django Packages

```bash
cd /Users/prateek/Desktop/scaler/restaurant_project
source venv/bin/activate

pip install django-redis redis
```

---

## Step 3: Configure Cache Backend in settings.py

Add to `restaurant_project/settings.py`:

```python
# ── Cache Configuration ──────────────────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'TIMEOUT': 300,  # Default TTL: 5 minutes
    }
}
```

Verify it works:

```bash
python manage.py shell
```

```python
from django.core.cache import cache

# Write to cache
cache.set('test_key', 'hello from redis!', timeout=60)

# Read from cache
print(cache.get('test_key'))
# → "hello from redis!"

# Check it's in Redis
exit()
```

```bash
redis-cli -n 1 KEYS '*'
# → Should show your test_key
```

---

## Step 4: Measure Before Caching

Start the server and measure baseline response time:

```bash
python manage.py runserver
```

```bash
# Measure response time (run a few times)
time curl -s http://127.0.0.1:8000/menu/items/ > /dev/null

# Or more precisely with curl's timing:
curl -o /dev/null -s -w "Total: %{time_total}s\n" http://127.0.0.1:8000/menu/items/
```

Note down the average time. Should be around 30-50ms.

---

## Step 5: Add Per-View Cache (Simplest Approach)

Update `menu/views.py`:

```python
from rest_framework import generics, filters
from rest_framework.pagination import PageNumberPagination
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import MenuItem
from .serializers import MenuItemSerializer


class MenuPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'size'
    max_page_size = 100


class MenuItemListView(generics.ListAPIView):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    pagination_class = MenuPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']

    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
```

Test:

```bash
# First request — cache MISS (hits DB)
curl -o /dev/null -s -w "Request 1 (miss): %{time_total}s\n" http://127.0.0.1:8000/menu/items/

# Second request — cache HIT
curl -o /dev/null -s -w "Request 2 (hit):  %{time_total}s\n" http://127.0.0.1:8000/menu/items/

# Different page — separate cache entry
curl -o /dev/null -s -w "Page 2 (miss):    %{time_total}s\n" "http://127.0.0.1:8000/menu/items/?page=2"

# Same page again — HIT
curl -o /dev/null -s -w "Page 2 (hit):     %{time_total}s\n" "http://127.0.0.1:8000/menu/items/?page=2"
```

Check Redis:

```bash
redis-cli -n 1 KEYS '*'
# → Shows cache keys for each unique URL
```

---

## Step 6: Manual Cache with Custom Keys (More Control)

Replace the `list` method with manual caching:

```python
from django.core.cache import cache
from rest_framework.response import Response


class MenuItemListView(generics.ListAPIView):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    pagination_class = MenuPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']

    def list(self, request, *args, **kwargs):
        # Build cache key from query params
        cache_key = f"menu_items:{request.GET.urlencode()}"

        # Check cache
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        # Cache miss — get from DB
        response = super().list(request, *args, **kwargs)

        # Store in cache for 5 minutes
        cache.set(cache_key, response.data, timeout=300)

        return response
```

Test:

```bash
# Miss → Hit
curl -o /dev/null -s -w "Miss: %{time_total}s\n" http://127.0.0.1:8000/menu/items/
curl -o /dev/null -s -w "Hit:  %{time_total}s\n" http://127.0.0.1:8000/menu/items/

# Search — different cache key
curl -o /dev/null -s -w "Search miss: %{time_total}s\n" "http://127.0.0.1:8000/menu/items/?search=chicken"
curl -o /dev/null -s -w "Search hit:  %{time_total}s\n" "http://127.0.0.1:8000/menu/items/?search=chicken"
```

Inspect in Redis:

```bash
redis-cli -n 1
> KEYS *menu*
> GET "menu_items:"              # Default page (no params)
> GET "menu_items:search=chicken"  # Search results
> TTL "menu_items:"              # Seconds until expiry
```

---

## Step 7: Cache Invalidation

When a menu item is updated, the cache should be cleared. Add a helper:

Create `menu/cache_utils.py`:

```python
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


def invalidate_menu_cache():
    """Clear all menu-related cache entries."""
    # Option 1: Delete specific keys (if you know them)
    # cache.delete('menu_items:')

    # Option 2: Use key pattern with django-redis
    from django_redis import get_redis_connection
    conn = get_redis_connection('default')
    keys = conn.keys('*menu_items*')
    if keys:
        conn.delete(*keys)
        logger.info(f"Invalidated {len(keys)} menu cache entries")
```

Call it whenever menu data changes:

```python
# In admin, signals, or an update view:
from menu.cache_utils import invalidate_menu_cache

# After updating a menu item:
item.save()
invalidate_menu_cache()
```

---

## Step 8: Verify the Full Flow

```bash
# 1. Start fresh — clear cache
redis-cli -n 1 FLUSHDB

# 2. First request — MISS, hits DB
curl -o /dev/null -s -w "Miss: %{time_total}s\n" http://127.0.0.1:8000/menu/items/

# 3. Second request — HIT, from cache
curl -o /dev/null -s -w "Hit:  %{time_total}s\n" http://127.0.0.1:8000/menu/items/

# 4. Check Redis has the data
redis-cli -n 1 KEYS '*menu*'

# 5. Clear cache (simulate menu update)
redis-cli -n 1 FLUSHDB

# 6. Next request — MISS again (cache was cleared)
curl -o /dev/null -s -w "After invalidation: %{time_total}s\n" http://127.0.0.1:8000/menu/items/
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ConnectionRefusedError: redis://127.0.0.1:6379` | Redis isn't running. Start it: `brew services start redis` or `sudo systemctl start redis` |
| `ModuleNotFoundError: No module named 'django_redis'` | `pip install django-redis` |
| Cache not working (always misses) | Check `CACHES` is in settings.py and Redis is running (`redis-cli ping`) |
| Cache returns stale data | Lower the TTL or call `invalidate_menu_cache()` on updates |
| `WRONGTYPE Operation against a key` | You're mixing Redis data types on the same key. Run `FLUSHDB` to reset |

---

## Final File Structure

```
restaurant_project/
├── restaurant_project/
│   └── settings.py          ← CACHES config added
└── menu/
    ├── views.py             ← cache_page or manual cache added
    └── cache_utils.py       ← NEW: invalidation helper
```
