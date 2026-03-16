from django.db import models

# Create your models here.
class TimestampedModel(models.Model):
    """
    Abstract base model that provides created_at and updated_at fields.
    Other models can inherit from this to automatically get these timestamp fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
