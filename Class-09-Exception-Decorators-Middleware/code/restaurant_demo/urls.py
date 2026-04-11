"""
URL configuration for restaurant_demo project.
Class 9: Exception Handling, Decorators & Middleware Demo
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('menu/', include('menu.urls')),
]
