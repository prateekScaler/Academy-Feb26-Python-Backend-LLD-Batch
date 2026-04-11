# Class 14: Pagination, Searching & Sorting

> Your API returns 10,000 menu items. The mobile app takes 8 seconds to load. Users leave. Learn how to return data in **pages**, let users **search** efficiently, and **sort** results — the way every production API works.

---

## Recap Quiz (Classes 12-13 Fundamentals)

**Q1: Your webhook handler processes a payment and returns 200 OK. Razorpay sends the same webhook again due to a network glitch. What prevents double-processing?**

<details>
<summary>Answer</summary>

**Idempotency.** Store each webhook's `event_id` in a `WebhookEvent` table. Before processing, check: "Have I seen this `event_id` before?" If yes, return 200 and skip.
</details>

---

**Q2: Your reconciliation cron runs every hour. A customer pays at 10:05 AM but the webhook fails. When is the earliest their order gets updated?**

<details>
<summary>Answer</summary>

The 11:00 AM cron checks payments older than 1 hour, so the 10:05 AM payment won't qualify until after 11:05 AM. The **12:00 PM** cron run catches it. This is why webhooks are primary — reconciliation is the safety net, not the fast path.
</details>

---

**Q3: Why do we wrap webhook processing in `transaction.atomic()`?**

<details>
<summary>Answer</summary>

To ensure **all-or-nothing** updates. If updating the payment succeeds but updating the order fails, the transaction rolls back everything — no partial state where payment says "paid" but order says "pending".
</details>

---

**Q4: You have 50,000 menu items in your database. A customer opens the menu page. Your API returns ALL 50,000 items in one response. What problems does this cause?**

<details>
<summary>Answer</summary>

- **Slow response** — serializing 50K items takes seconds
- **High memory usage** — server loads all 50K objects into RAM
- **Network bandwidth** — response is megabytes, mobile users on slow connections suffer
- **Bad UX** — browser/app freezes rendering 50K items
- **Database strain** — `SELECT * FROM menu_items` with no LIMIT is expensive

**Solution: Pagination** — return 20 items per page, let the client request more pages as needed.
</details>

---

## Section 1: The Problem — Why APIs Need Pagination

### What Happens Without Pagination

```python
# BAD: Returns ALL items
def list_menu_items(request):
    items = MenuItem.objects.all()       # Loads 50,000 objects into memory
    data = serialize_all(items)          # Serializes all of them
    return JsonResponse(data)            # Sends a 5MB response
```

```
Client Request:  GET /menu/items/
Response Size:   5.2 MB
Response Time:   4.3 seconds
Memory Used:     180 MB on server
```

### What Happens With Pagination

```python
# GOOD: Returns 20 items per page
def list_menu_items(request):
    page = request.GET.get('page', 1)
    items = MenuItem.objects.all()[(page-1)*20 : page*20]  # Only 20 items
    return JsonResponse(serialize(items))
```

```
Client Request:  GET /menu/items/?page=1
Response Size:   4.8 KB
Response Time:   45 ms
Memory Used:     2 MB on server
```

> **Every major API uses pagination:** Google Search (10 results per page), Twitter/X feed (20 tweets per load), Amazon products (48 per page), GitHub repos (30 per page).

---

## Section 2: Types of Pagination

### 1. Offset-Based (Page Number) Pagination

The most common and easiest to understand. Client sends a page number.

```
GET /menu/items/?page=1          → Items 1-20
GET /menu/items/?page=2          → Items 21-40
GET /menu/items/?page=3          → Items 41-60
```

**SQL under the hood:**
```sql
SELECT * FROM menu_items LIMIT 20 OFFSET 0;    -- page 1
SELECT * FROM menu_items LIMIT 20 OFFSET 20;   -- page 2
SELECT * FROM menu_items LIMIT 20 OFFSET 40;   -- page 3
```

**Pros:**
- Simple to implement
- User can jump to any page (page 1, page 50, page 100)
- Total count and page numbers are easy to show

**Cons:**
- **Slow on large offsets** — `OFFSET 100000` makes the DB scan and skip 100K rows
- **Inconsistent results** — if a new item is inserted while user is on page 2, page 3 might show a duplicate

> **When to use:** Admin dashboards, back-office tools, any UI with page numbers (1, 2, 3...).

### 2. Cursor-Based Pagination

Instead of page numbers, use a "cursor" — typically the ID or timestamp of the last item on the current page.

```
GET /menu/items/                          → Items 1-20, next_cursor=item_20_id
GET /menu/items/?cursor=item_20_id        → Items 21-40, next_cursor=item_40_id
GET /menu/items/?cursor=item_40_id        → Items 41-60, next_cursor=item_60_id
```

