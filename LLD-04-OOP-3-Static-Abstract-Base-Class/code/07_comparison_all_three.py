"""Instance vs Static vs Class — side by side."""

class MenuItem:
    tax_rate = 0.05

    def __init__(self, name, price):
        self.name = name
        self.price = price

    def price_with_tax(self):          # INSTANCE — uses self
        return self.price * (1 + self.tax_rate)

    @staticmethod
    def is_valid_price(price):          # STATIC — no self, no cls
        return isinstance(price, (int, float)) and price > 0

    @classmethod
    def from_dict(cls, data):           # CLASS — uses cls
        return cls(data["name"], data["price"])

# Instance: needs object
item = MenuItem("Biryani", 300)
print(f"With tax: {item.price_with_tax()}")

# Static: no object needed
print(f"Valid? {MenuItem.is_valid_price(300)}")

# Class: creates object
item2 = MenuItem.from_dict({"name": "Chai", "price": 40})
print(f"From dict: {item2.name}")

print("\n--- Summary ---")
print("Instance: uses self, operates on object data")
print("Static:   no self, no cls — pure utility")
print("Class:    uses cls — alternative constructors")
