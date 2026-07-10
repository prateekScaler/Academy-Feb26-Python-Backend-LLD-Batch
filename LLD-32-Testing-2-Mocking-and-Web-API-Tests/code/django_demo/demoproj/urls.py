from django.urls import path, include
from rest_framework.routers import SimpleRouter
from demoapp.views import EventViewSet, checkout

router = SimpleRouter()
router.register("events", EventViewSet, basename="event")

urlpatterns = [
    path("api/", include(router.urls)),
    path("api/checkout/", checkout, name="checkout"),
]
