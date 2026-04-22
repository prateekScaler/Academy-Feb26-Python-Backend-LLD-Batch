"""@staticmethod — no self needed, no object needed."""

class MenuItem:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    @staticmethod
    def is_valid_price(price):  # no self!
        return isinstance(price, (int, float)) and price > 0

    @staticmethod
    def format_currency(amount):
        return f"Rs.{amount:.2f}"

# Call on the CLASS — no object needed:
print(MenuItem.is_valid_price(300))      # True
print(MenuItem.is_valid_price(-50))      # False
print(MenuItem.format_currency(299.5))   # Rs.299.50

# Also works on an instance (but unnecessary):
item = MenuItem("Biryani", 300)
print(item.is_valid_price(300))          # True
