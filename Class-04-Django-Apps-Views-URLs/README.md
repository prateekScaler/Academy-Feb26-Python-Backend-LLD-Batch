# Class 4: Python Setup, Django, Apps, Views & URLs

Restaurant Analogy: **Time to build your restaurant! First, set up your kitchen (Python), design your workspace (Virtual Environment), install your restaurant management system (Django), and hire your first staff — the host who greets customers and directs them to the right table (URLs & Views).**

---

## Quick Revision: What We're Building

Remember from Class 1:

```
┌──────────┐         HTTP Request          ┌──────────┐
│  Client  │  ───────────────────────────► │  Server  │
│ (Browser)│                               │ (Django) │
│          │  ◄─────────────────────────── │          │
└──────────┘         HTTP Response         └──────────┘
                    (HTML/JSON)
```

Today, we build the **Server** part using Django!

---

## Part 1: Python Installation

### Why Python for Backend?

| Reason | Explanation |
|--------|-------------|
| **Readable** | Code reads like English — easier to learn, review, and maintain |
| **Batteries Included** | Rich standard library + huge ecosystem (Django, FastAPI, Flask) |
| **Versatile** | Web, ML, scripting, automation — one language, many domains |
| **Community** | Massive community = lots of tutorials, answers, and packages |

### Python Versions: A Brief History

**Python 3.0 was released on December 3, 2008** — a major redesign that broke backwards compatibility with Python 2. The migration took the community over a decade!

```
Python 2 ──────────────────────────────► EOL: Jan 1, 2020 ☠️
                                         (Don't use!)

Python 3.6 (2016) → 3.7 → 3.8 → 3.9 → 3.10 → 3.11 → 3.12 → 3.13 (Latest)
                                              │
                                              └── Performance boost!
```

**Which version to use?**

| Version | Status | Recommendation |
|---------|--------|----------------|
| Python 2.x | ☠️ Dead | Never use |
| Python 3.8-3.9 | Stable | Many production apps still run these |
| Python 3.10-3.11 | ⭐ Recommended | Best balance of features + stability |
| Python 3.12-3.13 | Latest | Cutting edge, some packages may lag |

### What Do Modern Projects Use?

Most modern production applications run on **Python 3.10 or 3.11**:

- **3.10+** introduced structural pattern matching (match/case) — like switch statements
- **3.11** is up to 25% faster than 3.10 with much better error messages
- Major frameworks (Django, FastAPI) fully support these versions
- All popular packages are compatible

**Rule of thumb:** Use `3.10` or `3.11` for this course. They have excellent Django support.

### Check If Python Is Installed

```bash
# macOS / Linux
python3 --version

# Windows (try both)
python --version
python3 --version
```

### Installing Python

#### macOS

```bash
# Option 1: Official installer (Recommended for beginners)
# Download from https://www.python.org/downloads/

# Option 2: Homebrew (if you use it)
brew install python@3.11

# Verify
python3 --version
```

#### Windows

```powershell
# Option 1: Official installer (Recommended)
# 1. Go to https://www.python.org/downloads/
# 2. Download Python 3.11.x
# 3. IMPORTANT: Check "Add Python to PATH" during installation!

# Option 2: Microsoft Store
# Search "Python 3.11" in Microsoft Store

# Verify (open Command Prompt or PowerShell)
python --version
```

#### What Does "Add Python to PATH" Mean?

**PATH** is an environment variable that tells your computer *where to find programs* when you type commands in the terminal.

When you type `python` in the terminal:
1. Your computer looks through all folders listed in PATH
2. It searches for an executable named `python` or `python.exe`
3. If found, it runs that program

| Without PATH | With PATH |
|--------------|-----------|
| Must type full path: `C:\Users\You\AppData\Local\Programs\Python\Python311\python.exe` | Just type: `python` |
| Very inconvenient! | System knows where to find it |

**If you forgot to check the box:** Reinstall Python and check it this time, or manually add Python to PATH in System Environment Variables.

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Verify
python3 --version
```

### 🎯 Quick Check: Is Your Python Ready?

```bash
# Run this command
python3 -c "print('Hello, Django awaits!')"

# Expected output:
# Hello, Django awaits!
```

---

## Part 2: Virtual Environments

### Why Do We Need Virtual Environments?

The core problem is **conflicting dependencies**. Imagine you're working on two different projects on the same computer:

- **Project A** (an old client project) needs `requests==2.20.0` (from 2018)
- **Project B** (your new project) needs `requests==2.31.0` (latest)

Without virtual environments, you can only have **one version** installed at a time. Installing 2.31.0 might break Project A!

### The Problem: Dependency Hell 🔥

```
Project A needs: Django 3.2, requests 2.25
Project B needs: Django 4.2, requests 2.31

Without isolation:
┌─────────────────────────────────────────┐
│           Your Computer                 │
│  Django = ??? (Which version?!)         │
│  requests = ??? (Conflict!)             │
└─────────────────────────────────────────┘
```

**Think of it like separate toolboxes:** A virtual environment gives each project its own toolbox:
- Each toolbox has exactly the tools (packages) that project needs
- Adding a tool to one toolbox doesn't affect others
- You can delete a toolbox without affecting your main system

### The Solution: Virtual Environments

```
┌─────────────────────────────────────────┐
│           Your Computer                 │
│                                         │
│  ┌─────────────┐   ┌─────────────┐     │
│  │  Project A  │   │  Project B  │     │
│  │  (venv)     │   │  (venv)     │     │
│  │ Django 3.2  │   │ Django 4.2  │     │
│  │ requests2.25│   │ requests2.31│     │
│  └─────────────┘   └─────────────┘     │
│                                         │
└─────────────────────────────────────────┘
```

Each project gets its own **isolated** Python environment!

### Restaurant Analogy 🍽️

| Without venv | With venv |
|--------------|-----------|
| One shared kitchen for all restaurants | Each restaurant has its own kitchen |
| Recipe conflicts! | Clean separation |
| Update one ingredient, break another dish | Changes don't affect other projects |

### Creating a Virtual Environment

#### macOS / Linux

```bash
# Navigate to your project folder
cd ~/projects/my_restaurant

# Create virtual environment (named 'venv')
python3 -m venv venv

# Activate it
source venv/bin/activate

# Your prompt changes to show (venv):
# (venv) username@computer:~/projects/my_restaurant$

# Deactivate when done
deactivate
```

#### Windows (Command Prompt)

```cmd
# Navigate to your project folder
cd C:\projects\my_restaurant

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate.bat

# Your prompt changes to show (venv):
# (venv) C:\projects\my_restaurant>

# Deactivate when done
deactivate
```

#### Windows (PowerShell)

```powershell
# Navigate to your project folder
cd C:\projects\my_restaurant

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\Activate.ps1

# If you get a permission error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Deactivate when done
deactivate
```

### How Do You Know venv Is Active?

| State | Terminal Prompt | `which python` / `where python` |
|-------|-----------------|--------------------------------|
| **Not active** | `username@computer:~$` | `/usr/bin/python3` (system) |
| **Active** | `(venv) username@computer:~$` | `/path/to/project/venv/bin/python` |

### Virtual Environment Checklist

```bash
# 1. Create project folder
mkdir my_restaurant && cd my_restaurant

# 2. Create venv
python3 -m venv venv        # macOS/Linux
python -m venv venv         # Windows

# 3. Activate
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate       # Windows

# 4. Verify (should show venv path)
which python                # macOS/Linux
where python                # Windows

# 5. Install packages (they go into venv, not system!)
pip install django

# 6. When done, deactivate
deactivate
```

### Can I Name My Virtual Environment Something Else?

**Yes!** The name "venv" is just a convention. You can use any name:

```bash
python3 -m venv myenv           # Creates folder "myenv"
python3 -m venv .venv           # Creates hidden folder ".venv"
python3 -m venv restaurant_env  # Creates folder "restaurant_env"
```

**Best Practice:** Use `venv` or `.venv` (with dot, makes it hidden on Unix systems). This is what most projects use, so other developers will immediately recognize it.

### Best Practice: Add venv to .gitignore

Virtual environments should **never** be committed to Git:

```bash
# .gitignore
venv/
.venv/
env/
```

**Why?** Virtual environments are large and system-specific. Instead, share a `requirements.txt`:

```bash
# Generate requirements file
pip freeze > requirements.txt

