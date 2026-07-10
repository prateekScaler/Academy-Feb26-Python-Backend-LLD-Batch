from django.conf import settings
from django.db import models


class Event(models.Model):
    title = models.CharField(max_length=128)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="events"
    )


class Order(models.Model):
    cart_id = models.IntegerField()
    amount_paise = models.IntegerField()
    receipt = models.CharField(max_length=64)
    status = models.CharField(max_length=16, default="PENDING")
