# Troubleshooting Guide: Class 4

Common issues students encounter when setting up Python, virtual environments, and Django.

---

## Python Installation Issues

### Issue: `python` command not found (Windows)

**Symptoms:**
```
'python' is not recognized as an internal or external command
```

**Solutions:**

1. **Check if Python is installed via py launcher:**
   ```cmd
   py --version
   py -3 --version
   ```

2. **Add Python to PATH:**
   - Reinstall Python
   - **IMPORTANT:** Check "Add Python to PATH" during installation
   - Or manually add to PATH: `C:\Users\<username>\AppData\Local\Programs\Python\Python311\`

3. **Use `python3` instead:**
   ```cmd
   python3 --version
   ```

4. **Windows Store version conflict:**
   - Search "Manage app execution aliases" in Windows settings
   - Disable the "App Installer" entries for python.exe and python3.exe

---

### Issue: `python3` command not found (macOS)

**Symptoms:**
```
zsh: command not found: python3
```

**Solutions:**

1. **Install via Homebrew:**
   ```bash
   brew install python@3.11
   ```

2. **Install from python.org:**
   - Download the macOS installer from python.org
   - Run the installer

3. **Check installation path:**
   ```bash
   which python3
   ls /usr/local/bin/python*
   ```

---

### Issue: Wrong Python version

**Symptoms:**
```
$ python --version
Python 2.7.18
```

**Solutions:**

1. **Use explicit python3:**
   ```bash
   python3 --version
   ```

2. **Create alias (add to ~/.bashrc or ~/.zshrc):**
   ```bash
   alias python=python3
   alias pip=pip3
   ```

3. **Use pyenv for version management:**
   ```bash
   brew install pyenv
   pyenv install 3.11
   pyenv global 3.11
   ```

---

## Virtual Environment Issues

### Issue: `python -m venv` fails

**Symptoms:**
```
Error: Command '...' returned non-zero exit status 1
```
or
```
The virtual environment was not created successfully
```

**Solutions:**

1. **Install venv package (Linux):**
   ```bash
   sudo apt install python3.11-venv
   ```

2. **Use full path to Python:**
   ```bash
   /usr/bin/python3.11 -m venv venv
   ```

3. **Delete and recreate:**
   ```bash
   rm -rf venv
   python3 -m venv venv
   ```

---

### Issue: `source venv/bin/activate` fails (Windows)

**Symptoms:**
```
source: command not found
```

**Solutions:**

**Windows uses different activation commands:**

```cmd
# Command Prompt
venv\Scripts\activate.bat

# PowerShell
venv\Scripts\Activate.ps1

# Git Bash
source venv/Scripts/activate
```

---

### Issue: PowerShell Execution Policy Error

**Symptoms:**
```
venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled
```

**Solutions:**

1. **Change execution policy (run as Administrator):**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Or use Command Prompt instead:**
   ```cmd
   venv\Scripts\activate.bat
   ```

---

### Issue: venv not activating (no `(venv)` prefix)

**Symptoms:**
- No `(venv)` in prompt
- `pip install` installs globally

**Solutions:**

1. **Check current Python:**
   ```bash
   # macOS/Linux
   which python
   # Should show: /path/to/project/venv/bin/python

   # Windows
   where python
   # Should show: C:\path\to\project\venv\Scripts\python.exe
   ```

2. **Re-activate:**
   ```bash
   deactivate  # if currently in another venv
   source venv/bin/activate
   ```

3. **Check if venv exists:**
   ```bash
   ls venv/bin/  # macOS/Linux
   dir venv\Scripts\  # Windows
   ```

---

## Django Installation Issues

### Issue: `pip install django` fails

**Symptoms:**
```
ERROR: Could not install packages due to an EnvironmentError
```

**Solutions:**

1. **Ensure venv is activated:**
   ```bash
   source venv/bin/activate
   pip install django
   ```

2. **Upgrade pip first:**
   ```bash
   pip install --upgrade pip
   pip install django
   ```

3. **Use --user flag (not recommended, prefer venv):**
   ```bash
   pip install --user django
   ```

4. **Check network/proxy:**
   ```bash
   pip install django --proxy http://proxy:port
   ```

---

### Issue: `django-admin` command not found

**Symptoms:**
```
django-admin: command not found
```

**Solutions:**

1. **Use Python module syntax:**
   ```bash
   python -m django startproject myproject
   ```

2. **Check if Django is installed:**
   ```bash
   pip list | grep -i django
   python -c "import django; print(django.get_version())"
   ```

3. **Ensure venv is activated** (most common cause)

---

## Django Project Issues

### Issue: "You have unapplied migrations" warning

**Symptoms:**
```
You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth...
```

**Solution:**
```bash
python manage.py migrate
```

This is normal on a fresh project. Django's built-in apps need database tables.

---

### Issue: Port 8000 already in use

**Symptoms:**
```
Error: That port is already in use.
```

**Solutions:**

1. **Use a different port:**
   ```bash
   python manage.py runserver 8001
   ```

2. **Find and kill the process:**
   ```bash
   # macOS/Linux
   lsof -i :8000
   kill -9 <PID>

   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