**SQL under the hood:**
```sql
SELECT * FROM menu_items WHERE id > 20 ORDER BY id LIMIT 20;   -- after cursor 20
SELECT * FROM menu_items WHERE id > 40 ORDER BY id LIMIT 20;   -- after cursor 40
```

**Pros:**
- **Fast at any depth** — no scanning/skipping, just a WHERE clause on an indexed column
- **Consistent results** — new inserts don't cause duplicates or missing items

**Cons:**
- Can't jump to page 50 — must scroll through pages sequentially
- Slightly more complex to implement

> **When to use:** Infinite scroll feeds (Instagram, Twitter), mobile apps, real-time data. This is what most modern APIs use.

### 3. Limit-Offset Pagination

Variation of offset-based where client controls the page size.

```
GET /menu/items/?limit=10&offset=0       → Items 1-10
GET /menu/items/?limit=10&offset=10      → Items 11-20
GET /menu/items/?limit=50&offset=100     → Items 101-150
```

> **When to use:** APIs where the client needs control over page size (data tables, analytics dashboards).

### Comparison

| | Offset (Page Number) | Cursor-Based | Limit-Offset |
|---|---|---|---|
| Jump to page N? | Yes | No | Yes |
| Performance at depth | Degrades | Constant | Degrades |
| Consistent results? | No (items shift) | Yes | No |
| Implementation | Simple | Moderate | Simple |
| Best for | Admin pages | Feeds, mobile apps | Flexible APIs |

---

## Section 3: Implementing Pagination in Django REST Framework

DRF has built-in pagination classes. You configure them globally or per-view.

### Global Configuration (settings.py)

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

This automatically paginates **every** list view. Response format:

```json
{
    "count": 152,
    "next": "http://localhost:8000/menu/items/?page=2",
    "previous": null,
    "results": [
        {"id": 1, "name": "Butter Chicken", "price": 350},
        {"id": 2, "name": "Paneer Tikka", "price": 280},
        ...
    ]
}
```

### Per-View Pagination (Override Defaults)

```python
from rest_framework.pagination import PageNumberPagination

class MenuPagination(PageNumberPagination):
    page_size = 10                   # Default items per page
    page_size_query_param = 'size'   # Client can override: ?size=50
    max_page_size = 100              # Cap it — don't let client request 10,000

class MenuItemListView(generics.ListAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    pagination_class = MenuPagination
```

```
GET /menu/items/              → 10 items (default)
GET /menu/items/?size=50      → 50 items
GET /menu/items/?size=999     → 100 items (capped at max_page_size)
GET /menu/items/?page=3       → Page 3 (items 21-30)
```

### Cursor Pagination

```python
from rest_framework.pagination import CursorPagination

class MenuCursorPagination(CursorPagination):
    page_size = 20
    ordering = '-created_at'     # Must be a unique, sequential field

class MenuItemListView(generics.ListAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    pagination_class = MenuCursorPagination
```

Response includes opaque cursor strings (not page numbers):
```json
{
    "next": "http://localhost:8000/menu/items/?cursor=cD0yMDI0LTA0LTA0",
    "previous": null,
    "results": [...]
}
```

### Limit-Offset Pagination

```python
from rest_framework.pagination import LimitOffsetPagination

class MenuLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100

class MenuItemListView(generics.ListAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    pagination_class = MenuLimitOffsetPagination
```

```
GET /menu/items/?limit=10&offset=30   → Items 31-40
```

---

## Section 4: Searching

### The Problem

```
GET /menu/items/                 → All items
GET /menu/items/?search=chicken  → Only items containing "chicken"
```

Without search, the client downloads everything and filters locally — wasteful.

### Django ORM: How Searching Works Under the Hood

```python
# Case-insensitive contains (LIKE '%chicken%')
MenuItem.objects.filter(name__icontains='chicken')

# Search multiple fields
from django.db.models import Q
MenuItem.objects.filter(
    Q(name__icontains='chicken') | Q(description__icontains='chicken')
)

# Starts with
MenuItem.objects.filter(name__istartswith='butter')

# Exact match
MenuItem.objects.filter(category__name='Main Course')
```

**SQL generated:**
```sql
SELECT * FROM menu_items
WHERE LOWER(name) LIKE '%chicken%'
   OR LOWER(description) LIKE '%chicken%';
```

### DRF SearchFilter (The Easy Way)

```python
from rest_framework import filters

class MenuItemListView(generics.ListAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'category__name']
```

Now clients can search:
```
GET /menu/items/?search=chicken         → Searches name, description, category
GET /menu/items/?search=butter chicken  → Items matching "butter" OR "chicken"
```

### Search Field Prefixes

DRF supports special prefixes to control how search works:

