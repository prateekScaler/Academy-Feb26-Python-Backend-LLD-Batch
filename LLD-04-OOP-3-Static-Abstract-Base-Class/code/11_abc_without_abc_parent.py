"""@abstractmethod without ABC parent = NO enforcement!"""
from abc import abstractmethod

class NotAnABC:  # No ABC!
    @abstractmethod
    def do_something(self):
        pass

# This SHOULD fail... but it doesn't:
obj = NotAnABC()
print(f"Created! type = {type(obj).__name__}")
print("@abstractmethod did NOTHING without ABC parent.")
print("Always: class Parent(ABC), not just class Parent.")
