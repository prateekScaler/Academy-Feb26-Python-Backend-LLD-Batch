"""
08 - All Three Factory Variants Side-by-Side
============================================

Same product hierarchy (Pet adoption) implemented THREE ways so you can
diff the patterns in the same file:

  - Variant A: Simple Factory     (PetFactory.create(kind))
  - Variant B: Factory Method     (PetCreator + DogCreator + CatCreator)
  - Variant C: Abstract Factory   (PetCareKitFactory producing matching
                                   food + bed + toy families for dogs vs cats)

Designed for PyCharm's UML class-diagram view to render the three shapes
cleanly side-by-side.

To view the UML:
  PyCharm  →  right-click this file  →  Diagrams  →  Show Diagram...
  Enable "Methods", "Fields", "Show Implements / Extends", "Show
  Dependencies". You'll see four distinct hierarchies stacked vertically.

Why this file is useful: in interviews, when asked "which variant would
you use?", you can point at this file and walk through the same domain
in three forms — it makes the trade-offs concrete.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


# ============================================================================
# Shared abstract Pet (the product everyone is creating)
# ============================================================================

class Pet(ABC):
    @abstractmethod
    def speak(self) -> str: ...


class Dog(Pet):
    def speak(self) -> str: return "woof!"


class Cat(Pet):
    def speak(self) -> str: return "meow!"


class Parrot(Pet):
    def speak(self) -> str: return "hello!"


# ============================================================================
# Variant A: Simple Factory
# ============================================================================

class PetFactory:
    """One static method, one if/elif. New pet kinds = modify this class."""

    @staticmethod
    def create(kind: str) -> Pet:
        if kind == "dog":    return Dog()
        if kind == "cat":    return Cat()
        if kind == "parrot": return Parrot()
        raise ValueError(f"unknown pet kind: {kind!r}")


# ============================================================================
# Variant B: Factory Method
# ============================================================================

class PetCreator(ABC):
    """Abstract creator. Each concrete subclass picks one pet kind."""

    @abstractmethod
    def create_pet(self) -> Pet: ...

    def adopt(self, family_name: str) -> str:
        """Template method using the factory method internally."""
        pet = self.create_pet()
        return f"The {family_name} family adopted a {type(pet).__name__}: {pet.speak()}"


class DogCreator(PetCreator):
    def create_pet(self) -> Pet: return Dog()


class CatCreator(PetCreator):
    def create_pet(self) -> Pet: return Cat()


class ParrotCreator(PetCreator):
    def create_pet(self) -> Pet: return Parrot()


# ============================================================================
# Variant C: Abstract Factory
# ============================================================================
#
# Now the products come in FAMILIES. Adopting a dog brings dog-food,
# dog-bed, dog-toy. Adopting a cat brings cat-food, cat-bed, cat-toy.
# Mixing (dog-food + cat-bed) is structurally impossible because there's
# only one factory.

class PetFood(ABC):
    @abstractmethod
    def label(self) -> str: ...


class PetBed(ABC):
    @abstractmethod
    def label(self) -> str: ...


class PetToy(ABC):
    @abstractmethod
    def label(self) -> str: ...


# Dog-family products
class DogFood(PetFood):
    def label(self) -> str: return "Premium Dog Chow 5kg"

class DogBed(PetBed):
    def label(self) -> str: return "Orthopedic Dog Cushion"

class DogToy(PetToy):
    def label(self) -> str: return "Squeaky Tennis Ball"


# Cat-family products
class CatFood(PetFood):
    def label(self) -> str: return "Salmon Pate 2kg"

class CatBed(PetBed):
    def label(self) -> str: return "Cozy Cat Igloo"

class CatToy(PetToy):
    def label(self) -> str: return "Feather Wand"


# The abstract factory
class PetCareKitFactory(ABC):
    @abstractmethod
    def create_food(self) -> PetFood: ...

    @abstractmethod
    def create_bed(self) -> PetBed: ...

    @abstractmethod
    def create_toy(self) -> PetToy: ...


# Concrete factories — one per family
class DogCareKitFactory(PetCareKitFactory):
    def create_food(self) -> PetFood: return DogFood()
    def create_bed(self)  -> PetBed:  return DogBed()
    def create_toy(self)  -> PetToy:  return DogToy()


class CatCareKitFactory(PetCareKitFactory):
    def create_food(self) -> PetFood: return CatFood()
    def create_bed(self)  -> PetBed:  return CatBed()
    def create_toy(self)  -> PetToy:  return CatToy()


# Client uses ONE care-kit factory - mixing is structurally impossible
class AdoptionPackage:
    def __init__(self, pet: Pet, kit: PetCareKitFactory) -> None:
        self.pet  = pet
        self.food = kit.create_food()
        self.bed  = kit.create_bed()
        self.toy  = kit.create_toy()

    def manifest(self) -> List[str]:
        return [
            f"Pet:  {type(self.pet).__name__} says {self.pet.speak()}",
            f"Food: {self.food.label()}",
            f"Bed:  {self.bed.label()}",
            f"Toy:  {self.toy.label()}",
        ]


# ============================================================================
# Demo
# ============================================================================

def demo_simple_factory() -> None:
    print("--- A) Simple Factory ---")
    for kind in ("dog", "cat", "parrot"):
        pet = PetFactory.create(kind)
        print(f"  {type(pet).__name__}: {pet.speak()}")


def demo_factory_method() -> None:
    print("\n--- B) Factory Method ---")
    creators: List[PetCreator] = [DogCreator(), CatCreator(), ParrotCreator()]
    for creator in creators:
        print(f"  {creator.adopt('Iyer')}")


def demo_abstract_factory() -> None:
    print("\n--- C) Abstract Factory (Pet + matching CareKit family) ---")
    dog_pkg = AdoptionPackage(pet=Dog(), kit=DogCareKitFactory())
    cat_pkg = AdoptionPackage(pet=Cat(), kit=CatCareKitFactory())

    print("\n  Dog adoption package:")
    for line in dog_pkg.manifest():
        print(f"    {line}")

    print("\n  Cat adoption package:")
    for line in cat_pkg.manifest():
        print(f"    {line}")


if __name__ == "__main__":
    demo_simple_factory()
    demo_factory_method()
    demo_abstract_factory()