# Another developer can recreate the environment:
pip install -r requirements.txt
```

---

## Part 3: pip — Python Package Manager

Before we install Django, let's understand pip.

### What Is a Package Manager?

At its core, a package manager is just a tool that answers one question:

> *"I need software X — go find it, download it, and set it up for me."*

**Before package managers existed, you'd manually:**
1. Google the library
2. Find the right version
3. Download a zip
4. Figure out where to put it
5. Manually handle anything *it* depends on

A package manager automates all of that.

### The Real-World Analogy

Think of it like an **app store**, but for code libraries:

| Concept | Equivalent |
|---------|------------|
| The store | **PyPI** (pypi.org) — has 400,000+ packages |
| The checkout counter | **pip** — the tool you use |
| `pip install django` | You saying *"get me Django from the store and install it"* |

### Where Does pip Come From?

**pip comes bundled with Python!** When you install Python 3.4+, pip is automatically included.

- **pip** = "Pip Installs Packages" (recursive acronym!)
- It downloads packages from [pypi.org](https://pypi.org) (Python Package Index)

### Breaking Down `pip install django`

```bash
pip install django
│    │       │
│    │       └── Package name (looked up on PyPI)
│    └── The action
└── Python's package manager
```

**Behind the scenes, pip:**
1. Goes to PyPI and finds the latest stable Django
2. Downloads it
3. Resolves Django's own dependencies (and installs those too)
4. Places everything in your **active environment's** `site-packages` folder

### Why the Virtual Environment Part Matters Here

This is the payoff of activating `.venv` first:

```bash
source .venv/bin/activate   # Step 1: Activate venv
pip install django          # Step 2: Install Django
```

| Scenario | Where Django Goes | Good or Bad? |
|----------|-------------------|--------------|
| **Without** activation | Global Python | ❌ Bad — affects all projects |
| **With** activation | Just this project's `.venv` | ✅ Good — isolated |

You can verify this with:

```bash
pip show django
# Location: .../.venv/lib/python3.x/site-packages ✓
```

### Common pip Commands

```bash
# Install a package
(venv) $ pip install django

# Install specific version
(venv) $ pip install django==4.2

# List installed packages
(venv) $ pip list

# Show package details (including location!)
(venv) $ pip show django

# Uninstall a package
(venv) $ pip uninstall django

# Save all installed packages to a file
(venv) $ pip freeze > requirements.txt

# Install from requirements file
(venv) $ pip install -r requirements.txt
```

> ⚠️ **Always activate your venv before using pip!** If you run `pip install` without activating venv, packages install globally (system-wide) — exactly what we want to avoid!

---

## Part 4: What Is Django?

### Where Does the Name "Django" Come From?

Django is named after **Django Reinhardt** (1910-1953), a legendary Belgian-born Romani-French jazz guitarist. The framework's creators, Adrian Holovaty and Simon Willison, were jazz enthusiasts.

### What Does "Batteries-Included" Mean?

Like a toy that comes with batteries ready to play immediately, Django comes with **everything you need** to build web applications out of the box:

- **Admin Panel** — Auto-generated interface to manage your data
- **ORM (Object-Relational Mapping)** — Talk to databases using Python, not SQL
- **Authentication** — User login, logout, permissions built-in
- **Form handling** — Validation and rendering
- **Security** — Protection against common attacks (XSS, CSRF, SQL injection)

**Compare to Flask:** Flask is a "micro-framework" — it gives you the minimum and you add batteries (extensions) yourself.

### Django: The "Batteries-Included" Framework

Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design.

```
┌────────────────────────────────────────────────────────────┐
│                         DJANGO                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   ORM    │  │  Admin   │  │   Auth   │  │  Forms   │  │
│  │(Database)│  │  Panel   │  │  System  │  │Validation│  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   URL    │  │Templating│  │ Security │  │  Cache   │  │
│  │  Router  │  │  Engine  │  │  Built-in│  │Framework │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└────────────────────────────────────────────────────────────┘
```

### Django's Philosophy: "The Django Way"

| Principle | Meaning | Restaurant Analogy |
|-----------|---------|-------------------|
| **DRY** (Don't Repeat Yourself) | Write once, reuse everywhere | One master recipe, not 10 copies |
| **Convention over Configuration** | Sensible defaults, override when needed | Standard kitchen layout; customize if needed |
| **Explicit is better than implicit** | No magic — code should be clear | Recipe says "2 cups flour", not "some flour" |
| **Loose coupling** | Components are independent | Waiter doesn't need to know how to cook |
| **MTV Architecture** | Model-Template-View separation | Kitchen (Model), Plating (Template), Waiter (View) |

### Django vs Other Python Frameworks

| Framework | Type | Best For | Analogy |
|-----------|------|----------|---------|
| **Django** | Full-stack, batteries-included | Large apps, admin panels, rapid MVP | Full restaurant with kitchen, dining, management |
| **Flask** | Micro-framework, minimal | Small APIs, learning, flexibility | Food truck — you build what you need |
| **FastAPI** | Modern, async, fast | APIs, microservices, ML serving | High-speed kitchen specializing in takeout |

### When to Choose Django?

✅ **Use Django when:**
- You need an admin panel (Django Admin is amazing!)
- You want rapid prototyping
- Building full-stack applications
- Security is a priority (built-in protections)
- Working with SQL databases

❌ **Consider alternatives when:**
- Building a tiny API (Flask might be simpler)
- Need maximum async performance (FastAPI)
- Want complete control over every component

---

## Part 4: Installing Django & Creating a Project

### Step 1: Install Django

```bash
# Make sure your venv is activated!
# You should see (venv) in your prompt

# Install Django
pip install django

# Verify installation
python -m django --version
# Output: 5.x.x (or similar)

# Alternative verification
django-admin --version
```

### Step 2: Create a Django Project

```bash
# Create a new Django project called 'restaurant_project'
django-admin startproject restaurant_project

# Alternative (if django-admin doesn't work)
python -m django startproject restaurant_project
```

### Breaking Down the Command

| Part | Meaning |
|------|---------|
| `django-admin` | Django's command-line tool (installed with Django) |
| `startproject` | Command to create a new project skeleton |
| `restaurant_project` | Your project name (use lowercase, underscores, no spaces) |

This creates a folder with all the files Django needs to run. You only do this **once per project**.

### What Just Got Created?

```
restaurant_project/           # Project root (can rename this)
│
├── manage.py                 # Command-line utility for Django
│
└── restaurant_project/       # Actual Python package (settings live here)
    ├── __init__.py          # Makes this directory a Python package
    ├── settings.py          # Project configuration
    ├── urls.py              # URL routing (main router)
    ├── asgi.py              # ASGI config (async servers)
    └── wsgi.py              # WSGI config (traditional servers)
```

### Understanding Each File

#### `manage.py` — Your Swiss Army Knife 🔧

```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_project.settings')
    # ...
```

**What it does:**
- Entry point for all Django commands
- `runserver`, `migrate`, `createsuperuser`, etc.
- Never edit this file!

**Common commands:**

```bash
python manage.py runserver          # Start development server
python manage.py migrate            # Apply database changes
python manage.py createsuperuser    # Create admin user
python manage.py startapp myapp     # Create new app
python manage.py shell              # Interactive Python shell with Django
python manage.py check              # Check for issues
```

#### `__init__.py` — Why Does This File Exist?

In Python, a folder is just a folder. But a folder with `__init__.py` becomes a **Python package** that can be imported.

```python
# This file is empty by default!
# Its mere existence tells Python: "This folder is a package"

# Without this file:
# from restaurant_project import settings  # Would FAIL!

