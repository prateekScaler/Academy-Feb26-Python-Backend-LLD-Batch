"""
URL routes for the JWT demo.

Five endpoints. Two of them we wrote; two of them SimpleJWT gave us for free.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from config.views import MeView, PublicView, RegisterView

urlpatterns = [
    # --- Sign up -----------------------------------------------------------
    # POST {"username": "...", "password": "..."} -> 201 {"id", "username"}
    # Open to anonymous callers. Creating an account is not logging in, so this
    # returns no tokens.
    path("api/register/", RegisterView.as_view(), name="register"),

    # --- Log in (get tokens) ----------------------------------------------
    # POST {"username": "...", "password": "..."} -> 200 {"access", "refresh"}
    # We did not write this view. TokenObtainPairView ships with SimpleJWT: it
    # checks the credentials against the User table and mints the token pair.
    # Wrong credentials -> 401.
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),

    # --- Get a fresh access token -----------------------------------------
    # POST {"refresh": "..."} -> 200 {"access", "refresh"}
    # Also from SimpleJWT. The client calls this when its access token expires,
    # so the user is not forced to re-enter a password every 15 minutes.
    # (It returns a new "refresh" too, because ROTATE_REFRESH_TOKENS is True.)
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # --- Protected resource ------------------------------------------------
    # GET with `Authorization: Bearer <access>` -> 200 {"id", "username"}
    # GET without that header                   -> 401
    path("api/me/", MeView.as_view(), name="me"),

    # --- Unprotected resource, for comparison ------------------------------
    # GET -> 200, header or no header. AllowAny.
    path("api/public/", PublicView.as_view(), name="public"),
]
