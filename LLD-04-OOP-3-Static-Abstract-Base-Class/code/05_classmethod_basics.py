"""@classmethod — gets cls (the class) instead of self (an instance)."""

class MenuItem:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["price"])  # cls = MenuItem

    @classmethod
    def from_csv(cls, line):
        name, price = line.split(",")
        return cls(name.strip(), float(price))

# Three ways to create:
m1 = MenuItem("Biryani", 300)
m2 = MenuItem.from_dict({"name": "Biryani", "price": 300})
m3 = MenuItem.from_csv("Biryani, 300")

print(m1.name, m2.name, m3.name)  # All "Biryani"