| Prefix | Lookup | Example | SQL |
|--------|--------|---------|-----|
| (none) | `icontains` | `search_fields = ['name']` | `WHERE name ILIKE '%query%'` |
| `^` | `istartswith` | `search_fields = ['^name']` | `WHERE name ILIKE 'query%'` |
| `=` | `iexact` | `search_fields = ['=status']` | `WHERE status ILIKE 'query'` |
| `@` | Full-text search | `search_fields = ['@description']` | Uses DB full-text index |

```python
class MenuItemListView(generics.ListAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'name',              # contains — "chicken" matches "Butter Chicken"
        '^name',             # starts with — "butter" matches "Butter Chicken"
        'description',       # contains
        'category__name',    # search across related model
    ]
```

### Performance: Why LIKE '%query%' is Slow

```sql
-- This can't use an index — must scan every row
SELECT * FROM menu_items WHERE name LIKE '%chicken%';

-- This CAN use an index (prefix match)
SELECT * FROM menu_items WHERE name LIKE 'chicken%';
```

`%chicken%` (contains) forces a **full table scan** — the DB checks every row. Fine for 1,000 items. Terrible for 1,000,000.

**Solutions for large datasets:**
- **Database indexes** for prefix searches (`istartswith`)
- **Full-text search** (PostgreSQL `SearchVector`, MySQL `FULLTEXT`)
- **Search engines** (Elasticsearch, Meilisearch) for complex search needs
- **Trigram indexes** (PostgreSQL `pg_trgm`) for fast `LIKE '%query%'`

For our restaurant project with hundreds of items, `icontains` is perfectly fine.

---

## Section 5: Sorting

### The Problem

```
GET /menu/items/                      → Random order? Alphabetical? By price?
GET /menu/items/?ordering=price       → Cheapest first
GET /menu/items/?ordering=-price      → Most expensive first
```

Without explicit sorting, the DB returns rows in **insertion order** (or whatever the optimizer decides). This is unpredictable.

### Django ORM: Sorting Under the Hood

```python
# Ascending (A-Z, low to high)
MenuItem.objects.order_by('price')

# Descending (Z-A, high to low)
MenuItem.objects.order_by('-price')

# Multiple fields (sort by category, then by price within each category)
MenuItem.objects.order_by('category__name', '-price')

# Default ordering in the model
class MenuItem(models.Model):
    class Meta:
        ordering = ['-created_at']  # Newest first by default
```

**SQL generated:**
```sql
SELECT * FROM menu_items ORDER BY price ASC;
SELECT * FROM menu_items ORDER BY price DESC;
SELECT * FROM menu_items ORDER BY category_name ASC, price DESC;
```

### DRF OrderingFilter (The Easy Way)

```python
from rest_framework import filters

class MenuItemListView(generics.ListAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['name', 'price', 'created_at', 'category__name']
    ordering = ['-created_at']   # Default ordering
```

Now clients can sort:
```
GET /menu/items/                          → Default: newest first
GET /menu/items/?ordering=price           → Cheapest first
GET /menu/items/?ordering=-price          → Most expensive first
GET /menu/items/?ordering=name            → A-Z
GET /menu/items/?ordering=-name           → Z-A
GET /menu/items/?ordering=category__name,price  → By category, then price
```

> **Security: Always whitelist `ordering_fields`.** Without it, DRF allows ordering by *any* field — including sensitive ones. A malicious user could figure out field names via error messages.

### Combining Search + Sort + Pagination

```python
from rest_framework import filters, generics
from rest_framework.pagination import PageNumberPagination

class MenuPagination(PageNumberPagination):
    page_size = 20
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
```

Now all three work together:
```
GET /menu/items/?search=chicken&ordering=-price&page=1&size=10
```
→ Search for "chicken", sort by price (most expensive first), page 1, 10 items per page.

---

## Section 6: Filtering (Bonus — Beyond Search)

Search is text-based (`?search=chicken`). **Filtering** is field-based:

```
GET /menu/items/?category=Main Course&is_vegetarian=true&price_min=100&price_max=500
```

### DRF django-filter

```bash
pip install django-filter
```

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}
```

```python
import django_filters
from menu.models import MenuItem

class MenuItemFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = django_filters.CharFilter(field_name='category__name', lookup_expr='iexact')

    class Meta:
        model = MenuItem
        fields = ['is_available', 'category']

