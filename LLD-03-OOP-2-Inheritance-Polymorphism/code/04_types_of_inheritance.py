"""
Types of Inheritance
====================
- Single inheritance: one parent, one child
- Multilevel inheritance: grandparent -> parent -> child
- Multiple inheritance: child inherits from TWO parents
- MRO (Method Resolution Order): how Python decides which method to call

Run: python 04_types_of_inheritance.py
"""


# ============================================================
# 1. Single Inheritance: Animal -> Dog
# ============================================================
print("=" * 60)
print("1. Single Inheritance: Animal -> Dog")
print("=" * 60)
print()


class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return f"{self.name} makes a sound"

    def eat(self):
        return f"{self.name} is eating"


class Dog(Animal):
    def speak(self):
        return f"{self.name} says: Woof!"

    def fetch(self):
        return f"{self.name} fetches the ball!"


dog = Dog("Bruno")
print(f"dog.speak() -> {dog.speak()}")   # overridden
print(f"dog.eat()   -> {dog.eat()}")     # inherited
print(f"dog.fetch() -> {dog.fetch()}")   # new in Dog
print()
print("Diagram: Animal -> Dog")
print("This is the most common type. Use it by default.")
print()


# ============================================================
# 2. Multilevel Inheritance: Animal -> Dog -> GuideDog
# ============================================================
print("=" * 60)
print("2. Multilevel Inheritance: Animal -> Dog -> GuideDog")
print("=" * 60)
print()


class GuideDog(Dog):
    def __init__(self, name, owner):
        super().__init__(name)
        self.owner = owner

    def guide(self):
        return f"{self.name} is guiding {self.owner} safely"


guide = GuideDog("Rex", "Ananya")
print(f"guide.speak() -> {guide.speak()}")   # from Dog (override of Animal)
print(f"guide.eat()   -> {guide.eat()}")     # from Animal (grandparent!)
print(f"guide.fetch() -> {guide.fetch()}")   # from Dog
print(f"guide.guide() -> {guide.guide()}")   # from GuideDog itself
print()
print("Diagram: Animal -> Dog -> GuideDog")
print("GuideDog inherits from Dog, which inherits from Animal.")
print("It gets methods from ALL ancestors.")
print()


# ============================================================
# 3. Multiple Inheritance: FlyingCar(Car, Plane)
# ============================================================
print("=" * 60)
print("3. Multiple Inheritance: FlyingCar(Car, Plane)")
print("=" * 60)
print()


class Car:
    def __init__(self):
        self.wheels = 4

    def drive(self):
        return "Driving on the road"

    def start(self):
        return "Car engine started (vroom!)"


class Plane:
    def __init__(self):
        self.wings = 2

    def fly(self):
        return "Flying in the sky"

    def start(self):
        return "Plane engine started (whoosh!)"


class FlyingCar(Car, Plane):
    """Inherits from BOTH Car and Plane."""

    def __init__(self):
        super().__init__()  # calls Car.__init__ (first parent in MRO)

    def transform(self):
        return "Transforming between car and plane mode!"


fc = FlyingCar()
fc.start() # come from car

plane = Plane()
FlyingCar.start(plane) # still come from car

print(Plane.start(fc))

print(f"fc.drive()     -> {fc.drive()}")       # from Car
print(f"fc.fly()       -> {fc.fly()}")         # from Plane
print(f"fc.transform() -> {fc.transform()}")   # from FlyingCar
print()

# Both Car and Plane have start() -- which one wins?
print(f"fc.start()     -> {fc.start()}")
print()
print("Both Car and Plane have start(). Python picks Car's version.")
print("Why? Because of the MRO (Method Resolution Order).")
print()


# ============================================================
# 4. MRO -- Method Resolution Order
# ============================================================
print("=" * 60)
print("4. MRO -- Method Resolution Order")
print("=" * 60)
print()
print("When Python looks for a method, it follows a specific order.")
print("You can see this order using __mro__:")
print()

print("FlyingCar MRO:")
for i, cls in enumerate(FlyingCar.__mro__):
    print(f"  {i + 1}. {cls.__name__}")

print()
print("Python checks: FlyingCar -> Car -> Plane -> object")
print("Since Car comes before Plane, Car.start() wins.")
print()

print("GuideDog MRO:")
for i, cls in enumerate(GuideDog.__mro__):
    print(f"  {i + 1}. {cls.__name__}")
print()

print("Dog MRO (for comparison):")
for i, cls in enumerate(Dog.__mro__):
    print(f"  {i + 1}. {cls.__name__}")
print()


# ============================================================
# 5. Practical advice
# ============================================================
print("=" * 60)
print("5. Practical Advice")
print("=" * 60)
print()
print("  Single inheritance   -> Use it freely. It's clean and simple.")
print("  Multilevel (2-3)     -> Fine, but don't go deeper than 3 levels.")
print("  Multiple inheritance -> Use sparingly. It gets confusing fast.")
print()
print("In Django, you'll mostly see single inheritance:")
print("  class Dish(models.Model):    # single inheritance")
print("  class DishSerializer(serializers.ModelSerializer):  # single")
print()
print("Multiple inheritance shows up in 'mixins' (we'll cover later):")
print("  class DishView(LoginRequiredMixin, ListView):  # mixin pattern")
