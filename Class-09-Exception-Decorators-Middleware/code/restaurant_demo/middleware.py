"""
Custom Middleware Examples
==========================
Middleware processes EVERY request/response globally.

Request flow:  TOP to BOTTOM through MIDDLEWARE list
Response flow: BOTTOM to TOP through MIDDLEWARE list

Think of it as layers of an onion - request goes in through outer layers,
response comes out through the same layers in reverse.
"""
import time
import logging
from django.conf import settings
from django.http import HttpResponse, JsonResponse

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """
    Logs every incoming request.

    Use Case: Debugging, monitoring, analytics
    This runs for ALL views automatically.
    """

    def __init__(self, get_response):
        # Called once when server starts
        self.get_response = get_response
        print("[RequestLoggingMiddleware] Initialized")

    def __call__(self, request):
        # BEFORE view executes
        print(f"[LOG] {request.method} {request.path}")

        # Call the next middleware or view
        response = self.get_response(request)

        # AFTER view executes
        print(f"[LOG] Response: {response.status_code}")

        return response


class RequestTimingMiddleware:
    """
    Measures how long each request takes.

    Use Case: Performance monitoring
    Adds X-Request-Time header to every response.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Start timer BEFORE view
        start_time = time.time()

        # Process request
        response = self.get_response(request)

        # Calculate duration AFTER view
        duration = time.time() - start_time
        duration_ms = duration * 1000

        # Add timing header to response
        response['X-Request-Time'] = f'{duration_ms:.2f}ms'
        print(f"[TIMING] {request.path}: {duration_ms:.2f}ms")

        return response


class MaintenanceModeMiddleware:
    """
    Blocks all requests when maintenance mode is enabled.

    Use Case: Deploying updates, database migrations
    Enable by setting MAINTENANCE_MODE = True in settings.py
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check maintenance flag BEFORE processing
        if getattr(settings, 'MAINTENANCE_MODE', False):
            # Allow admin access during maintenance
            if request.path.startswith('/admin/'):
                return self.get_response(request)

            # Block everyone else
            message = getattr(
                settings,
                'MAINTENANCE_MESSAGE',
                'Site is under maintenance.'
            )
            return HttpResponse(message, status=503)

        return self.get_response(request)


class JsonErrorMiddleware:
    """
    Converts HTML error responses to JSON for API clients.

    Use Case: REST APIs that need consistent JSON responses
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Optional hook: Called when view raises an exception.

        This is called BEFORE Django's default error handling.
        Return None to let Django handle it, or return a Response.
        """
        # Only for API endpoints
        if request.path.startswith('/menu/api/'):
            return JsonResponse({
                'error': str(exception),
                'type': type(exception).__name__
            }, status=500)

        # Let Django handle non-API errors
        return None


class IPBlockingMiddleware:
    """
    Blocks requests from specific IP addresses.

    Use Case: Security, rate limiting, blocking abusive users
    """

    BLOCKED_IPS = [
        # Add IPs to block here
        # '192.168.1.100',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get client IP
        ip = self.get_client_ip(request)

        if ip in self.BLOCKED_IPS:
            return HttpResponse('Forbidden', status=403)

        return self.get_response(request)

    def get_client_ip(self, request):
        """Extract client IP, handling proxy headers."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


# =============================================================================
# MIDDLEWARE VS DECORATOR - WHEN TO USE WHAT?
# =============================================================================
#
# USE MIDDLEWARE when:
# - You need to process ALL requests (logging, timing)
# - Global behavior (maintenance mode, security headers)
# - You need both request and response processing
#
# USE DECORATORS when:
# - You need behavior on SPECIFIC views only
# - Per-view configuration (permissions, rate limits)
# - The logic is view-specific
#
# Example:
# - Log all requests → Middleware (global)
# - Require login for /admin/ → Decorator (@login_required)
# - Add security headers → Middleware (global)
# - Rate limit one expensive API → Decorator
# =============================================================================