class MenuItemListView(generics.ListAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filterset_class = MenuItemFilter
```

```
GET /menu/items/?category=Main Course              → Only main courses
GET /menu/items/?price_min=100&price_max=300        → Items Rs.100-300
GET /menu/items/?is_available=true                  → Only available items
GET /menu/items/?category=Dessert&ordering=-price   → Desserts, expensive first
```

---

## Section 7: Performance Considerations

### Database Indexes

Sorting and filtering are only fast if the database has **indexes** on those columns.

```python
class MenuItem(models.Model):
    name = models.CharField(max_length=200, db_index=True)    # Index for searching
    price = models.DecimalField(..., db_index=True)           # Index for sorting/filtering
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Index for sorting

    class Meta:
        indexes = [
            models.Index(fields=['category', 'price']),  # Composite index
            models.Index(fields=['-created_at']),         # Descending index
        ]
```

**SQL without index:**
```sql
SELECT * FROM menu_items ORDER BY price;
-- Full table scan → sorts ALL rows → returns 20
-- Time: 850ms (on 1M rows)
```

**SQL with index:**
```sql
SELECT * FROM menu_items ORDER BY price;
-- Reads index (already sorted) → returns 20
-- Time: 2ms (on 1M rows)
```

### The N+1 Problem with Pagination

```python
# BAD: N+1 queries
items = MenuItem.objects.all()[:20]
for item in items:
    print(item.category.name)  # 1 extra query PER item = 21 queries

# GOOD: Select related
items = MenuItem.objects.select_related('category').all()[:20]
# 1 query with JOIN = 1 query total
```

**Always use `select_related()` / `prefetch_related()` with paginated views.**

### Count Queries

Offset pagination requires knowing the total count:
```sql
SELECT COUNT(*) FROM menu_items;   -- Can be SLOW on large tables
SELECT * FROM menu_items LIMIT 20 OFFSET 0;
```

For tables with millions of rows, consider:
- Cursor pagination (no count needed)
- Caching the count (update periodically)
- Approximate count (`EXPLAIN` trick in PostgreSQL)

---

## Key Takeaways

1. **Always paginate list endpoints** — never return unbounded result sets
2. **Offset pagination** for admin/dashboards, **cursor pagination** for feeds/mobile
3. **SearchFilter** for text search, **OrderingFilter** for sorting — both built into DRF
4. **Whitelist fields** — always specify `search_fields` and `ordering_fields`
5. **Add database indexes** on columns you search, sort, or filter by
6. **Use `select_related`/`prefetch_related`** — pagination doesn't fix N+1
7. **Combine them all:** `?search=chicken&ordering=-price&page=1&size=10`

---

## Real-World Examples

| API | Pagination | Search | Sort |
|-----|-----------|--------|------|
| GitHub | Page number (`?page=2&per_page=30`) | `?q=django+language:python` | `?sort=stars&order=desc` |
| Stripe | Cursor (`?starting_after=ch_xxx`) | `?query=customer@email.com` | `?created[gte]=timestamp` |
| Shopify | Cursor (`?page_info=xxx`) | Title, vendor, product_type | `?sort_key=PRICE` |
| Razorpay | Offset (`?skip=10&count=10`) | N/A (filter by status, etc.) | `?from=timestamp&to=timestamp` |

---

## Further Reading: Circuit Breaker Pattern

When your Django app calls external services (Razorpay API, Elasticsearch, third-party APIs), those services can go down. Without protection, your app keeps sending requests to a dead service — burning threads, timing out, and eventually crashing itself.

The **Circuit Breaker pattern** prevents this:
- **Closed** (normal) — requests flow through
- **Open** (service is down) — requests fail immediately without waiting, return a fallback
- **Half-Open** (testing recovery) — allow one request through to check if service is back

```
Normal: App ──→ Razorpay API ──→ Response ✓

Service down (without circuit breaker):
App ──→ Razorpay ──→ 30s timeout ──→ App hangs ──→ All requests pile up ──→ App crashes

Service down (with circuit breaker):
App ──→ Circuit Breaker says "OPEN, don't even try" ──→ Instant fallback ──→ App stays healthy
```

In Django, you can implement this with the [`pybreaker`](https://github.com/danielfm/pybreaker) library or build a simple version with Redis counters. This is especially relevant for payment reconciliation crons — if Razorpay's API is down, the circuit breaker stops the cron from hammering it.

---

## Resources

- [DRF Pagination Docs](https://www.django-rest-framework.org/api-guide/pagination/)
- [DRF Filtering Docs](https://www.django-rest-framework.org/api-guide/filtering/)
- [django-filter Documentation](https://django-filter.readthedocs.io/)
- [Use The Index, Luke — SQL Indexing Guide](https://use-the-index-luke.com/)
- [Slack Engineering: Evolving API Pagination at Slack](https://slack.engineering/evolving-api-pagination-at-slack/)
- [Circuit Breaker Pattern — Martin Fowler](https://martinfowler.com/bliki/CircuitBreaker.html)
- [pybreaker — Circuit Breaker for Python](https://github.com/danielfm/pybreaker)

---

*For the hands-on implementation guide, see [HANDS-ON-GUIDE.md](HANDS-ON-GUIDE.md)*
