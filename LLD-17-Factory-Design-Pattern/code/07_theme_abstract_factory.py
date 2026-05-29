"""
07 - UI Theme System (Abstract Factory)
=======================================

Designed for PyCharm's UML class-diagram view to render the textbook
Abstract Factory shape:

  - ONE abstract factory (ThemeFactory) producing THREE abstract products
    (Button, TextInput, Card).
  - THREE concrete factories (Light / Dark / HighContrast) each producing
    a matching family of three concrete products.
  - ONE client class (Window) that holds a ThemeFactory by composition.

To view the UML:
  In PyCharm  →  right-click this file in Project pane  →  Diagrams  →
  Show Diagram...  →  enable "Methods", "Fields", "Constructors",
  "Show Implements / Extends edges", "Show Dependencies".

You should see three parallel trees (one per product) plus the factory
tree, with composition arrows from Window → ThemeFactory.

Domain: a desktop app needs to render its UI in three different visual
themes. Each theme has its own Button, TextInput, and Card styles. You
NEVER want to mix themes — that's the family-consistency constraint
Abstract Factory enforces.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


# ============================================================================
# Abstract products (one per kind of widget)
# ============================================================================

class Button(ABC):
    @abstractmethod
    def render(self) -> str: ...


class TextInput(ABC):
    @abstractmethod
    def render(self) -> str: ...


class Card(ABC):
    @abstractmethod
    def render(self) -> str: ...


# ============================================================================
# Concrete products - Light theme family
# ============================================================================

class LightButton(Button):
    def render(self) -> str:
        return "[ Button: white bg / blue text ]"


class LightTextInput(TextInput):
    def render(self) -> str:
        return "[ TextInput: white bg / gray border ]"


class LightCard(Card):
    def render(self) -> str:
        return "[ Card: subtle shadow on white ]"


# ============================================================================
# Concrete products - Dark theme family
# ============================================================================

class DarkButton(Button):
    def render(self) -> str:
        return "[ Button: navy bg / white text ]"


class DarkTextInput(TextInput):
    def render(self) -> str:
        return "[ TextInput: dark gray bg / white border ]"


class DarkCard(Card):
    def render(self) -> str:
        return "[ Card: deep shadow on charcoal ]"


# ============================================================================
# Concrete products - HighContrast theme family
# ============================================================================

class HighContrastButton(Button):
    def render(self) -> str:
        return "[ Button: yellow bg / black text / thick border ]"


class HighContrastTextInput(TextInput):
    def render(self) -> str:
        return "[ TextInput: black bg / yellow text / 3px border ]"


class HighContrastCard(Card):
    def render(self) -> str:
        return "[ Card: solid black border, no shadow ]"


# ============================================================================
# Abstract Factory
# ============================================================================

class ThemeFactory(ABC):
    """Each concrete subclass produces ONE complete theme family."""

    @abstractmethod
    def create_button(self) -> Button: ...

    @abstractmethod
    def create_text_input(self) -> TextInput: ...

    @abstractmethod
    def create_card(self) -> Card: ...


# ============================================================================
# Concrete factories - one per family
# ============================================================================

class LightThemeFactory(ThemeFactory):
    def create_button(self)     -> Button:    return LightButton()
    def create_text_input(self) -> TextInput: return LightTextInput()
    def create_card(self)       -> Card:      return LightCard()


class DarkThemeFactory(ThemeFactory):
    def create_button(self)     -> Button:    return DarkButton()
    def create_text_input(self) -> TextInput: return DarkTextInput()
    def create_card(self)       -> Card:      return DarkCard()


class HighContrastThemeFactory(ThemeFactory):
    def create_button(self)     -> Button:    return HighContrastButton()
    def create_text_input(self) -> TextInput: return HighContrastTextInput()
    def create_card(self)       -> Card:      return HighContrastCard()


# ============================================================================
# Client: a Window HAS-A ThemeFactory and uses it to build its widgets
# ============================================================================

@dataclass
class Window:
    """A Window holds a single ThemeFactory. All widgets it renders come
    from that one factory — making family-mixing structurally impossible."""

    title: str
    theme: ThemeFactory

    def render(self) -> str:
        button = self.theme.create_button()
        text   = self.theme.create_text_input()
        card   = self.theme.create_card()
        return "\n".join([
            f"=== {self.title} (theme: {type(self.theme).__name__}) ===",
            "  " + button.render(),
            "  " + text.render(),
            "  " + card.render(),
        ])


# ============================================================================
# Demo
# ============================================================================

def demo() -> None:
    themes: List[ThemeFactory] = [
        LightThemeFactory(),
        DarkThemeFactory(),
        HighContrastThemeFactory(),
    ]

    for theme in themes:
        window = Window(title="Settings", theme=theme)
        print(window.render())
        print()


if __name__ == "__main__":
    demo()
