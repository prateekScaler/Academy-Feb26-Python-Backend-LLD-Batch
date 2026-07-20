"""URL routing: which path maps to which view function."""
from django.urls import path

from . import views

urlpatterns = [
    # The demo page with the form and the fetch button.
    path("", views.index, name="index"),

    # POST target for the HTML form. Protected by CsrfViewMiddleware.
    path("submit/", views.submit, name="submit"),

    # Small JSON endpoint. Fetch it from this page (same origin) and from a
    # page served on another origin to see CORS in action.
    path("api/ping/", views.api_ping, name="api_ping"),

    # Deliberately unprotected, for contrast. See the warning in views.py.
    path("api/unsafe-submit/", views.unsafe_submit, name="unsafe_submit"),
]
