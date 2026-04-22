"""Why cls matters: inheritance."""

class MenuItem:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    @classmethod
    def from_dict(cls, data):
        print(f"  cls = {cls.__name__}")
        return cls(data["name"], data["price"])  # cls, NOT MenuItem

class Food(MenuItem):
    pass

# Food inherits from_dict. cls = Food, not MenuItem:
f = Food.from_dict({"name": "Biryani", "price": 300})
print(f"  type(f) = {type(f).__name__}")  # Food, not MenuItem!

# If we'd written MenuItem(...) instead of cls(...), f would be MenuItem.
