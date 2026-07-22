"""URL routes for the email service.

    /            -> a plain-text help page explaining how to poke the service
    /signup/     -> enqueue a welcome email and return JSON immediately
"""

from django.urls import path

from emails import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
]