3. **Previous Django server still running?** Check other terminal windows.

---

### Issue: "DisallowedHost" error

**Symptoms:**
```
DisallowedHost at /
Invalid HTTP_HOST header: 'your-domain.com'
```

**Solution:**
```python
# settings.py
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'your-domain.com']

# For development only:
ALLOWED_HOSTS = ['*']  # Never use in production!
```

---

### Issue: Page not found (404) on your view

**Checklist:**

1. **URL pattern correct?**
   - Check trailing slash: `/polls/` not `/polls`
   - Check for typos

2. **App URLs included?**
   ```python
   # project/urls.py
   path('polls/', include('polls.urls')),  # Did you add this?
   ```

3. **App registered?**
   ```python
   # settings.py
   INSTALLED_APPS = [
       ...
       'polls',  # Is your app here?
   ]
   ```

4. **URL file exists?**
   - Did you create `polls/urls.py`?

5. **Server restarted?** Sometimes needed after URL changes.

---

### Issue: "No module named 'myapp'"

**Symptoms:**
```
ModuleNotFoundError: No module named 'polls'
```

**Solutions:**

1. **Check you're in the right directory:**
   ```bash
   ls  # Should see manage.py
   ```

2. **Check app was created:**
   ```bash
   ls polls/  # Should see views.py, models.py, etc.
   ```

3. **Check INSTALLED_APPS spelling:**
   ```python
   # Correct
   'polls',

   # Wrong
   'poll',  # Missing 's'
   'polls.apps.PollsConfig',  # Only if apps.py is configured
   ```

---

### Issue: ModuleNotFoundError when including app URLs

**Symptoms:**
```
ModuleNotFoundError: No module named 'restaurantproject.menu'
```

Full traceback shows error in `menu/urls.py`:
```
File "/path/to/menu/urls.py", line 3, in <module>
    from restaurantproject.menu import views
ModuleNotFoundError: No module named 'restaurantproject.menu'
```

**Cause:**

Using **absolute import** instead of **relative import** in your app's `urls.py`:

```python
# ❌ WRONG - Absolute import (hardcodes project name)
from restaurantproject.menu import views

# ✅ CORRECT - Relative import (portable, works everywhere)
from . import views
```

**Why does this happen?**

Django apps are designed to be **reusable and portable**. When you write `from restaurantproject.menu import views`, you're hardcoding the project name. If you:
- Rename the project
- Copy the app to another project
- Your colleague clones with a different folder name

...the import breaks!

**The Solution:**

Use **relative imports** with the dot (`.`) notation:

```python
# menu/urls.py

from django.urls import path
from . import views  # "." means "current package" (menu/)

urlpatterns = [
    path('', views.home, name='home'),
]
```

**Understanding the dot notation:**

| Import | Meaning |
|--------|---------|
| `from . import views` | Import `views` from current directory |
| `from .views import home` | Import `home` function from `views.py` in current directory |
| `from .. import something` | Import from parent directory (rarely needed) |

**Key concept:** The `.` (dot) means "relative to where this file is located" — it's like saying `./views.py` in terminal paths.

---

### Issue: Changes not reflecting in browser

**Solutions:**

1. **Hard refresh browser:**
   - Mac: `Cmd + Shift + R`
   - Windows: `Ctrl + Shift + R`

2. **Clear browser cache**

3. **Check runserver output for errors**

4. **Django auto-reloads, but sometimes:**
   ```bash
   # Stop server (Ctrl+C) and restart
   python manage.py runserver
   ```

5. **Check you're editing the right file** (common with multiple terminals/editors)

---

## General Debugging Tips

### Print Debugging
```python
def my_view(request):
    print("=== DEBUG ===")
    print(f"Method: {request.method}")
    print(f"Path: {request.path}")
    print("=== END DEBUG ===")
    return HttpResponse("Hello")
```
Check terminal output where runserver is running.

### Django Shell
```bash
python manage.py shell
>>> from polls.views import index
>>> # Test things interactively
```

### Check Django Version
```bash
python -m django --version
```

### Verify All Imports Work
```bash
python manage.py check
```

---

## Quick Reference: Common Commands

```bash
# Python & venv
python3 --version                    # Check version
python3 -m venv venv                 # Create venv
source venv/bin/activate             # Activate (macOS/Linux)
venv\Scripts\activate                # Activate (Windows)
deactivate                           # Deactivate
pip install django                   # Install Django
pip freeze > requirements.txt        # Save dependencies

# Django
django-admin startproject myproject  # Create project
python manage.py startapp myapp      # Create app
python manage.py runserver           # Start server
python manage.py runserver 8001      # Different port
python manage.py migrate             # Apply migrations
python manage.py check               # Verify configuration
```

---

## Still Stuck?

1. **Read the error message carefully** - Django errors are usually descriptive
2. **Google the exact error message** - Someone has seen it before
3. **Check Django documentation** - docs.djangoproject.com
4. **Stack Overflow** - Most issues have been answered
5. **Ask in class Slack/Discord** - Classmates might have solved it

---

*Last updated: Class 4 - Django Apps, Views & URLs*
