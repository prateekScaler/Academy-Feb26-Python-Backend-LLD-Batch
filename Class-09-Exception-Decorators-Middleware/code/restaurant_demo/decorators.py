"""
Custom Decorator Examples
=========================
Decorators wrap functions to add behavior before/after execution.

Basic structure:
    @my_decorator
    def my_view(request):
        ...

Is equivalent to:
    my_view = my_decorator(my_view)
"""
import functools
import time
from django.http import HttpResponse, JsonResponse


# =============================================================================
# BASIC DECORATOR TEMPLATE
# =============================================================================

def basic_decorator(func):
    """
    Template for creating decorators.

    @functools.wraps preserves the original function's:
    - __name__
    - __doc__
    - Other metadata

    Without it, debugging becomes confusing because all decorated
    functions would appear to have the same name.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Code BEFORE the function runs
        print(f"Before {func.__name__}")

        # Call the original function
        result = func(*args, **kwargs)

        # Code AFTER the function runs
        print(f"After {func.__name__}")

        return result
    return wrapper


# =============================================================================
# PRACTICAL DECORATORS FOR DJANGO VIEWS
# =============================================================================

def timing_decorator(func):
    """
    Measures execution time of a view.

    Usage:
        @timing_decorator
        def my_view(request):
            ...
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"[TIMING] {func.__name__}: {duration*1000:.2f}ms")
        return result
    return wrapper


def require_json(func):
    """
    Ensures request has JSON content type.

    Usage:
        @require_json
        @api_view(['POST'])
        def create_item(request):
            ...
    """
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        content_type = request.content_type
        if 'application/json' not in content_type:
            return JsonResponse(
                {'error': 'Content-Type must be application/json'},
                status=400
            )
        return func(request, *args, **kwargs)
    return wrapper


def log_request(func):
    """
    Logs request details before processing.

    Usage:
        @log_request
        def my_view(request):
            ...
    """
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        print(f"[REQUEST] {request.method} {request.path}")
        print(f"[REQUEST] User: {request.user}")
        print(f"[REQUEST] Args: {args}, Kwargs: {kwargs}")
        return func(request, *args, **kwargs)
    return wrapper


# =============================================================================
# DECORATOR WITH ARGUMENTS (3-LEVEL NESTING)
# =============================================================================

def rate_limit(max_calls, period_seconds):
    """
    Simple rate limiting decorator (demo - not production ready).

    Usage:
        @rate_limit(max_calls=5, period_seconds=60)
        def expensive_view(request):
            ...

    This has THREE levels of nesting:
    1. rate_limit(max_calls, period_seconds) - receives config
    2. decorator(func) - receives the function
    3. wrapper(*args, **kwargs) - receives function arguments
    """
    # Track calls per IP (in-memory, not production ready)
    call_history = {}

    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            # Get client IP
            ip = request.META.get('REMOTE_ADDR', 'unknown')
            current_time = time.time()

            # Initialize or clean old entries
            if ip not in call_history:
                call_history[ip] = []

            # Remove calls outside the period
            call_history[ip] = [
                t for t in call_history[ip]
                if current_time - t < period_seconds
            ]

            # Check rate limit
            if len(call_history[ip]) >= max_calls:
                return JsonResponse(
                    {'error': f'Rate limit exceeded. Max {max_calls} calls per {period_seconds}s'},
                    status=429
                )

            # Record this call
            call_history[ip].append(current_time)

            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_role(role_name):
    """
    Requires user to have a specific role/group.

    Usage:
        @require_role('admin')
        def admin_only_view(request):
            ...

    Three levels:
    1. require_role('admin') - receives the role name
    2. decorator(func) - receives the function
    3. wrapper(request, ...) - receives the request
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)

            # Check if user is in the required group
            if not request.user.groups.filter(name=role_name).exists():
                return JsonResponse(
                    {'error': f'Role "{role_name}" required'},
                    status=403
                )

            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def cache_response(timeout_seconds):
    """
    Simple response caching decorator.

    Usage:
        @cache_response(300)  # Cache for 5 minutes
        def expensive_api(request):
            ...

    Note: This is a simplified demo. Production caching should use
    Django's cache framework or Redis.
    """
    cache = {}

    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            # Create cache key from path and query string
            cache_key = f"{request.path}?{request.GET.urlencode()}"
            current_time = time.time()

            # Check cache
            if cache_key in cache:
                cached_response, cached_time = cache[cache_key]
                if current_time - cached_time < timeout_seconds:
                    print(f"[CACHE HIT] {cache_key}")
                    return cached_response

            # Cache miss - call the function
            print(f"[CACHE MISS] {cache_key}")
            response = func(request, *args, **kwargs)

            # Store in cache
            cache[cache_key] = (response, current_time)

            return response
        return wrapper
    return decorator


# =============================================================================
# STACKING DECORATORS
# =============================================================================
#
# Decorators are applied bottom-to-top, executed top-to-bottom:
#
#     @log_request        # Executes 1st (outermost)
#     @timing_decorator   # Executes 2nd
#     @require_json       # Executes 3rd (innermost)
#     def my_view(request):
#         ...
#
# The above is equivalent to:
#     my_view = log_request(timing_decorator(require_json(my_view)))
#
# Execution order:
# 1. log_request's BEFORE code
# 2. timing_decorator's BEFORE code
# 3. require_json's BEFORE code
# 4. my_view() executes
# 5. require_json's AFTER code
# 6. timing_decorator's AFTER code
# 7. log_request's AFTER code
# =============================================================================
