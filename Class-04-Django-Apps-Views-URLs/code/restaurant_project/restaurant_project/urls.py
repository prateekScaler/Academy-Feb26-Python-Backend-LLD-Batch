# restaurant_project/urls.py
# Class 4: Main URL Router

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('menu/', include('menu.urls')),  # Delegate to menu app
]
