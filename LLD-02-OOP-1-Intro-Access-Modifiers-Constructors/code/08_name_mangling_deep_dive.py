"""
08 - Name Mangling: Why Python Allows Access to "Private" Attributes
=====================================================================
Python's philosophy: "We're all consenting adults here."
Name mangling prevents ACCIDENTS, not ATTACKS.
"""


# =============================================
# What is name mangling?
# =============================================

print("=== What is Name Mangling? ===\n")


class Secret:
    def __init__(self):
        self.__password = "hunter2"
        self.__api_key = "sk_secret_12345"


s = Secret()

# What you think is happening:
#   self.__password is stored as __password (hidden)

# What's ACTUALLY happening:
#   self.__password is stored as _Secret__password (renamed)

print("What Python actually stores:")
print(f"  s.__dict__ = {s.__dict__}")
print()

# Direct access fails (the name doesn't match)
try:
    print(s.__password)
except AttributeError:
    print("s.__password → AttributeError (name doesn't exist as-is)")

# But the mangled name works
print(f"s._Secret__password → {s._Secret__password}")
print(f"s._Secret__api_key  → {s._Secret__api_key}")


# =============================================
# WHY does Python do this? (Not for security!)
# =============================================

print("\n=== Why Name Mangling Exists ===\n")
print("Name mangling was NOT designed for security.")
print("It was designed to prevent NAME COLLISIONS in inheritance.\n")


class Parent:
    def __init__(self):
        self.__value = "parent_value"

    def get_parent_value(self):
        return self.__value  # Accesses _Parent__value


class Child(Parent):
    def __init__(self):
        super().__init__()
        self.__value = "child_value"  # This is _Child__value, NOT _Parent__value

    def get_child_value(self):
        return self.__value  # Accesses _Child__value


c = Child()
print(f"Parent's __value: {c.get_parent_value()}")  # "parent_value"
print(f"Child's __value:  {c.get_child_value()}")   # "child_value"
print(f"They don't collide! Stored as:")
print(f"  {c.__dict__}")
print()
print("Without name mangling, Child's __value would OVERWRITE Parent's __value.")
print("Name mangling keeps them separate by adding the class name as a prefix.")


# =============================================
# Prevention of ACCIDENTS, not ATTACKS
# =============================================

print("\n=== Accidents vs Attacks ===\n")


class User:
    def __init__(self, name, is_admin):
        self.name = name
        self.__is_admin = is_admin

    def check_admin(self):
        return self.__is_admin


user = User("Rahul", False)

# Accidental access — PREVENTED by name mangling
# A developer typing quickly won't accidentally write:
#   user.__is_admin = True  (this creates a new attr, doesn't change the real one)

user.__is_admin = True  # Creates a DIFFERENT attribute
print(f"user.__is_admin (new attr):  {user.__is_admin}")
print(f"user.check_admin() (real):   {user.check_admin()}")  # Still False!

# Intentional access — POSSIBLE (for debugging/testing)
user._User__is_admin = True  # This actually changes it
print(f"After _User__is_admin = True: {user.check_admin()}")  # Now True

print()
print("Key insight:")
print("  Nobody ACCIDENTALLY types 'user._User__is_admin = True'")
print("  But they might accidentally type 'user.__is_admin = True'")
print("  Name mangling makes the ACCIDENT harmless (creates a new attr)")
print("  while keeping INTENTIONAL access possible (debugging, testing)")
