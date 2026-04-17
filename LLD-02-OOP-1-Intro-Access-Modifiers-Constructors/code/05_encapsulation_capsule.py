"""
05 - Encapsulation: Bundle and Protect
=======================================
Like a medicine capsule:
  1. Holds things TOGETHER   → class bundles attributes + methods
  2. PROTECTS from outside   → __private attributes
  3. CONTROLLED interface    → methods with validation

Each aspect is shown with arrows in the code.
"""

# =============================================
# WITHOUT Encapsulation — no capsule
# =============================================

print("=== WITHOUT Encapsulation ===\n")

# Data floating as a global variable
account_balance = 5000

# Function floating separately
def withdraw_no_capsule(amount):
    global account_balance
    account_balance -= amount

# Problem: anyone can break this
account_balance = -99999  # No capsule = no protection!
print(f"Balance set to: {account_balance}")
print("No bundling, no protection, no validation.\n")


# =============================================
# WITH Encapsulation — the capsule approach
# =============================================

print("=== WITH Encapsulation ===\n")


class BankAccount:                    # ← THE CAPSULE (holds everything together)

    def __init__(self, owner, balance):
        self.owner = owner
        self.__balance = balance      # ← PROTECTED INSIDE (can't tamper from outside)

    def withdraw(self, amount):       # ← CONTROLLED INTERFACE
        if amount <= 0:               #    (validates before modifying)
            raise ValueError("Amount must be positive")
        if amount > self.__balance:
            raise ValueError(f"Insufficient funds (balance: {self.__balance})")
        self.__balance -= amount
        print(f"  Withdrew Rs.{amount}. Remaining: Rs.{self.__balance}")

    def deposit(self, amount):        # ← CONTROLLED INTERFACE
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self.__balance += amount
        print(f"  Deposited Rs.{amount}. New balance: Rs.{self.__balance}")

    def get_balance(self):            # ← CONTROLLED INTERFACE (read-only)
        return self.__balance


# --- Capsule Aspect 1: HOLDS THINGS TOGETHER ---
print("1. BUNDLING: owner, balance, withdraw(), deposit() — all in one class")
account = BankAccount("Rahul", 5000)

# --- Capsule Aspect 2: PROTECTS FROM OUTSIDE ---
print("\n2. PROTECTION: Can't directly modify __balance")
try:
    print(f"   account.__balance → ", end="")
    print(account.__balance)
except AttributeError as e:
    print(f"AttributeError! (protected)")

# This creates a NEW attribute, doesn't change the real one
account.__balance = -99999
print(f"   account.__balance = -99999 → new attr, not the real one")
print(f"   Real balance: Rs.{account.get_balance()}")  # Unchanged!

# --- Capsule Aspect 3: CONTROLLED INTERFACE ---
print("\n3. CONTROLLED INTERFACE: Must use methods")
account.deposit(2000)
account.withdraw(1000)

# Validation catches bad values
print("\n   Validation in action:")
try:
    account.withdraw(-500)
except ValueError as e:
    print(f"   withdraw(-500) → {e}")

try:
    account.withdraw(999999)
except ValueError as e:
    print(f"   withdraw(999999) → {e}")

print(f"\n   Final balance: Rs.{account.get_balance()}")
print("   The capsule held! Data is safe.")


# =============================================
# RECAP: How the capsule maps to Python
# =============================================

print("\n" + "=" * 55)
print("CAPSULE → PYTHON MAPPING:")
print("=" * 55)
print()
print("Medicine capsule     →  Python class")
print("  Shell              →  class BankAccount:")
print("  Ingredients inside →  self.__balance (private attribute)")
print("  Swallow capsule    →  account.withdraw(1000) (method)")
print("  Can't open capsule →  account.__balance → AttributeError")
