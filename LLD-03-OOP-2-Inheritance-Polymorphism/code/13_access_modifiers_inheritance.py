"""
13 - Access Modifiers in Inheritance
=====================================
How public, protected, and private attributes behave
when a child class tries to access them.

Run this file and observe:
  - Public: works everywhere
  - Protected: works in child, linter warns outside
  - Private: AttributeError in child (name mangling)
"""


# =============================================
# Parent class with all 3 access levels
# =============================================

class MenuItem:
    def __init__(self, name, price, secret_recipe):
        self.name = name                  # PUBLIC — anyone
        self._base_price = price          # PROTECTED — children + internal
        self.__secret_recipe = secret_recipe  # PRIVATE — only MenuItem

    def get_recipe(self):
        """Only MenuItem itself can access __secret_recipe."""
        return self.__secret_recipe

    def describe(self):
        return f"{self.name} - Rs.{self._base_price}"


# =============================================
# Child class trying to access parent's attributes
# =============================================

class Food(MenuItem):
    def __init__(self, name, price, secret_recipe, calories):
        super().__init__(name, price, secret_recipe)
        self.calories = calories

    def show_public(self):
        """PUBLIC: self.name — works perfectly."""
        return f"Name (public): {self.name}"

    def show_protected(self):
        """PROTECTED: self._base_price — works, but linter warns outside."""
        return f"Base price (protected): Rs.{self._base_price}"

    def calculate_price_with_tax(self):
        """PROTECTED used properly: child adds tax to parent's base price."""
        return self._base_price * 1.05  # This is WHY _protected exists

    def try_private(self):
        """PRIVATE: self.__secret_recipe — will this work?"""
        try:
            return f"Recipe (private): {self.__secret_recipe}"
        except AttributeError as e:
            return f"FAILED: {e}"


# =============================================
# DEMO: Access from INSIDE the child class
# =============================================

print("=" * 60)
print("ACCESS FROM INSIDE THE CHILD CLASS (Food)")
print("=" * 60)

biryani = Food("Biryani", 300, "secret spice mix", 450)

# Public — works
print(f"\n  {biryani.show_public()}")

# Protected — works (child CAN access parent's _protected)
print(f"  {biryani.show_protected()}")
print(f"  Price with tax: Rs.{biryani.calculate_price_with_tax()}")

# Private — FAILS
print(f"  {biryani.try_private()}")
print("  → Child CANNOT access parent's __private (name mangled)")


# =============================================
# DEMO: Access from OUTSIDE (main code)
# =============================================

print(f"\n{'=' * 60}")
print("ACCESS FROM OUTSIDE (main code)")
print("=" * 60)

# Public — works
print(f"\n  biryani.name = {biryani.name}")
print("  ✓ Public: anyone can access")

# Protected — works BUT shouldn't be used outside
print(f"\n  biryani._base_price = {biryani._base_price}")
print("  ⚠ Protected: works, but YOUR LINTER SHOULD WARN HERE")
print("    → Run: pylint or flake8 on this file to see the warning")
print("    → The underscore says 'this is internal, don't touch'")

# Private — FAILS
print(f"\n  biryani.__secret_recipe = ", end="")
try:
    print(biryani.__secret_recipe)
except AttributeError as e:
    print(f"AttributeError!")
    print(f"  ✗ Private: name mangled to _MenuItem__secret_recipe")

# But you CAN access it via the mangled name (not recommended)
print(f"\n  biryani._MenuItem__secret_recipe = {biryani._MenuItem__secret_recipe}")
print("  ✗ This works but is WRONG — never do this in real code")


# =============================================
# DEMO: Access via parent's own method
# =============================================

print(f"\n{'=' * 60}")
print("ACCESS VIA PARENT'S OWN METHOD")
print("=" * 60)

# The parent CAN access its own private attributes
print(f"\n  biryani.get_recipe() = {biryani.get_recipe()}")
print("  ✓ Parent's method can access __private (it's in the same class)")
print("  This is the CORRECT way to expose private data: through a method")


# =============================================
# SUMMARY TABLE
# =============================================

print(f"\n{'=' * 60}")
print("SUMMARY: Who can access what?")
print("=" * 60)
print()
print(f"  {'Attribute':<25} {'Inside Parent':<15} {'Inside Child':<15} {'Outside'}")
print(f"  {'-'*25} {'-'*15} {'-'*15} {'-'*15}")
print(f"  {'self.name (public)':<25} {'✓ Yes':<15} {'✓ Yes':<15} {'✓ Yes'}")
print(f"  {'self._price (protected)':<25} {'✓ Yes':<15} {'✓ Yes':<15} {'⚠ Linter warns'}")
print(f"  {'self.__secret (private)':<25} {'✓ Yes':<15} {'✗ Error':<15} {'✗ Error'}")
print()
print("  Protected (_name) is the SWEET SPOT for inheritance:")
print("  → Children need it (to extend behavior)")
print("  → Outsiders shouldn't touch it (internal detail)")
print("  → It's why _base_price exists: Food needs it for tax calculation,")
print("    but a view/template should use calculate_price_with_tax() instead")


# =============================================
# BONUS: See what Python actually stores
# =============================================

print(f"\n{'=' * 60}")
print("BONUS: What's actually stored in the object?")
print("=" * 60)
print(f"\n  biryani.__dict__ = ")
for key, value in biryani.__dict__.items():
    marker = ""
    if key.startswith("_MenuItem__"):
        marker = "  ← name mangled (private)"
    elif key.startswith("_"):
        marker = "  ← protected"
    print(f"    {key!r}: {value!r}{marker}")
