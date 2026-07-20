#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Each demo in this class gets its own port so all three can run side by side
# during the session -- no "That port is already in use" mid-demo. A bare
# `python manage.py runserver` lands here (Login with Google); pass a port
# explicitly (`runserver 9000`) and that still wins.
#
# This one deliberately stays on Django's default 8000: the redirect URI
# http://127.0.0.1:8000/oauth/callback/ is what is registered in Google Cloud
# Console, and Google matches it character for character. Change this port and
# you must add the matching URI in the Console first, or the login fails with
# redirect_uri_mismatch.
DEFAULT_PORT = "8000"


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # Apply DEFAULT_PORT only when no address/port was actually given, so
    # `runserver --noreload` still gets it and `runserver 9000` still wins.
    if len(sys.argv) > 1 and sys.argv[1] == "runserver":
        if not any(not arg.startswith("-") for arg in sys.argv[2:]):
            sys.argv.append(DEFAULT_PORT)

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
