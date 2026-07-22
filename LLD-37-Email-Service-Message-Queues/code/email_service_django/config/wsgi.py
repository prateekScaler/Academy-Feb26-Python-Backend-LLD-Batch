"""WSGI entry point (used by production servers like gunicorn/uwsgi).

Not needed for the demo -- `runserver` uses this indirectly -- but included so
the project layout is complete and realistic.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