# With this file:
# from restaurant_project import settings  # Works!
```

#### `settings.py` — The Configuration Hub ⚙️

This file contains ALL configuration for your Django project. Let's go through **every** default setting:

```python
"""
Django settings for restaurant_project project.

Generated by 'django-admin startproject' using Django 5.x.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
```

##### 1. BASE_DIR — The Project Root

```python
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
```

| Part | Meaning |
|------|---------|
| `Path(__file__)` | Path to this settings.py file |
| `.resolve()` | Convert to absolute path (no `..` or `.`) |
| `.parent` | Go up one directory (to `restaurant_project/`) |
| `.parent` | Go up again (to project root with `manage.py`) |

**Why?** All other paths (database, templates, static files) are relative to this. Using `Path` (from `pathlib`) makes paths work on Windows, macOS, and Linux.

##### 2. Security Settings

```python
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-^gotz33w8690mo+=mm(rbi5$k6jow(&^+#3v-@6a!pl&@et#z8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
```

| Setting | Purpose | Development | Production |
|---------|---------|-------------|------------|
| `SECRET_KEY` | Cryptographic signing (sessions, tokens, CSRF) | Auto-generated (fine to commit) | **Must be secret!** Use environment variable |
| `DEBUG` | Show detailed error pages with code | `True` | **Must be `False`!** Exposes sensitive info |
| `ALLOWED_HOSTS` | Domains allowed to serve this app | `[]` (localhost only) | `['yourdomain.com', 'www.yourdomain.com']` |

##### 3. INSTALLED_APPS — Registered Applications

```python
INSTALLED_APPS = [
    'django.contrib.admin',        # Auto-generated admin interface
    'django.contrib.auth',         # User authentication system
    'django.contrib.contenttypes', # Framework for content types
    'django.contrib.sessions',     # Session framework (user state)
    'django.contrib.messages',     # Flash messaging framework
    'django.contrib.staticfiles',  # Static file handling
]
```

| App | Purpose | Restaurant Analogy |
|-----|---------|-------------------|
| `admin` | Auto-generated CRUD interface for your models | Manager's dashboard |
| `auth` | Users, groups, permissions, login/logout | Employee ID system |
| `contenttypes` | Track all models in your project | Central recipe registry |
| `sessions` | Store user data across requests (login state) | Customer loyalty card |
| `messages` | One-time notifications ("Item added!") | Waiter's confirmation slip |
| `staticfiles` | Serve CSS, JavaScript, images | Restaurant décor & menus |

**Your apps go here too!** Add `'menu',` when you create the menu app.

##### 4. MIDDLEWARE — Request/Response Pipeline

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

Middleware are like **security checkpoints** that every request passes through:

```
Request → [Middleware 1] → [Middleware 2] → ... → View
Response ← [Middleware 1] ← [Middleware 2] ← ... ← View
```

| Middleware | What It Does |
|------------|--------------|
| `SecurityMiddleware` | Adds security headers (HTTPS redirect, HSTS) |
| `SessionMiddleware` | Enables session support (`request.session`) |
| `CommonMiddleware` | URL normalization (adds trailing slashes), handles `Content-Length` |
| `CsrfViewMiddleware` | Protects against Cross-Site Request Forgery attacks |
| `AuthenticationMiddleware` | Attaches `request.user` to every request |
| `MessageMiddleware` | Enables flash messages (`messages.success(request, "Done!")`) |
| `XFrameOptionsMiddleware` | Prevents clickjacking (blocks embedding in iframes) |

**Order matters!** `SessionMiddleware` must come before `AuthenticationMiddleware` (auth needs sessions).

##### 5. ROOT_URLCONF — Main URL Router

```python
ROOT_URLCONF = 'restaurant_project.urls'
```

This tells Django: "Start URL matching from `restaurant_project/urls.py`". All incoming requests first check this file.

##### 6. TEMPLATES — Template Engine Configuration

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

| Setting | Purpose |
|---------|---------|
| `BACKEND` | Template engine to use (Django's built-in or Jinja2) |
| `DIRS` | Additional directories to search for templates (e.g., `[BASE_DIR / 'templates']`) |
| `APP_DIRS` | If `True`, look for `templates/` folder inside each app |
| `context_processors` | Functions that add variables to every template |

**Context Processors Explained:**

| Processor | What It Adds to Templates |
|-----------|--------------------------|
| `request` | The `request` object (access `request.user`, `request.path`) |
| `auth` | `user` and `perms` variables |
| `messages` | Flash messages from `django.contrib.messages` |

##### 7. WSGI_APPLICATION — Server Entry Point

```python
WSGI_APPLICATION = 'restaurant_project.wsgi.application'
```

Points to the WSGI application object in `wsgi.py`. Production servers (Gunicorn, uWSGI) use this to run your app.

##### 8. DATABASES — Database Configuration

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

| Setting | Purpose |
|---------|---------|
| `ENGINE` | Database backend (`sqlite3`, `postgresql`, `mysql`, `oracle`) |
| `NAME` | Database name (for SQLite, it's the file path) |

**SQLite** is perfect for development — zero setup, file-based. For production, use PostgreSQL or MySQL:

```python
# Production PostgreSQL example
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'restaurant_db',
        'USER': 'restaurant_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

##### 9. AUTH_PASSWORD_VALIDATORS — Password Security

```python
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

| Validator | What It Checks |
|-----------|---------------|
| `UserAttributeSimilarityValidator` | Password can't be too similar to username/email |
| `MinimumLengthValidator` | Password must be at least 8 characters (default) |
| `CommonPasswordValidator` | Rejects 20,000 common passwords ("password123") |
| `NumericPasswordValidator` | Password can't be entirely numbers |

##### 10. Internationalization (i18n) Settings

```python
LANGUAGE_CODE = 'en-us'  # Default language
TIME_ZONE = 'UTC'        # Server timezone (use 'Asia/Kolkata' for IST)
USE_I18N = True          # Enable Django's translation system
USE_TZ = True            # Store datetimes in UTC, convert on display
```

| Setting | Purpose |
|---------|---------|
| `LANGUAGE_CODE` | Default language for the site |
| `TIME_ZONE` | Timezone for displaying dates/times |
| `USE_I18N` | Enable internationalization (translations) |
| `USE_TZ` | Use timezone-aware datetimes (recommended!) |

**Why `USE_TZ = True`?** Storing everything in UTC prevents timezone bugs. Django converts to `TIME_ZONE` when displaying.

##### 11. Static Files Configuration

```python
STATIC_URL = 'static/'
```

| Setting | Purpose |
|---------|---------|
| `STATIC_URL` | URL prefix for static files (`/static/css/style.css`) |

**For production, you'll also add:**

```python
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Where collectstatic puts files
STATICFILES_DIRS = [BASE_DIR / 'static']  # Additional static directories
```

##### 12. Default Primary Key Type

```python
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

New in Django 3.2+. Sets the default type for auto-generated primary keys. `BigAutoField` supports larger IDs than `AutoField` (useful for tables with millions of rows).

#### `urls.py` — The Traffic Director 🚦

```python
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),  # Built-in admin panel
]
```

**Restaurant Analogy:** This is your **host/receptionist**. When a customer (request) arrives:
- "I want `/admin/`" → "Right this way to the admin area!"
- "I want `/menu/`" → "Let me direct you to the menu view!"

#### `wsgi.py` & `asgi.py` — Server Interfaces

```python
# wsgi.py — For traditional synchronous servers (Gunicorn, uWSGI)
# asgi.py — For async servers (Daphne, Uvicorn) — WebSockets, etc.
```

| File | Protocol | Use Case |
|------|----------|----------|
| `wsgi.py` | WSGI (sync) | Traditional web apps, most deployments |
| `asgi.py` | ASGI (async) | Real-time features, WebSockets, HTTP/2 |

### Step 3: Run the Development Server

```bash
# Navigate into the project
cd restaurant_project

# Run the server
python manage.py runserver
```

**Expected output:**

```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).

You have 18 unapplied migration(s)...
Run 'python manage.py migrate' to apply them.

Django version 5.x.x, using settings 'restaurant_project.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### 🎯 Visit Your First Django Page!

Open your browser and go to: **http://127.0.0.1:8000/**

You should see the Django welcome page: "The install worked successfully!"

```
┌─────────────────────────────────────────────────────────┐
│  🎉 The install worked successfully! Congratulations!  │
│                                                         │
│  You are seeing this page because DEBUG=True...        │
└─────────────────────────────────────────────────────────┘
```

### Fixing the Migration Warning

```bash
# Apply initial migrations (creates database tables)
python manage.py migrate

# Output:
# Operations to perform:
#   Apply all migrations: admin, auth, contenttypes, sessions
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying auth.0001_initial... OK
#   ...
```

---

## Part 5: Django Apps — Modular Building Blocks

### Why Can't We Put Everything in the Project Folder?

You *could* put all your code in the project folder, but it would quickly become a mess! Here's why Django uses apps:

| Reason | Explanation |
|--------|-------------|
| **Separation of concerns** | Menu logic stays in `menu/`, orders in `orders/` |
| **Reusability** | You can copy an app (e.g., `users/`) to another project |
| **Team collaboration** | Different developers can work on different apps without conflicts |
| **Testing** | Test each app independently |
| **Maintainability** | A 1000-line models.py is harder to manage than 10 files of 100 lines each |

### What Is a Django App?

A Django **project** can contain multiple **apps**. Each app is a self-contained module that does one thing well.

```
restaurant_project/              # The Restaurant Chain (Project)
│
├── manage.py
├── restaurant_project/          # Chain headquarters (settings, main URLs)
│
├── menu/                        # Menu App (handles food items)
├── orders/                      # Orders App (handles orders)
├── reservations/                # Reservations App (handles bookings)
└── staff/                       # Staff App (handles employees)
```

**Restaurant Analogy:**
- **Project** = Restaurant chain (Domino's, McDonald's)
- **App** = Department (Kitchen, Delivery, HR, Marketing)

### Project vs App: Key Differences

| Concept | Project | App |
|---------|---------|-----|
| **Contains** | Settings, root URLs, deployment config | Models, Views, URLs, Templates |
| **Quantity** | One per website | Multiple per project |
| **Purpose** | Tie everything together | Handle one specific feature |
| **Reusability** | Not reusable | Can be reused across projects! |

### Django Apps vs Microservices: A Common Confusion

Many developers ask: *"Are Django apps like microservices?"* The short answer: **No, but they share the same motivation.**

#### The Similarities

Both Django apps and microservices aim for:

| Goal | Django Apps | Microservices |
|------|-------------|---------------|
| **Modularity** | Separate folders for separate features | Separate services for separate features |
| **Separation of concerns** | `menu/` handles menus, `orders/` handles orders | Menu Service handles menus, Order Service handles orders |
| **Team ownership** | Teams can work on different apps | Teams own different services |
| **Focused scope** | One app = one domain | One service = one domain |

#### The Critical Differences

```
Django Apps (Monolith):
┌────────────────────────────────────────────────────────┐
│                  ONE PROCESS / ONE SERVER              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │  menu/   │  │ orders/  │  │  users/  │            │
│  │  app     │◄─►│  app     │◄─►│  app     │            │
│  └──────────┘  └──────────┘  └──────────┘            │
│         │            │            │                   │
│         └────────────┼────────────┘                   │
│                      ▼                                │
│            ┌──────────────────┐                       │
│            │  SHARED DATABASE │                       │
│            └──────────────────┘                       │
└────────────────────────────────────────────────────────┘

Microservices:
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Menu Service │     │ Order Service│     │ User Service │
│  (Process 1) │────►│  (Process 2) │────►│  (Process 3) │
│    :8001     │ API │    :8002     │ API │    :8003     │
├──────────────┤     ├──────────────┤     ├──────────────┤
│   Menu DB    │     │   Order DB   │     │   User DB    │
└──────────────┘     └──────────────┘     └──────────────┘
   Network calls between services (HTTP/gRPC/Message Queue)
```

| Aspect | Django Apps | Microservices |
|--------|-------------|---------------|
| **Communication** | Direct Python imports (`from orders.models import Order`) | Network calls (HTTP APIs, gRPC, message queues) |
| **Database** | Shared database, same tables | Typically separate databases per service |
| **Deployment** | Deploy entire project together | Deploy each service independently |
| **Scaling** | Scale the whole app | Scale individual services |
| **Failure isolation** | One crash = entire app down | One service down ≠ all services down |
| **Latency** | Microseconds (function calls) | Milliseconds (network calls) |
| **Complexity** | Simple: one codebase, one deployment | Complex: service discovery, distributed tracing, eventual consistency |

#### Historical Context

- **Django (2005)** predates the microservices trend (popularized ~2011-2014 by Netflix, Amazon)
- Django apps are inspired by **Unix philosophy**: "Do one thing well"
- The concept is closer to a **"Modular Monolith"** than microservices
- Many successful companies (Instagram, Pinterest, Disqus) scaled Django monoliths to millions of users

#### Which Should You Use?

| Start Here | Graduate To (If Needed) |
|------------|------------------------|
| Django apps (monolith) | Microservices |

**Why start with a monolith?**
- Simpler to develop, test, deploy
- No network latency between components
- Shared transactions (ACID guarantees)
- Easier debugging (one codebase)

**Consider microservices when:**
- Different parts need different scaling (e.g., video processing vs. user profiles)
- Teams are large enough to own separate services (50+ engineers)
- You need independent deployment cycles
- Different parts need different tech stacks

> **Martin Fowler's advice:** *"Don't start with microservices. Start with a modular monolith, and extract services only when you have a proven need."*

#### Restaurant Analogy

| Architecture | Restaurant Equivalent |
|--------------|----------------------|
| **Django Apps** | Departments in ONE restaurant: kitchen, waitstaff, billing all work together in the same building |
| **Microservices** | Separate companies: one company does food prep, another does delivery, another does payments — they communicate via phone calls and contracts |

### Creating Your First App

```bash
# Make sure you're in the project directory (where manage.py is)
cd restaurant_project

# Create a new app called 'menu'
python manage.py startapp menu
```

### App Directory Structure

```
menu/                           # Your new app
│
├── __init__.py                 # Makes this a Python package
├── admin.py                    # Register models for admin panel
├── apps.py                     # App configuration
├── models.py                   # Database models (tables)
├── tests.py                    # Unit tests
├── views.py                    # View functions/classes
│
└── migrations/                 # Database migration files
    └── __init__.py
```

### Understanding Each App File

| File | Purpose | Restaurant Analogy |
|------|---------|-------------------|
| `models.py` | Define database tables | Recipe cards (what ingredients exist) |
| `views.py` | Handle requests, return responses | Waiters (take orders, bring food) |
| `urls.py` | Route URLs to views | Host station (direct customers) |
| `admin.py` | Configure admin panel | Manager's dashboard |
| `tests.py` | Automated tests | Quality control checks |
| `apps.py` | App configuration | Department policies |

### Registering Your App

**Important!** After creating an app, you must register it in `settings.py`:

```python
# restaurant_project/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your apps
    'menu',  # Add this line!
]
```

---

## Part 6: Views — The Heart of Your App

### What Is a View?

A **view** is a Python function (or class) that:
1. Receives an HTTP request
2. Does some processing
3. Returns an HTTP response

```
Request ──► View ──► Response
           │
           ├── Query database
           ├── Process data
           └── Render template
```

**Restaurant Analogy:** Views are your **waiters**:
- Customer asks for the menu → Waiter fetches and presents it
- Customer orders pasta → Waiter takes order to kitchen, brings back food

### Your First View: Hello World

#### Step 1: Create the View

```python
# menu/views.py

from django.http import HttpResponse

def home(request):
    """
    The simplest possible view.
    - Receives: HttpRequest object
    - Returns: HttpResponse object
    """
    return HttpResponse("Welcome to our restaurant! 🍽️")


def menu_list(request):
    """A view that returns a simple menu."""
    menu_items = """
    <h1>Today's Menu</h1>
    <ul>
        <li>Pasta Carbonara - $15</li>
        <li>Grilled Salmon - $22</li>
        <li>Caesar Salad - $12</li>
    </ul>
    """
    return HttpResponse(menu_items)
```

#### Step 2: Create App URLs

Create a new file `menu/urls.py`:

```python
# menu/urls.py

from django.urls import path
from . import views  # Relative import: "." = current folder

urlpatterns = [
    path('', views.home, name='home'),
    path('list/', views.menu_list, name='menu_list'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
]
```

> **Why `from . import views` instead of `from menu import views`?**
>
> The dot (`.`) means "current package" — like `./` in terminal paths. This is a **relative import**. It keeps your app portable: if you rename the project or reuse this app elsewhere, the import still works. Never hardcode the project name like `from myproject.menu import views` — that breaks portability.

##### Breaking Down Each `path()` Call — Parameter by Parameter

The `path()` function signature:

```python
path(route, view, kwargs=None, name=None)
```

**Let's dissect each URL pattern:**

---

**Pattern 1:** `path('', views.home, name='home')`

| Parameter | Value | Explanation |
|-----------|-------|-------------|
| `route` | `''` | Empty string = matches the base URL of wherever this is included. If included at `/menu/`, this matches `/menu/` exactly |
| `view` | `views.home` | The function `home` from `views.py` that handles this request |
| `name` | `'home'` | A unique identifier for this URL. Used in templates (`{% url 'home' %}`) and code (`reverse('home')`) |

**What happens:** When user visits `/menu/`, Django calls `views.home(request)`.

---

**Pattern 2:** `path('list/', views.menu_list, name='menu_list')`

| Parameter | Value | Explanation |
|-----------|-------|-------------|
| `route` | `'list/'` | Matches the path `list/` (with trailing slash). Combined with `/menu/` prefix, matches `/menu/list/` |
| `view` | `views.menu_list` | The function `menu_list` from `views.py` |
| `name` | `'menu_list'` | Unique name for reverse URL lookup |

**What happens:** When user visits `/menu/list/`, Django calls `views.menu_list(request)`.

**Note on trailing slash:** Django convention is to always include trailing slashes. `CommonMiddleware` can redirect `/menu/list` to `/menu/list/` automatically.

---

**Pattern 3:** `path('item/<int:item_id>/', views.item_detail, name='item_detail')`

| Parameter | Value | Explanation |
|-----------|-------|-------------|
| `route` | `'item/<int:item_id>/'` | Matches `item/` followed by an integer. The `<int:item_id>` is a **path converter** |
| `view` | `views.item_detail` | The function that receives the captured value |
| `name` | `'item_detail'` | Used as `{% url 'item_detail' item_id=5 %}` |

**Breaking down `<int:item_id>`:**

```
<int:item_id>
  │     │
  │     └── Variable name passed to the view function
  └── Converter type (int = only matches integers)
```

| Converter | Matches | Example URL | Captured Value |
|-----------|---------|-------------|----------------|
| `<int:item_id>` | Integers only | `/menu/item/42/` | `item_id=42` (int) |
| `<str:name>` | Any non-empty string (no `/`) | `/menu/item/pasta/` | `name='pasta'` (str) |
| `<slug:title>` | Letters, numbers, hyphens, underscores | `/menu/item/pasta-carbonara/` | `title='pasta-carbonara'` |
| `<uuid:id>` | UUID format | `/menu/item/550e8400-e29b.../` | `id=UUID(...)` |
| `<path:file>` | Any string including `/` | `/files/docs/2024/report.pdf` | `file='docs/2024/report.pdf'` |

**What happens:**
```python
# URL: /menu/item/42/

def item_detail(request, item_id):  # item_id is passed automatically!
    # item_id = 42 (as an integer, not string)
    return HttpResponse(f"Showing item #{item_id}")
```

---

#### Step 3: Include App URLs in Project URLs

```python
# restaurant_project/urls.py

from django.contrib import admin
from django.urls import path, include  # Add 'include'!

urlpatterns = [
    path('admin/', admin.site.urls),
    path('menu/', include('menu.urls')),
]
```

##### Breaking Down the Project URLs

**Pattern 1:** `path('admin/', admin.site.urls)`

| Parameter | Value | Explanation |
|-----------|-------|-------------|
| `route` | `'admin/'` | All URLs starting with `admin/` |
| `view` | `admin.site.urls` | Special: Django admin's URL configuration (not a regular view) |

---

**Pattern 2:** `path('menu/', include('menu.urls'))`

| Parameter | Value | Explanation |
|-----------|-------|-------------|
| `route` | `'menu/'` | URL prefix — all menu-related URLs start with `/menu/` |
| `include(...)` | `include('menu.urls')` | Delegate to `menu/urls.py` for further matching |

##### How `include()` Works — Step by Step

```
User visits: /menu/item/42/

Step 1: Django checks restaurant_project/urls.py
        - Does '/menu/item/42/' start with 'admin/'? NO
        - Does '/menu/item/42/' start with 'menu/'? YES ✓

Step 2: Strip 'menu/' prefix → remaining path is 'item/42/'
        Django now checks menu/urls.py with 'item/42/'

Step 3: In menu/urls.py:
        - Does 'item/42/' match ''? NO
        - Does 'item/42/' match 'list/'? NO
        - Does 'item/42/' match 'item/<int:item_id>/'? YES ✓
        - Captured: item_id = 42

Step 4: Call views.item_detail(request, item_id=42)
```

##### Why Use `include()`?

| Without include | With include |
|-----------------|--------------|
| All URLs in one giant file | URLs organized by app |
| `/menu/list/` defined in project | `/menu/list/` defined in menu app |
| Hard to reuse apps | Apps are self-contained and portable |
| Team conflicts on single file | Teams work on separate files |

---

#### Step 4: Test It!

```bash
python manage.py runserver
```

Visit:
- http://127.0.0.1:8000/menu/ → "Welcome to our restaurant! 🍽️"
- http://127.0.0.1:8000/menu/list/ → The menu HTML

### Anatomy of a View Function

```python
def my_view(request):        # Must accept 'request' as first argument
    #                        # 'request' contains all HTTP request info
    #
    # ... process data ...   # Your logic goes here
    #
    return HttpResponse(...) # Must return an HttpResponse
```

**The `request` object contains:**

| Attribute | Contains | Example |
|-----------|----------|---------|
| `request.method` | HTTP method | `'GET'`, `'POST'` |
| `request.GET` | URL query parameters | `?search=pasta` |
| `request.POST` | Form data | Form submissions |
| `request.path` | URL path | `'/menu/list/'` |
| `request.user` | Current user | `User` object or `AnonymousUser` |

### View Response Types

```python
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

# Plain text/HTML
def text_view(request):
    return HttpResponse("Hello!")

# JSON response (for APIs)
def api_view(request):
    data = {'menu': ['Pasta', 'Pizza', 'Salad']}
    return JsonResponse(data)

# Render HTML template
def template_view(request):
    context = {'restaurant_name': 'Chez Django'}
    return render(request, 'menu/home.html', context)

# Redirect to another URL
def redirect_view(request):
    return redirect('home')  # Redirect to named URL 'home'
```

### Different Ways to Write Views in Django

Django offers multiple approaches to writing views. Understanding these helps you choose the right tool for each situation.

**Official Documentation:** [https://docs.djangoproject.com/en/5.0/topics/http/views/](https://docs.djangoproject.com/en/5.0/topics/http/views/)

#### 1. Function-Based Views (FBVs)

The simplest approach — just a Python function:

```python
# menu/views.py
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404

def menu_list(request):
    """Simple function that handles a request."""
    if request.method == 'GET':
        items = MenuItem.objects.all()
        return JsonResponse({'items': list(items.values())})
    elif request.method == 'POST':
        # Handle creation
        pass
```

| Pros | Cons |
|------|------|
| Simple and explicit | Can get messy with multiple HTTP methods |
| Easy to understand | Repeated code across similar views |
| Full control | No built-in structure |

#### 2. Class-Based Views (CBVs)

Object-oriented approach — inherit from Django's view classes:

```python
# menu/views.py
from django.views import View
from django.http import JsonResponse

class MenuListView(View):
    """Class-based view for menu items."""

    def get(self, request):
        """Handle GET requests."""
        items = MenuItem.objects.all()
        return JsonResponse({'items': list(items.values())})

    def post(self, request):
        """Handle POST requests."""
        # Handle creation
        pass
```

**URL configuration for CBVs:**

```python
# menu/urls.py
from django.urls import path
from .views import MenuListView

urlpatterns = [
    path('', MenuListView.as_view(), name='menu_list'),  # Note: .as_view()
]
```

| Pros | Cons |
|------|------|
| Clean separation of HTTP methods | Steeper learning curve |
| Reusable via inheritance | "Magic" can be hard to trace |
| Built-in generic views for common patterns | Overkill for simple views |

#### 3. Generic Class-Based Views (GCBVs)

Pre-built views for common patterns (CRUD operations):

```python
# menu/views.py
from django.views.generic import ListView, DetailView, CreateView

class MenuListView(ListView):
    model = MenuItem
    template_name = 'menu/list.html'
    context_object_name = 'items'

class MenuDetailView(DetailView):
    model = MenuItem
    template_name = 'menu/detail.html'

class MenuCreateView(CreateView):
    model = MenuItem
    fields = ['name', 'price', 'description']
    success_url = '/menu/'
```

| Pros | Cons |
|------|------|
| Minimal code for standard operations | Complex customization can be tricky |
| DRY — don't reinvent CRUD | Must understand class hierarchy |
| Consistent patterns | Less explicit than FBVs |

**Official Generic Views Reference:** [https://docs.djangoproject.com/en/5.0/ref/class-based-views/](https://docs.djangoproject.com/en/5.0/ref/class-based-views/)

#### Which Should You Use? (Production Recommendations)

| Scenario | Recommended Approach |
|----------|---------------------|
| Simple, one-off views | Function-Based Views |
| Standard CRUD operations | Generic Class-Based Views |
| Complex logic with multiple methods | Class-Based Views |
| API endpoints (with DRF) | DRF's APIView or ViewSets |
| Team prefers explicit code | Function-Based Views |
| Team comfortable with OOP | Class-Based Views |

**Industry Best Practice:** Many production Django applications use a **mix**:
- Generic CBVs for standard CRUD
- FBVs for custom/complex endpoints
- DRF ViewSets for APIs

---

### Should All Logic Live in Views? The Service Layer Pattern

**Short answer: No!** Views should be thin. They should handle HTTP concerns only.

#### The Problem: Fat Views

```python
# ❌ BAD: Too much logic in the view
def create_order(request):
    if request.method == 'POST':
        # Validation
        data = json.loads(request.body)
        if not data.get('items'):
            return JsonResponse({'error': 'No items'}, status=400)

        # Business logic mixed with HTTP handling
        total = 0
        for item in data['items']:
            menu_item = MenuItem.objects.get(id=item['id'])
            total += menu_item.price * item['quantity']

        # Apply discount
        if total > 100:
            total *= 0.9

        # Check inventory
        for item in data['items']:
            menu_item = MenuItem.objects.get(id=item['id'])
            if menu_item.stock < item['quantity']:
                return JsonResponse({'error': 'Out of stock'}, status=400)

        # Create order
        order = Order.objects.create(total=total, user=request.user)
        # ... more logic ...

        return JsonResponse({'order_id': order.id})
```

**Problems:**
- Hard to test (need HTTP request to test business logic)
- Hard to reuse (can't call from management command or Celery task)
- Hard to read (mixing HTTP with business logic)

#### The Solution: Service Layer

Create a separate layer for business logic:

```
┌─────────────────────────────────────────────────────────────┐
│                        Views Layer                          │
│         (HTTP handling, request/response, validation)       │
└─────────────────────────────────┬───────────────────────────┘
                                  │ calls
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      Services Layer                         │
│              (Business logic, orchestration)                │
└─────────────────────────────────┬───────────────────────────┘
                                  │ uses
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│                       Models Layer                          │
│              (Data access, database operations)             │
└─────────────────────────────────────────────────────────────┘
```

#### Where to Put Services in Django?

Django doesn't have a built-in convention, but here's the recommended structure:

```
menu/
├── __init__.py
├── models.py          # Data models
├── views.py           # HTTP handlers (thin!)
├── urls.py            # URL routing
├── services.py        # Business logic ← NEW!
├── selectors.py       # Complex queries (optional) ← NEW!
└── tests/
    ├── test_views.py
    └── test_services.py  # Test business logic in isolation
```

#### Example: Refactored with Service Layer

**services.py — Business Logic:**

```python
# menu/services.py
from django.db import transaction
from .models import MenuItem, Order, OrderItem

class OrderService:
    """Handles all order-related business logic."""

    @staticmethod
    def calculate_total(items_data):
        """Calculate order total with discounts."""
        total = 0
        for item in items_data:
            menu_item = MenuItem.objects.get(id=item['id'])
            total += menu_item.price * item['quantity']

        # Apply bulk discount
        if total > 100:
            total *= 0.9

        return total

    @staticmethod
    def check_inventory(items_data):
        """Verify all items are in stock."""
        for item in items_data:
            menu_item = MenuItem.objects.get(id=item['id'])
            if menu_item.stock < item['quantity']:
                raise ValueError(f"{menu_item.name} is out of stock")

    @classmethod
    @transaction.atomic
    def create_order(cls, user, items_data):
        """
        Create an order with all items.

        Can be called from views, management commands, Celery tasks, etc.
        """
        cls.check_inventory(items_data)
        total = cls.calculate_total(items_data)

        order = Order.objects.create(user=user, total=total)

        for item in items_data:
            OrderItem.objects.create(
                order=order,
                menu_item_id=item['id'],
                quantity=item['quantity']
            )

        return order
```

**views.py — Thin HTTP Handler:**

```python
# menu/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .services import OrderService

@require_POST
def create_order(request):
    """Handle HTTP request for order creation."""
    try:
        data = json.loads(request.body)

        if not data.get('items'):
            return JsonResponse({'error': 'No items provided'}, status=400)

        # Delegate to service layer
        order = OrderService.create_order(
            user=request.user,
            items_data=data['items']
        )

        return JsonResponse({'order_id': order.id, 'total': order.total})

    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Order creation failed'}, status=500)
```

#### Benefits of Service Layer

| Benefit | Explanation |
|---------|-------------|
| **Testability** | Test business logic without HTTP overhead |
| **Reusability** | Call from views, CLI commands, Celery tasks, tests |
| **Readability** | Views are thin, services are focused |
| **Maintainability** | Changes to business logic in one place |
| **Team Scaling** | Clear boundaries between concerns |

#### Alternative Patterns

| Pattern | Description | When to Use |
|---------|-------------|-------------|
| **Fat Models** | Put logic in model methods | Simple logic tied to single model |
| **Services** | Separate service classes/functions | Complex logic spanning multiple models |
| **Selectors** | Separate query logic | Complex, reusable queries |
| **Use Cases** | One class per business operation | Very complex domains (Clean Architecture) |

**Further Reading:**
- [Django Styleguide by HackSoftware](https://github.com/HackSoftware/Django-Styleguide) — Excellent production patterns
- [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x) — Industry best practices

---

### Templates vs JSON APIs: The Modern Evolution

**Discussion Question:** Why do we sometimes return HTML and sometimes return JSON?

#### The Traditional Approach: Server-Side Templates

In the early days of web development (and still valid today for many apps), the server did everything:

```
┌──────────┐    Request     ┌──────────┐    Query    ┌──────────┐
│  Browser │ ─────────────► │  Django  │ ──────────► │ Database │
│          │                │  View    │             │          │
│          │ ◄───────────── │          │ ◄────────── │          │
└──────────┘  Complete HTML └──────────┘    Data     └──────────┘
                 Page
```

The server rendered **complete HTML pages** using templates:

```python
# Traditional Django view with template
def menu_list(request):
    items = MenuItem.objects.all()
    return render(request, 'menu/list.html', {'items': items})
```

**Advantages:**
- Simple — one codebase does everything
- SEO-friendly — search engines see complete HTML
- Fast initial load — page arrives ready to view

#### The Modern Approach: JSON APIs + Frontend Framework

Today, many applications separate the backend (API) from the frontend (React, Vue, mobile apps):

```
┌──────────┐   GET /api/menu/   ┌──────────┐   Query    ┌──────────┐
│  React   │ ─────────────────► │  Django  │ ─────────► │ Database │
│  App     │                    │  REST    │            │          │
│          │ ◄───────────────── │  API     │ ◄───────── │          │
└──────────┘      JSON Data     └──────────┘    Data    └──────────┘
     │
     │ React renders
     │ the UI
     ▼
┌──────────────────┐
│   Beautiful UI   │
│   in Browser     │
└──────────────────┘
```

The server returns **only data** as JSON:

```python
# Modern API view
def menu_list_api(request):
    items = MenuItem.objects.all()
    return JsonResponse({'items': list(items.values())})
```

**Advantages:**
- Same API serves web, mobile, IoT
- Frontend teams can work independently
- Better user experience (no full page reloads)

#### When to Use Which?

| Approach | Best For |
|----------|----------|
| **Templates (HTML)** | Admin panels, simple websites, SEO-critical pages, prototypes |
| **JSON APIs** | Single-page apps (SPAs), mobile backends, microservices, real-time apps |
| **Hybrid** | Public pages with templates, authenticated features with API |

**In this course:** We'll start with simple HTML responses, then move to JSON APIs when we introduce Django REST Framework (DRF).

---

## Part 7: URLs — Routing Requests

### URL Patterns Explained

```python
# The path() function:
path(route, view, kwargs=None, name=None)

# Example:
path('menu/items/', views.item_list, name='item_list')
#     │             │                │
#     │             │                └── Name for reverse lookup
#     │             └── View to call
#     └── URL pattern to match
```

### URL Routing Flow

```
Browser: GET /menu/list/

                    ┌─────────────────────────┐
                    │  restaurant_project/    │
                    │       urls.py           │
                    └───────────┬─────────────┘
                                │
              "menu/" matches path('menu/', include('menu.urls'))
                                │
                                ▼
                    ┌─────────────────────────┐
                    │      menu/urls.py       │
                    └───────────┬─────────────┘
                                │
              "list/" matches path('list/', views.menu_list)
                                │
                                ▼
                    ┌─────────────────────────┐
                    │   menu/views.py         │
                    │   menu_list(request)    │
                    └─────────────────────────┘
```

### Detailed URL Delegation Flow

Here's a more comprehensive view of how Django routes requests through multiple apps:

```
                            ┌──────────────────────────────────┐
                            │         Incoming Request         │
                            │      GET /menu/item/42/          │
                            └───────────────┬──────────────────┘
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     restaurant_project/urls.py                               │
│                                                                              │
│   urlpatterns = [                                                            │
│       path('admin/', admin.site.urls),        ──► /admin/*                   │
│       path('menu/', include('menu.urls')),    ──► /menu/* ✓ MATCHED!         │
│       path('orders/', include('orders.urls')),──► /orders/*                  │
│       path('api/', include('api.urls')),      ──► /api/*                     │
│   ]                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                            │
                    "menu/" prefix stripped, remaining: "item/42/"
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           menu/urls.py                                       │
│                                                                              │
│   urlpatterns = [                                                            │
│       path('', views.home, name='home'),                    ──► /menu/       │
│       path('list/', views.menu_list, name='list'),          ──► /menu/list/  │
│       path('item/<int:item_id>/', views.item_detail, ...),  ──► ✓ MATCHED!   │
│   ]                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                            │
                    "item/" matched, <int:item_id> captures 42
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           menu/views.py                                      │
│                                                                              │
│   def item_detail(request, item_id):   ◄── item_id = 42                      │
│       # Your logic here                                                      │
│       return HttpResponse(f"Item #{item_id}")                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                            │
                                            ▼
                            ┌──────────────────────────────────┐
                            │         Response Sent            │
                            │        "Item #42"                │
                            └──────────────────────────────────┘
```

**Key Points:**
- Django tries URL patterns **in order** (top to bottom)
- `include()` **strips the matched prefix** and passes the rest to the app's urls.py
- Path converters like `<int:item_id>` capture values and pass them to the view
- If no pattern matches, Django returns a 404 error

### Dynamic URLs: Capturing Values

```python
# menu/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Static URL
    path('', views.home, name='home'),

    # Dynamic URL with integer
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    # Example: /menu/item/42/ → item_id = 42

    # Dynamic URL with string
    path('category/<str:category_name>/', views.category, name='category'),
    # Example: /menu/category/desserts/ → category_name = 'desserts'

    # Dynamic URL with slug (URL-friendly string)
    path('dish/<slug:dish_slug>/', views.dish, name='dish'),
    # Example: /menu/dish/pasta-carbonara/ → dish_slug = 'pasta-carbonara'
]
```

```python
# menu/views.py

def item_detail(request, item_id):
    """View that receives item_id from URL."""
    return HttpResponse(f"Showing item #{item_id}")


def category(request, category_name):
    """View that receives category name from URL."""
    return HttpResponse(f"Category: {category_name}")
```

### URL Path Converters

| Converter | Matches | Example |
|-----------|---------|---------|
| `str` | Any non-empty string (excluding `/`) | `<str:name>` |
| `int` | Zero or positive integers | `<int:id>` |
| `slug` | Letters, numbers, hyphens, underscores | `<slug:title>` |
| `uuid` | UUID format | `<uuid:pk>` |
| `path` | Any string including `/` | `<path:file_path>` |

### Naming URLs: Why It Matters

```python
# Instead of hardcoding URLs:
# ❌ Bad: <a href="/menu/item/5/">View Item</a>

# Use named URLs:
# ✅ Good: <a href="{% url 'item_detail' item_id=5 %}">View Item</a>

# In Python code:
from django.urls import reverse

url = reverse('item_detail', kwargs={'item_id': 5})
# Returns: '/menu/item/5/'
```

**Why?** If you change a URL pattern, all references update automatically!

---

## Part 8: Best Practices

### Project Structure Best Practices

```
my_project/
│
├── manage.py
├── requirements.txt              # Dependencies!
├── .gitignore                    # Ignore venv, db.sqlite3, __pycache__
├── README.md
│
├── my_project/                   # Project config
│   ├── settings/                 # Split settings (advanced)
│   │   ├── base.py              # Common settings
│   │   ├── development.py       # Dev settings
│   │   └── production.py        # Prod settings
│   ├── urls.py
│   └── wsgi.py
│
├── apps/                         # All apps in one folder (optional)
│   ├── menu/
│   ├── orders/
│   └── users/
│
├── templates/                    # Global templates
│   └── base.html
│
└── static/                       # Global static files
    ├── css/
    └── js/
```

### View Best Practices

```python
# ✅ Good: Single responsibility
def get_menu(request):
    """Returns the menu."""
    items = MenuItem.objects.all()
    return JsonResponse({'items': list(items.values())})


# ❌ Bad: Doing too much
def do_everything(request):
    """Menu, orders, users, payments... all in one view!"""
    # This is a nightmare to maintain
    pass


# ✅ Good: Use meaningful names
def list_available_dishes(request):
    pass

def get_dish_details(request, dish_id):
    pass


# ❌ Bad: Vague names
def handle(request):
    pass

def process(request):
    pass
```

### URL Best Practices

```python
# ✅ Good: RESTful, descriptive URLs
urlpatterns = [
    path('dishes/', views.dish_list, name='dish_list'),           # List
    path('dishes/<int:id>/', views.dish_detail, name='dish_detail'), # Detail
    path('dishes/create/', views.dish_create, name='dish_create'),   # Create
]

# ❌ Bad: Unclear, inconsistent URLs
urlpatterns = [
    path('getDishes/', views.dishes, name='get'),
    path('dish_view/<int:x>/', views.view, name='v'),
]

# ✅ Good: Use app namespaces (prevents name collisions)
# menu/urls.py
app_name = 'menu'  # Add this!

urlpatterns = [
    path('', views.home, name='home'),
]

# Now reference as: {% url 'menu:home' %}
```

### App Best Practices

| Do | Don't |
|----|-------|
| One app = one feature/domain | One giant app for everything |
| Keep apps small and focused | Apps with 50+ models |
| Apps should be loosely coupled | Apps that import everything from each other |
| Reusable apps where possible | Hardcoded dependencies |

---

## Part 9: How Other Frameworks Differ

### The Same Concepts, Different Names

| Concept | Django | Flask | FastAPI |
|---------|--------|-------|---------|
| **URL Routing** | `urls.py` with `path()` | `@app.route()` decorator | `@app.get()` decorator |
| **Views** | Functions or Classes | Functions | Functions (async supported) |
| **Request Object** | `request` parameter | `flask.request` global | `Request` parameter |
| **Response** | `HttpResponse`, `JsonResponse` | `return` string/dict | `return` dict (auto JSON) |
| **Project Structure** | Enforced (apps, settings) | You decide | You decide |
| **ORM** | Built-in Django ORM | Choose (SQLAlchemy, etc.) | Choose (SQLAlchemy, etc.) |
| **Admin Panel** | Built-in | Not included | Not included |

### Quick Comparison: Same Endpoint

**Django:**
```python
# urls.py
path('hello/<str:name>/', views.hello, name='hello')

# views.py
def hello(request, name):
    return JsonResponse({'message': f'Hello, {name}!'})
```

**Flask:**
```python
@app.route('/hello/<name>')
def hello(name):
    return {'message': f'Hello, {name}!'}
```

**FastAPI:**
```python
@app.get('/hello/{name}')
async def hello(name: str):
    return {'message': f'Hello, {name}!'}
```

### Key Differences Summary

| Aspect | Django | Flask | FastAPI |
|--------|--------|-------|---------|
| **Philosophy** | Batteries included | Minimal, DIY | Modern, async-first |
| **Learning Curve** | Steeper (more concepts) | Gentle (simple start) | Moderate (types, async) |
| **Best For** | Full apps, admin, rapid MVP | Small APIs, learning | High-perf APIs, ML |
| **Built-in Features** | Many (auth, admin, ORM) | Few (routing, templates) | Medium (validation, docs) |
| **Async Support** | Limited (improving) | Limited | Native, excellent |
| **Auto API Docs** | No (use DRF + drf-yasg) | No | Yes (Swagger/OpenAPI) |

---

## Interactive Exercises

### Exercise 1: Complete Setup Checklist

Do this on your own machine:

- [ ] Verify Python 3.10+ is installed
- [ ] Create a new project folder
- [ ] Create and activate a virtual environment
- [ ] Install Django
- [ ] Create a new project called `bookstore`
- [ ] Run the development server
- [ ] See the welcome page in your browser
- [ ] Run migrations to clear the warning

### Exercise 2: Create Your First App

- [ ] Create an app called `catalog`
- [ ] Register it in `settings.py`
- [ ] Create a view that returns "Welcome to BookStore Catalog!"
- [ ] Create `catalog/urls.py` with a route
- [ ] Include catalog URLs in project URLs
- [ ] Test at `http://127.0.0.1:8000/catalog/`

### Exercise 3: Dynamic Routes

Create views for:
- [ ] `/books/` — List all books (hardcoded for now)
- [ ] `/books/<int:book_id>/` — Show "Book #X"
- [ ] `/books/category/<str:category>/` — Show "Category: X"

---

## Assignments

### Assignment 1: Blog Project Setup (Required)

Create a blog project with proper structure:

1. Create project `blog_project` with virtual environment
2. Create app `posts`
3. Implement these URLs and views:
   - `/` — Home page welcoming visitors
   - `/posts/` — List of blog posts (hardcoded)
   - `/posts/<int:post_id>/` — Single post detail
   - `/about/` — About page

**Deliverable:** Screenshot of all 4 pages working + your code.

### Assignment 2: Exploration Tasks (Research)

Research and write a short answer (2-3 sentences each):

1. What is the difference between `path()` and `re_path()` in Django URLs?
2. What is `DEBUG = False` and why is it important for production?
3. What is `ALLOWED_HOSTS` and what happens if you don't set it?
4. How does Django know which settings file to use?
5. What are Django "migrations" and why do we need them?

### Assignment 3: Framework Comparison (Bonus)

Build the SAME tiny API in all three frameworks:
- One endpoint: `GET /greet/<name>` returns `{"greeting": "Hello, <name>!"}`

Compare:
- Lines of code required
- Setup complexity
- Your experience building each

---

## Common Errors & Solutions

### "ModuleNotFoundError: No module named 'django'"

```bash
# Make sure venv is activated!
# You should see (venv) in your prompt

# If not:
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate       # Windows

# Then:
pip install django
```

### "No module named 'your_app'"

```python
# Did you add your app to INSTALLED_APPS?
INSTALLED_APPS = [
    # ...
    'your_app',  # Make sure this is here!
]
```

### "Page not found (404)" on your view

Check:
1. Is the URL pattern correct? (trailing slash!)
2. Did you include app URLs in project URLs?
3. Is the server running?
4. Check for typos in `urlpatterns`

### "DisallowedHost" error

```python
# settings.py
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Or for development:
ALLOWED_HOSTS = ['*']  # Never use in production!
```

---

## Interview Questions

1. **What is a virtual environment and why use one?**
   > Isolated Python environment for project-specific dependencies. Prevents conflicts between projects with different package versions.

2. **Explain Django's MTV architecture.**
   > Model (data/database), Template (presentation/HTML), View (logic connecting them). View in Django is like Controller in MVC.

3. **What's the difference between a Django project and an app?**
   > Project is the entire website (settings, configuration). App is a module handling one feature. A project contains multiple apps.

4. **What does `manage.py` do?**
   > Command-line utility for Django administrative tasks: runserver, migrate, startapp, createsuperuser, etc.

5. **How does URL routing work in Django?**
   > Request URL is matched against patterns in `urls.py`. When matched, the associated view function is called. `include()` delegates to app-specific URL configs.

6. **What's the purpose of naming URLs?**
   > Allows referencing URLs by name instead of hardcoding paths. If URL changes, all references update automatically via `reverse()` or `{% url %}`.

7. **What happens when `DEBUG = True`?**
   > Shows detailed error pages with code snippets and stack traces. Never enable in production — exposes sensitive information!

8. **How would you pass data from URL to view?**
   > Use path converters: `path('item/<int:id>/', views.detail)`. The `id` parameter is passed to the view function.

9. **Why did many modern applications move from server-rendered templates to JSON APIs?**
   > To enable multiple clients (web, mobile, IoT) to consume the same backend. JSON APIs allow frontend and backend teams to work independently, enable richer user experiences with SPAs (single-page applications), and support real-time updates without full page reloads.

10. **When would you still use Django templates instead of a JSON API?**
    > For SEO-critical pages (search engines render HTML better), admin interfaces, quick prototypes, or when you don't need a separate frontend framework. Templates are simpler when the server can handle all rendering.

---

## Resources

### Official Documentation
- [Django Documentation](https://docs.djangoproject.com/) — The best resource
- [Django Girls Tutorial](https://tutorial.djangogirls.org/) — Beginner-friendly

### Interactive Learning
- [Django for Everybody](https://www.dj4e.com/) — Free course by Dr. Chuck
- [Real Python Django Tutorials](https://realpython.com/tutorials/django/) — Excellent tutorials

### Video Courses
- [Corey Schafer Django Series](https://www.youtube.com/playlist?list=PL-osiE80TeTtoQCKZ03TU5fNfx2UY6U4p) — YouTube
- [Traversy Media Django Crash Course](https://www.youtube.com/watch?v=e1IyzVyrLSU) — Quick overview

### Practice
- [Django Polls Tutorial](https://docs.djangoproject.com/en/stable/intro/tutorial01/) — Official tutorial
- Build a todo app, blog, or bookstore as practice

---

## Next Class Preview

**Class 5: Django Models and Admin**

Restaurant Analogy: *How does the kitchen track inventory?*

We'll cover:
- Defining database models (your recipe cards)
- Django's powerful admin panel (manager's dashboard)
- Migrations (updating the recipe book safely)
- Basic queries (finding ingredients)

---

## Quick Reference Card

```bash
# Python & Virtual Environment
python3 --version                    # Check Python version
python3 -m venv venv                 # Create venv
source venv/bin/activate             # Activate (macOS/Linux)
venv\Scripts\activate                # Activate (Windows)
deactivate                           # Deactivate venv

# Django Project
pip install django                   # Install Django
django-admin startproject myproject  # Create project
cd myproject
python manage.py runserver           # Start server (http://127.0.0.1:8000)
python manage.py migrate             # Apply migrations

# Django App
python manage.py startapp myapp      # Create app
# Then add 'myapp' to INSTALLED_APPS in settings.py

# Project Structure
myproject/
├── manage.py                        # CLI tool
├── myproject/
│   ├── settings.py                  # Configuration
│   ├── urls.py                      # Main URL router
│   └── wsgi.py                      # Server interface
└── myapp/
    ├── views.py                     # Request handlers
    ├── urls.py                      # App URL router (create this!)
    └── models.py                    # Database models
```
