"""
06 - Vehicle Manufacturing (Factory Method)
===========================================

A second worked example with a rich class hierarchy designed to render
well in PyCharm's UML class-diagram view:

  PyCharm:  right-click the file in the Project pane →
            "Diagrams" → "Show Diagram..." → check
            "Classes" + "Methods" + "Fields" + "Constructors"

You'll see two clean inheritance trees (Vehicle and VehicleFactory),
with composition arrows from each Factory to the Vehicle it produces.

Domain: a fleet management company manufactures different vehicles.
Each VehicleFactory subclass knows how to build ONE kind of vehicle.
Adding a new vehicle (e.g. Bicycle) = new Vehicle subclass + new
VehicleFactory subclass. Existing code untouched.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List


# ============================================================================
# Product hierarchy
# ============================================================================

class Vehicle(ABC):
    """Anything with wheels you can drive."""

    def __init__(self, model: str, max_speed_kmph: int) -> None:
        self.model = model
        self.max_speed_kmph = max_speed_kmph

    @abstractmethod
    def fuel_type(self) -> str: ...

    @abstractmethod
    def wheels(self) -> int: ...

    def describe(self) -> str:
        return (
            f"{type(self).__name__}(model={self.model!r}, "
            f"top={self.max_speed_kmph}km/h, fuel={self.fuel_type()}, "
            f"wheels={self.wheels()})"
        )


class Car(Vehicle):
    def __init__(self, model: str, seats: int) -> None:
        super().__init__(model, max_speed_kmph=180)
        self.seats = seats

    def fuel_type(self) -> str: return "petrol"
    def wheels(self) -> int:    return 4


class ElectricCar(Vehicle):
    def __init__(self, model: str, battery_kwh: int) -> None:
        super().__init__(model, max_speed_kmph=200)
        self.battery_kwh = battery_kwh

    def fuel_type(self) -> str: return "electric"
    def wheels(self) -> int:    return 4


class Truck(Vehicle):
    def __init__(self, model: str, payload_kg: int) -> None:
        super().__init__(model, max_speed_kmph=110)
        self.payload_kg = payload_kg

    def fuel_type(self) -> str: return "diesel"
    def wheels(self) -> int:    return 6


class Motorcycle(Vehicle):
    def __init__(self, model: str, displacement_cc: int) -> None:
        super().__init__(model, max_speed_kmph=220)
        self.displacement_cc = displacement_cc

    def fuel_type(self) -> str: return "petrol"
    def wheels(self) -> int:    return 2


# ============================================================================
# Creator hierarchy (Factory Method)
# ============================================================================

class VehicleFactory(ABC):
    """Abstract creator. Subclasses pick which Vehicle to build."""

    @abstractmethod
    def create_vehicle(self) -> Vehicle: ...

    def manufacture_batch(self, count: int) -> List[Vehicle]:
        """Template method - uses the factory method internally."""
        return [self.create_vehicle() for _ in range(count)]


class CarFactory(VehicleFactory):
    def create_vehicle(self) -> Vehicle:
        return Car(model="SedanX", seats=5)


class ElectricCarFactory(VehicleFactory):
    def create_vehicle(self) -> Vehicle:
        return ElectricCar(model="Volt-One", battery_kwh=75)


class TruckFactory(VehicleFactory):
    def create_vehicle(self) -> Vehicle:
        return Truck(model="HaulMaster-9", payload_kg=5_000)


class MotorcycleFactory(VehicleFactory):
    def create_vehicle(self) -> Vehicle:
        return Motorcycle(model="Roadster-R6", displacement_cc=600)


# ============================================================================
# Composition: a Fleet HAS-A list of factories
# ============================================================================

@dataclass
class Fleet:
    """A fleet uses zero or more VehicleFactory instances to produce vehicles."""

    name: str
    factories: List[VehicleFactory] = field(default_factory=list)

    def add_factory(self, factory: VehicleFactory) -> None:
        self.factories.append(factory)

    def manufacture_all(self) -> List[Vehicle]:
        all_vehicles: List[Vehicle] = []
        for factory in self.factories:
            all_vehicles.extend(factory.manufacture_batch(2))
        return all_vehicles


# ============================================================================
# Demo
# ============================================================================

def demo() -> None:
    fleet = Fleet(name="CityFleet-Mumbai")
    fleet.add_factory(CarFactory())
    fleet.add_factory(ElectricCarFactory())
    fleet.add_factory(TruckFactory())
    fleet.add_factory(MotorcycleFactory())

    print(f"--- {fleet.name} manufacturing run ---")
    for vehicle in fleet.manufacture_all():
        print(f"  {vehicle.describe()}")


if __name__ == "__main__":
    demo()
