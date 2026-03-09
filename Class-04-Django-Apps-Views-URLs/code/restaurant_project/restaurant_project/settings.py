# restaurant_project/settings.py
# Class 4: Key Settings (partial file - showing what we modified)
#
# NOTE: This is not a complete settings.py file.
# When you run `django-admin startproject`, Django generates the full file.
# Below are the key sections we discussed in class.

# =============================================================================
# INSTALLED_APPS - Register your apps here!
# =============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Our apps (add below the built-ins)
    'menu',
]

# =============================================================================
# ROOT_URLCONF - Where Django starts URL matching
# =============================================================================

ROOT_URLCONF = 'restaurant_project.urls'

# =============================================================================
# For a complete settings.py, run:
#   django-admin startproject restaurant_project .
#
# This file is just for reference to show what we modified in class.
# =============================================================================
