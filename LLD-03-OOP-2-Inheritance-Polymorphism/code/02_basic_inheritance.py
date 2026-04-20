"""
Basic Inheritance -- Syntax and Mechanics
==========================================
- class Child(Parent) syntax
- super().__init__() to call the parent constructor
- Child inherits parent methods
- Child can add NEW methods
- isinstance() and issubclass() checks

Run: python 02_basic_inheritance.py
"""


# ============================================================
# 1. The syntax: class Child(Parent)
# ============================================================
print("=" * 60)
print("1. Syntax: class Child(Parent)")
print("=" * 60)
print()


class DeliveryPerson:
    """Parent class for all delivery staff."""

    def __init__(self, name, phone):
        self.name = name
        self.phone = phone

    def introduce(self):
        return f"Hi, I'm {self.name}. Call me at {self.phone}."

    def deliver(self, item):
        return f"{self.name} is delivering: {item}"


class BikeDelivery(DeliveryPerson):
    """Child class -- inherits everything from DeliveryPerson."""
    pass  # no extra code yet -- still a valid class!


rider = BikeDelivery("Rahul", "9876543210")
print(f"rider.introduce() -> {rider.introduce()}")
print(f"rider.deliver('Pizza') -> {rider.deliver('Pizza')}")
print()
print("BikeDelivery has ZERO code of its own, but it works!")
print("It inherited __init__, introduce, and deliver from DeliveryPerson.")
print()


# ============================================================
# 2. super().__init__() -- calling the parent constructor
# ============================================================
print("=" * 60)
print("2. super().__init__() -- Calling the Parent Constructor")
print("=" * 60)
print()


class CarDelivery(DeliveryPerson):
    """Adds car-specific attributes while reusing parent's __init__."""

    def __init__(self, name, phone, car_model):
        super().__init__(name, phone)  # parent handles name & phone
        self.car_model = car_model     # we handle car-specific stuff

    def vehicle_info(self):
        return f"{self.name} drives a {self.car_model}"


driver = CarDelivery("Amit", "9123456789", "Swift Dzire")
print(f"driver.name       -> {driver.name}")        # from parent
print(f"driver.phone      -> {driver.phone}")        # from parent
print(f"driver.car_model  -> {driver.car_model}")    # from child
print(f"driver.introduce() -> {driver.introduce()}")  # inherited method
print(f"driver.vehicle_info() -> {driver.vehicle_info()}")  # new method
print()
print("super().__init__(name, phone) says:")
print("  'Hey Parent, please do YOUR setup first. I'll add mine after.'")
print()


# ============================================================
# 3. Child inherits parent methods
# ============================================================
print("=" * 60)
print("3. Child Inherits Parent Methods")
print("=" * 60)
print()

print(f"driver.deliver('Biryani') -> {driver.deliver('Biryani')}")
print()
print("We never wrote a deliver() method in CarDelivery.")
print("Python looks up the chain: CarDelivery -> DeliveryPerson -> found it!")
print()


# ============================================================
# 4. Child can add NEW methods
# ============================================================
print("=" * 60)
print("4. Child Can Add NEW Methods")
print("=" * 60)
print()


class DroneDelivery(DeliveryPerson):
    """Adds drone-specific capabilities."""

    def __init__(self, name, phone, max_altitude_m):
        super().__init__(name, phone)
        self.max_altitude_m = max_altitude_m

    def fly(self):
        return f"Drone '{self.name}' flying at {self.max_altitude_m}m altitude!"


drone = DroneDelivery("SkyBot-7", "N/A", 120)
print(f"drone.introduce() -> {drone.introduce()}")  # inherited
print(f"drone.fly()       -> {drone.fly()}")          # new method
print()

# Parent doesn't have the child's method
person = DeliveryPerson("Priya", "9999999999")
try:
    person.fly()
except AttributeError as e:
    print(f"person.fly() -> AttributeError: {e}")
    print("Parent does NOT get child's methods. Inheritance is one-way (downward).")
print()


# ============================================================
# 5. isinstance() and issubclass()
# ============================================================
print("=" * 60)
print("5. isinstance() and issubclass()")
print("=" * 60)
print()

print("isinstance() -- Is this OBJECT a type of ...?")
print(f"  isinstance(driver, CarDelivery)     -> {isinstance(driver, CarDelivery)}")
print(f"  isinstance(driver, DeliveryPerson)  -> {isinstance(driver, DeliveryPerson)}")
print(f"  isinstance(driver, DroneDelivery)   -> {isinstance(driver, DroneDelivery)}")
print()
print("A CarDelivery IS a DeliveryPerson (child is a type of parent).")
print("A CarDelivery is NOT a DroneDelivery (siblings are not related).")
print()

print("issubclass() -- Is this CLASS a subclass of ...?")
print(f"  issubclass(CarDelivery, DeliveryPerson)  -> {issubclass(CarDelivery, DeliveryPerson)}")
print(f"  issubclass(DeliveryPerson, CarDelivery)  -> {issubclass(DeliveryPerson, CarDelivery)}")
print(f"  issubclass(CarDelivery, CarDelivery)     -> {issubclass(CarDelivery, CarDelivery)}")
print()
print("Every class is a subclass of itself.")
print("Parent is NOT a subclass of Child.")
