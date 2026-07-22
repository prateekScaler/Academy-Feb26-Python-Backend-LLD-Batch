"""
Make sure the Celery app is created and imported when Django starts.

This import is what lets `@shared_task` (in emails/tasks.py) attach itself to the
one shared Celery app. Without it, tasks might not be registered with the worker.
"""

from .celery import app as celery_app

__all__ = ("celery_app",)
