"""
07 - Access Modifiers: Public, Protected, Private
===================================================
Python uses naming conventions, not compiler enforcement.
  self.name      → Public    (anyone)
  self._name     → Protected (convention: internal use)
  self.__name    → Private   (name mangling)
"""


class BankAccount:
    def __init__(self, owner, balance, account_type="savings"):
        self.owner = owner                # Public
        self._account_type = account_type  # Protected
        self.__balance = balance          # Private

    def get_balance(self):
        return self.__balance

    def __str__(self):
        return f"BankAccount({self.owner}, {self._account_type}, Rs.{self.__balance})"


account = BankAccount("Rahul", 5000)
print(f"Account: {account}\n")


# =============================================
# PUBLIC: self.owner — anyone can access
# =============================================

print("=== PUBLIC (self.owner) ===")
print(f"Read:  account.owner = {account.owner}")
account.owner = "Priya"
print(f"Write: account.owner = {account.owner}")
print("No restrictions. Anyone can read and write.\n")


# =============================================
# PROTECTED: self._account_type — convention only
# =============================================

print("=== PROTECTED (self._account_type) ===")
print(f"Read:  account._account_type = {account._account_type}")
account._account_type = "current"
print(f"Write: account._account_type = {account._account_type}")
print("Python doesn't stop you. But the single underscore signals:")
print("  'This is internal. Don't touch unless you're a subclass.'\n")


# =============================================
# PRIVATE: self.__balance — name mangling
# =============================================

print("=== PRIVATE (self.__balance) ===")

# Direct access fails
try:
    print(account.__balance)
except AttributeError as e:
    print(f"account.__balance → AttributeError: {e}")

# Name mangling: Python renames __balance to _BankAccount__balance
print(f"account._BankAccount__balance = {account._BankAccount__balance}")
print("Python RENAMES it, doesn't truly hide it.\n")


# =============================================
# What's in the object? Let's look.
# =============================================

print("=== What attributes does the object have? ===")
attrs = [a for a in dir(account) if not a.startswith('__') or a == '__balance']
real_attrs = [a for a in account.__dict__]
print(f"account.__dict__ = {account.__dict__}")
print()
print("Notice:")
print("  - 'owner' is stored as 'owner'")
print("  - '_account_type' is stored as '_account_type'")
print("  - '__balance' is stored as '_BankAccount__balance'  ← name mangled!")


# =============================================
# The gotcha: setting __balance from outside
# =============================================

print("\n=== The Gotcha ===")
account.__balance = -99999
print(f"account.__balance = {account.__balance}")  # -99999
print(f"account.get_balance() = {account.get_balance()}")  # Still 5000!
print(f"account.__dict__ = {account.__dict__}")
print()
print("Setting account.__balance creates a NEW attribute '__balance'.")
print("The REAL balance is stored as '_BankAccount__balance'.")
print("They're different attributes!")
