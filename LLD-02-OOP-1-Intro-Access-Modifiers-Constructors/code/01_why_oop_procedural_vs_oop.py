"""
01 - Why OOP: Procedural vs Object-Oriented
============================================
Shows the problems with using plain dicts and functions,
then solves them with a class.
"""

# =============================================
# PART 1: Procedural Approach (The Problems)
# =============================================

customer1 = {"name": "Rahul", "email": "rahul@gmail.com", "balance": 5000}
customer2 = {"name": "Priya", "email": "priya@gmail.com", "balance": 3000}


def withdraw(customer, amount):
    """Withdraw money from a customer dict."""
    if amount > customer["balance"]:
        print("Insufficient funds")
        return
    customer["balance"] -= amount


def get_full_info(customer):
    return f"{customer['name']} ({customer['email']}) - Rs.{customer['balance']}"




# Problem 1: No protection — anyone can set balance to anything
customer1["balance"] = -99999
print(f"Balance after direct modification: {customer1['balance']}")  # -99999!

# Problem 2: Typos fail silently — creates a new key instead of erroring
customer1["balance"] = 5000  # fix it back
customer1["blance"] = 9999  # typo — no error, just a useless new key
print(f"Keys in customer1: {list(customer1.keys())}")  # includes 'blance'!

# Problem 3: Can delete required keys — breaks other functions
customer_copy = {"name": "Test", "email": "test@test.com", "balance": 100}
del customer_copy["email"]
try:
    print(get_full_info(customer_copy))  # KeyError!
except KeyError as e:
    print(f"Crashed because key was deleted: {e}")

# Problem 4: Functions aren't tied to data
random_dict = {"color": "red", "size": 5}
withdraw(random_dict, 3)  # This runs! But it makes no sense.
print(f"Random dict after withdraw: {random_dict}")  # {'color': 'red', 'size': 5, ...} — KeyError!


print("\n" + "=" * 50)
print("PART 2: OOP Approach (The Solution)")
print("=" * 50 + "\n")


# =============================================
# PART 2: OOP Approach (The Solution)
# =============================================

class Customer:
    def __init__(self, name, email, balance):
        self.name = name
        self.email = email
        self.__balance = balance  # Private — can't be set to -99999

    def withdraw(self, amount):
        """Withdraw money with validation."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > self.__balance:
            raise ValueError("Insufficient funds")
        self.__balance -= amount
        print(f"Withdrew Rs.{amount}. New balance: Rs.{self.__balance}")

    def get_balance(self):
        return self.__balance

    def get_full_info(self):
        return f"{self.name} ({self.email}) - Rs.{self.__balance}"


# Benefit 1: Data and behavior bundled together
rahul = Customer("Rahul", "rahul@gmail.com", 5000)
rahul.withdraw(1000)  # Works — goes through validation
print(f"Balance: Rs.{rahul.get_balance()}")

# Benefit 2: Protection — private attribute
rahul.__balance = -99999  # This creates a NEW attribute, doesn't modify the real one
print(f"Real balance unchanged: Rs.{rahul.get_balance()}")  # Still 4000!

# Benefit 3: Validation enforced
try:
    rahul.withdraw(999999)
except ValueError as e:
    print(f"Validation caught: {e}")

try:
    rahul.withdraw(-500)
except ValueError as e:
    print(f"Validation caught: {e}")

# Benefit 4: Structure is defined
print(f"\nFull info: {rahul.get_full_info()}")
