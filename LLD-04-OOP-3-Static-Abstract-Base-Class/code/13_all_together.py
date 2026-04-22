"""Static + Class + Abstract — all in one class."""
from abc import ABC, abstractmethod

class MenuItem(ABC):
    def __init__(self, name, price):
        if not MenuItem.is_valid_price(price):
            raise ValueError(f"Invalid price: {price}")
        self.name = name
        self.price = price

    @abstractmethod
    def calculate_price(self): pass

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["price"])

    @staticmethod
    def is_valid_price(price):
        return isinstance(price, (int, float)) and price > 0

class Food(MenuItem):
    def calculate_price(self):
        return self.price * 1.05  # 5% GST

class Beverage(MenuItem):
    def calculate_price(self):
        return self.price + 10  # Container deposit

# Static: validate without object
print(f"Valid price? {MenuItem.is_valid_price(300)}")

# Classmethod: create from dict
biryani = Food.from_dict({"name": "Biryani", "price": 300})
print(f"{biryani.name}: Rs.{biryani.calculate_price()}")

# Abstract: MenuItem can't be created directly
try:
    MenuItem("Test", 100)
except TypeError as e:
    print(f"MenuItem() → {e}")
