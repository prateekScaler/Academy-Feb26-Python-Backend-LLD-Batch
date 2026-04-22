"""Static methods CANNOT access self or cls."""

class MenuItem:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    @staticmethod
    def broken_describe():
        try:
            return f"{self.name} - Rs.{self.price}"
        except NameError as e:
            return f"NameError: {e}"

item = MenuItem("Biryani", 300)
print(item.broken_describe())
# NameError: name 'self' is not defined
# Static methods have NO access to self. If you need self, remove @staticmethod.
