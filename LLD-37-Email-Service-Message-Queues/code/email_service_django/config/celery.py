"""
The Celery application object.

This is the bridge between Django and Celery. When you run

    celery -A config worker -l info
                 ^^^^^^
`-A config` tells Celery to import THIS package (config) and find a Celery app
in it -- which config/__init__.py re-exports as `celery_app`.
"""

import os

from celery import Celery

# Celery needs to know Django's settings too (so tasks can use the ORM, the
# email backend, etc.). Same DJANGO_SETTINGS_MODULE Django itself uses.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# The Celery app. The name is just a label that shows up in logs.
app = Celery("email_service")

# Pull all Celery config from Django settings. `namespace="CELERY"` means Celery
# only looks at settings that start with CELERY_ (e.g. CELERY_BROKER_URL ->
# broker_url). This keeps Celery and Django config in ONE place (settings.py).
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover a `tasks.py` in every app listed in INSTALLED_APPS. This is how
# `@shared_task` in emails/tasks.py gets registered without importing it by hand.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """A trivial task to confirm the worker is wired up: `debug_task.delay()`."""
    print(f"Celery is alive. Request: {self.request!r}")
