"""
Pre-LSP Concept Quiz
====================
Four warm-up snippets that build up to LSP. Run each section to see the
runtime behavior, then read the explanation below it.
"""

from abc import ABC, abstractmethod


# ---------------------------------------------------------------
# Q1: Runtime method resolution (dynamic / runtime polymorphism)
# ---------------------------------------------------------------
class Animal:
    def sound(self):
        return "Some sound"


class Dog(Animal):
    def sound(self):
        return "Bark"


def demo_q1():
    pet: Animal = Dog()
    print("Q1:", pet.sound())  # -> "Bark"
    # The reference type is Animal, but Python resolves .sound()
    # on the actual object (Dog) at runtime.


# ---------------------------------------------------------------
# Q2: Method Resolution Order (MRO) and inheritance
# ---------------------------------------------------------------
class Parent:
    def display(self):
        return "Parent"


class Child(Parent):
    pass


def demo_q2():
    obj = Child()
    print("Q2:", obj.display())  # -> "Parent"
    # Child doesn't override display(); MRO walks Child -> Parent -> object
    # and finds Parent.display().


# ---------------------------------------------------------------
# Q3: Python is dynamically typed - type hints are not enforced
# ---------------------------------------------------------------
class Vehicle:
    def start(self):
        return "Vehicle starting"


class Car(Vehicle):
    def honk(self):
        return "Beep beep!"


def demo_q3():
    v: Vehicle = Car()
    # The hint says Vehicle, but at runtime v is a Car which HAS honk().
    print("Q3:", v.honk())  # -> "Beep beep!"
    # mypy would flag this; the Python interpreter does not.


# ---------------------------------------------------------------
# Q4: The LSP punchline - substitution that breaks the caller
# ---------------------------------------------------------------
class Calculator:
    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b


class StrictCalculator(Calculator):
    def divide(self, a, b):
        if b == 0:
            # NEW exception type the parent never promised
            raise ZeroDivisionError("Division by zero")
        return a / b


def compute(calc: Calculator):
    try:
        result = calc.divide(10, 0)
    except ValueError:
        print("Handled gracefully")


def demo_q4():
    # Parent's contract: throws ValueError on b == 0
    # Child changed it to ZeroDivisionError
    # The caller only catches ValueError -> uncaught crash
    try:
        compute(StrictCalculator())
    except ZeroDivisionError as e:
        print("Q4: CRASH ->", e)
    # This is exactly what LSP forbids: a subclass that breaks the
    # parent's contract (here: the exception contract).


if __name__ == "__main__":
    demo_q1()
    demo_q2()
    demo_q3()
    demo_q4()
