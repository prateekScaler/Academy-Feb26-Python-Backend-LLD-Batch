"""
10 - Types of Inheritance & MRO
================================
Single, Multiple, Hierarchical, Multilevel inheritance.
Method Resolution Order (MRO) — how Python decides which method to call.
"""


# =============================================
# SINGLE INHERITANCE: One parent, one child
# =============================================

print("=== Single Inheritance ===\n")


class Animal:
    def speak(self):
        return "..."


class Dog(Animal):
    def speak(self):
        return "Woof!"


dog = Dog()
print(f"  Dog speaks: {dog.speak()}")
print(f"  Dog → Animal (single chain)\n")


# =============================================
# HIERARCHICAL: One parent, MULTIPLE children
# =============================================

print("=== Hierarchical Inheritance ===\n")


class MenuItem:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def describe(self):
        return f"{self.name} - Rs.{self.price}"


class Food(MenuItem):
    pass


class Beverage(MenuItem):
    pass


class Dessert(MenuItem):
    pass


# All three inherit from MenuItem
biryani = Food("Biryani", 300)
chai = Beverage("Chai", 40)
gulab_jamun = Dessert("Gulab Jamun", 80)
print(f"  {biryani.describe()}")
print(f"  {chai.describe()}")
print(f"  {gulab_jamun.describe()}")
print("  Food, Beverage, Dessert → all inherit from MenuItem\n")


# =============================================
# MULTILEVEL: Grandparent → Parent → Child
# =============================================

print("=== Multilevel Inheritance ===\n")


class Animal2:
    def breathe(self):
        return "breathing..."


class Dog2(Animal2):
    def bark(self):
        return "Woof!"


class GuideDog(Dog2):
    def guide(self):
        return "guiding owner..."


buddy = GuideDog()
print(f"  GuideDog can breathe: {buddy.breathe()}")  # From Animal2
print(f"  GuideDog can bark:    {buddy.bark()}")      # From Dog2
print(f"  GuideDog can guide:   {buddy.guide()}")     # Its own
print(f"  GuideDog → Dog → Animal (chain of 3)\n")


# =============================================
# MULTIPLE INHERITANCE: One child, MULTIPLE parents
# Python allows this. Java does NOT.
# =============================================

print("=== Multiple Inheritance ===\n")


class Car:
    def drive(self):
        return "driving on road"


class Plane:
    def fly(self):
        return "flying in sky"


class FlyingCar(Car, Plane):  # Inherits from BOTH
    pass


fc = FlyingCar()
print(f"  FlyingCar can drive: {fc.drive()}")
print(f"  FlyingCar can fly:   {fc.fly()}")
print("  FlyingCar inherits from Car AND Plane")
print("  Java doesn't allow this! Python does.\n")


# =============================================
# MRO — Method Resolution Order
# When multiple parents have the same method, which one runs?
# =============================================

print("=== MRO (Method Resolution Order) ===\n")


class A:
    def greet(self):
        return "Hello from A"


class B(A):
    def greet(self):
        return "Hello from B"


class C(A):
    def greet(self):
        return "Hello from C"


class D(B, C):  # Inherits from both B and C
    pass


d = D()
print(f"  d.greet() = {d.greet()}")  # Which one? B or C?
print(f"\n  MRO of D: {[cls.__name__ for cls in D.__mro__]}")
print("  Python uses C3 Linearization: D → B → C → A → object")
print("  It goes LEFT to RIGHT in the parent list: B before C")

# You can also use .mro() method
print(f"\n  D.mro() = {[cls.__name__ for cls in D.mro()]}")


# =============================================
# The Diamond Problem
# =============================================

print("\n=== The Diamond Problem ===\n")
print("  D inherits from B and C, both inherit from A")
print("      A")
print("     / \\")
print("    B   C")
print("     \\ /")
print("      D")
print()
print("  Java solves this by BANNING multiple inheritance of classes.")
print("  Python solves this with MRO (C3 Linearization).")
print("  MRO ensures each class appears only ONCE in the chain.")


# =============================================
# super vs super()
# =============================================

print("\n=== super vs super() ===\n")

# super  → the built-in class itself (rarely used alone)
# super() → creates a PROXY OBJECT that follows MRO to find the next class

print("  super   = the class (type object)")
print("  super() = a proxy that follows MRO")
print()
print("  You almost ALWAYS want super() with parentheses.")
print("  super().__init__()  → calls parent's __init__ following MRO")
print("  super().describe()  → calls parent's describe() following MRO")


class Parent:
    def greet(self):
        return "Hello from Parent"


class Child(Parent):
    def greet(self):
        parent_greeting = super().greet()  # Follows MRO
        return f"{parent_greeting} + Child"


c = Child()
print(f"\n  Child.greet() = {c.greet()}")
print("  super() followed MRO: Child → Parent")
