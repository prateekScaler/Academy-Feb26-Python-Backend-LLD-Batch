"""
URL map for the OAuth demo. Four URLs, that's the whole app.

    /                   -> home page (shows profile if signed in)
    /login/google/      -> kicks off the flow (redirects the browser to Google)
    /oauth/callback/    -> Google sends the browser back here with ?code=&state=
    /logout/            -> clears the session
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/google/", views.login_google, name="login_google"),
    path("oauth/callback/", views.oauth_callback, name="oauth_callback"),
    path("logout/", views.logout_view, name="logout"),
]
