"""Instance methods need self — you MUST create an object first."""

class MenuItem:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def describe(self):  # needs self
        return f"{self.name} - Rs.{self.price}"

# Must create an object:
item = MenuItem("Biryani", 300)
print(item.describe())  # "Biryani - Rs.300"

# Can't call without an object:
try:
    MenuItem.describe()
except TypeError as e:
    print(f"MenuItem.describe() → {e}")
