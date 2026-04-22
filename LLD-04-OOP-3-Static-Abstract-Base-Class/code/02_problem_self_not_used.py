"""The problem: self is required but never used."""

class MenuItem:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def is_valid_price(self, price):  # self is here but NEVER used
        return isinstance(price, (int, float)) and price > 0

# You must create a useless object just to call validation:
temp = MenuItem("temp", 0)
print(temp.is_valid_price(300))  # True — but why did we need an object?
print(temp.is_valid_price(-50))  # False

# This is wasteful. is_valid_price doesn't use self at all.
