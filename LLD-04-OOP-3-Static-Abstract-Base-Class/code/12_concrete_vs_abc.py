"""When to use concrete inheritance vs ABC."""
from abc import ABC, abstractmethod

# CONCRETE: parent has working implementation
class MenuItem:
    def __init__(self, name, price):
        self.name = name
        self.price = price
    def describe(self):
        return f"{self.name} - Rs.{self.price}"

class Food(MenuItem):
    pass  # describe() works — inherited as-is

print(Food("Biryani", 300).describe())  # Works without override

# ABC: parent defines contract only
class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount): pass

class Razorpay(PaymentGateway):
    def charge(self, amount):
        print(f"Razorpay charged Rs.{amount}")

try:
    PaymentGateway()  # Can't create — it's abstract
except TypeError as e:
    print(f"PaymentGateway() → {e}")

Razorpay().charge(500)  # Works — implements charge()

print("\nConcrete = shared defaults, children CAN override")
print("ABC = contract only, children MUST implement")
