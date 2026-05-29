"""
03 - Abstract Factory
=====================

Products come in FAMILIES (Windows widgets / Mac widgets / Linux widgets).
A single factory parameter holds the whole family, so the caller CANNOT
accidentally mix a Mac checkbox with a Windows button.

Compare with file 01 (Simple Factory) and file 02 (Factory Method) -
both would let you mix families by passing different os_type strings or
different creator instances.
"""

from abc import ABC, abstractmethod


# ---------------------------------------------------------------------------
# Abstract products: one per kind of widget
# ---------------------------------------------------------------------------

class Button(ABC):
    @abstractmethod
    def render(self) -> str: ...


class Checkbox(ABC):
    @abstractmethod
    def render(self) -> str: ...


class Menu(ABC):
    @abstractmethod
    def render(self) -> str: ...


# ---------------------------------------------------------------------------
# Concrete products grouped by FAMILY
# ---------------------------------------------------------------------------

class WindowsButton(Button):
    def render(self): return "Windows-style button"

class WindowsCheckbox(Checkbox):
    def render(self): return "Windows-style checkbox"

class WindowsMenu(Menu):
    def render(self): return "Windows-style menu"


class MacButton(Button):
    def render(self): return "Mac-style button"

class MacCheckbox(Checkbox):
    def render(self): return "Mac-style checkbox"

class MacMenu(Menu):
    def render(self): return "Mac-style menu"


class LinuxButton(Button):
    def render(self): return "Linux-style button"

class LinuxCheckbox(Checkbox):
    def render(self): return "Linux-style checkbox"

class LinuxMenu(Menu):
    def render(self): return "Linux-style menu"


# ---------------------------------------------------------------------------
# Abstract Factory: produces a FAMILY of related products
# ---------------------------------------------------------------------------

class WidgetFactory(ABC):
    """Each concrete subclass produces ONE complete family."""

    @abstractmethod
    def create_button(self) -> Button: ...

    @abstractmethod
    def create_checkbox(self) -> Checkbox: ...

    @abstractmethod
    def create_menu(self) -> Menu: ...


# ---------------------------------------------------------------------------
# Concrete factories - one per family
# ---------------------------------------------------------------------------

class WindowsWidgetFactory(WidgetFactory):
    def create_button(self):   return WindowsButton()
    def create_checkbox(self): return WindowsCheckbox()
    def create_menu(self):     return WindowsMenu()


class MacWidgetFactory(WidgetFactory):
    def create_button(self):   return MacButton()
    def create_checkbox(self): return MacCheckbox()
    def create_menu(self):     return MacMenu()


class LinuxWidgetFactory(WidgetFactory):
    def create_button(self):   return LinuxButton()
    def create_checkbox(self): return LinuxCheckbox()
    def create_menu(self):     return LinuxMenu()


# ---------------------------------------------------------------------------
# Client - takes ONE factory, family-consistent by construction
# ---------------------------------------------------------------------------

class Application:
    def __init__(self, factory: WidgetFactory):
        # All widgets come from the same factory - mixing is structurally
        # impossible because there's only one `factory` to pass in.
        self.button   = factory.create_button()
        self.checkbox = factory.create_checkbox()
        self.menu     = factory.create_menu()

    def render(self):
        return "\n".join([
            self.button.render(),
            self.checkbox.render(),
            self.menu.render(),
        ])


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo():
    factories = {
        "Windows": WindowsWidgetFactory(),
        "Mac":     MacWidgetFactory(),
        "Linux":   LinuxWidgetFactory(),
    }

    for os_name, factory in factories.items():
        print(f"--- Rendering on {os_name} ---")
        app = Application(factory)
        print(app.render())
        print()


if __name__ == "__main__":
    demo()
