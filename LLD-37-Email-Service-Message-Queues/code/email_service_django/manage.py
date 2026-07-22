#!/usr/bin/env python
"""Django's command-line utility for administrative tasks.

Common commands for this demo:
    python manage.py makemigrations       # (already committed, safe to re-run)
    python manage.py migrate              # create the SQLite tables
    python manage.py runserver            # serves on 8000 (the web/producer side)

The Celery WORKER is started separately (see README):
    celery -A config worker -l info
"""
import os
import sys


def main():
    # Point Django at our settings module.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and available "
            "on your PYTHONPATH? Did you forget to activate a virtualenv?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
