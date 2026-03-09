# Troubleshooting Guide: Class 5

Common issues with Django Models, Migrations, and Admin.

---

## Migration Issues

### Issue: "No changes detected" when running makemigrations

**Symptoms:**
```
No changes detected
```

**Solutions:**

1. **Check app is registered in INSTALLED_APPS:**
   ```python
   # settings.py
   INSTALLED_APPS = [
       ...
       'menu',  # Is your app here?
   ]
   ```

2. **Specify the app name:**
   ```bash
   python manage.py makemigrations menu
   ```

3. **Check models.py has models inheriting from models.Model:**
   ```python
   # Correct
   class MenuItem(models.Model):
       pass

   # Wrong - won't be detected
   class MenuItem:
       pass
   ```

---

### Issue: "No such table" error

**Symptoms:**
```
django.db.utils.OperationalError: no such table: menu_menuitem
```

**Solution:**
```bash
python manage.py migrate
```

If that doesn't work:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

### Issue: "Column does not exist" after adding a field

**Symptoms:**
```
OperationalError: no such column: menu_menuitem.new_field
```

**Solution:**
```bash
# Create migration for the new field
python manage.py makemigrations

# Apply it
python manage.py migrate
```

---

### Issue: Migration asks for default value

**Symptoms:**
```
You are trying to add a non-nullable field 'category' to menuitem without a default...
```

**Solutions:**

1. **Provide a one-off default:**
   ```
   Select an option: 1
   >>> 1  # Use 1 as the category_id for existing rows
   ```

2. **Or add null=True to the field:**
   ```python
   category = models.ForeignKey(Category, null=True, on_delete=models.CASCADE)
   ```

3. **Or add a default:**
   ```python
   category = models.ForeignKey(Category, default=1, on_delete=models.CASCADE)
   ```

---

### Issue: "Conflicting migrations" error

**Symptoms:**
```
CommandError: Conflicting migrations detected
```

**Solution:**
```bash
# Merge migrations
python manage.py makemigrations --merge
python manage.py migrate
```

---

## Model Issues

### Issue: "null value in column violates not-null constraint"

**Symptoms:**
```
IntegrityError: NOT NULL constraint failed: menu_menuitem.category_id
```

**Cause:** Trying to create a MenuItem without a category.

**Solution:**
```python
# Always provide required foreign keys
category = Category.objects.first()
MenuItem.objects.create(name="Pasta", price=15.99, category=category)
```

---

### Issue: ForeignKey on_delete error

**Symptoms:**
```
TypeError: __init__() missing 1 required positional argument: 'on_delete'
```

**Solution:**

`on_delete` is required for ForeignKey:
```python
# Correct
category = models.ForeignKey(Category, on_delete=models.CASCADE)

# Wrong - missing on_delete
category = models.ForeignKey(Category)
```

---

### Issue: DecimalField precision error

**Symptoms:**
```
decimal.InvalidOperation: [<class 'decimal.ConversionSyntax'>]
```

**Cause:** Value has more digits than allowed.

**Solution:**
```python
# max_digits includes decimal places
# max_digits=6, decimal_places=2 means max 9999.99
price = models.DecimalField(max_digits=6, decimal_places=2)

# For larger values:
price = models.DecimalField(max_digits=10, decimal_places=2)  # Up to 99999999.99
```

---

## Admin Issues

### Issue: Model not showing in admin

**Solution:**

Register the model in admin.py:
```python
# menu/admin.py
from django.contrib import admin
from .models import MenuItem

admin.site.register(MenuItem)

# Or with customization:
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
```

---

### Issue: Admin shows "Categorys" instead of "Categories"

**Solution:**

Add Meta class to model:
```python
class Category(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Categories"
```

---

### Issue: Admin login not working

**Solutions:**

1. **Create superuser if you haven't:**
   ```bash
   python manage.py createsuperuser
   ```

2. **Reset password:**
   ```bash
   python manage.py changepassword admin
   ```

3. **Check user is active and staff:**
   ```bash
   python manage.py shell
   >>> from django.contrib.auth.models import User
   >>> u = User.objects.get(username='admin')
   >>> u.is_active = True
   >>> u.is_staff = True
   >>> u.is_superuser = True
   >>> u.save()
   ```

---

## QuerySet Issues

### Issue: "MenuItem matching query does not exist"

**Symptoms:**
```
menu.models.MenuItem.DoesNotExist: MenuItem matching query does not exist.
```

**Cause:** Using `.get()` for non-existent item.

**Solutions:**

1. **Use try/except:**
   ```python
   try:
       item = MenuItem.objects.get(id=999)
   except MenuItem.DoesNotExist:
       item = None
   ```

2. **Use .first() instead:**
   ```python
   item = MenuItem.objects.filter(id=999).first()  # Returns None if not found
   ```

3. **Use get_object_or_404 in views:**
   ```python
   from django.shortcuts import get_object_or_404
   item = get_object_or_404(MenuItem, id=999)  # Returns 404 response
   ```

---

### Issue: "Multiple objects returned"

**Symptoms:**
```
menu.models.MenuItem.MultipleObjectsReturned: get() returned more than one MenuItem
```

**Cause:** Using `.get()` but multiple items match.

**Solutions:**

1. **Use a unique field:**
   ```python
   item = MenuItem.objects.get(id=1)  # id is always unique
   ```

2. **Use .filter() and handle multiple:**
   ```python
   items = MenuItem.objects.filter(name="Pasta")
   item = items.first()  # Get just the first one
   ```

---

## Shell Issues

### Issue: Import error in shell

**Symptoms:**
```
>>> from menu.models import MenuItem
ImportError: No module named 'menu'
```

**Solutions:**

1. **Make sure you're in the project directory:**
   ```bash
   ls  # Should show manage.py
   ```

2. **Use Django's shell, not regular Python:**
   ```bash
   python manage.py shell  # Correct
   python  # Wrong - doesn't load Django
   ```

---

## Quick Reference: Common Commands

```bash
# Migrations
python manage.py makemigrations          # Create migration files
python manage.py migrate                 # Apply migrations
python manage.py showmigrations          # List migrations
python manage.py sqlmigrate menu 0001    # Show SQL

# Admin
python manage.py createsuperuser         # Create admin user
python manage.py changepassword admin    # Reset password

# Shell
python manage.py shell                   # Django shell
python manage.py dbshell                 # Database shell

# Reset everything (careful!)
rm db.sqlite3
rm -rf menu/migrations/0*.py
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

---

*Last updated: Class 5 - Django Models & Admin*
