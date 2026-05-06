"""Collection types — list, dict, tuple, set with element types."""


# --- Python 3.9+ syntax (recommended) ---
def process_names(names: list[str]) -> list[str]:
    """Uppercase all names."""
    return [name.upper() for name in names]


def get_scores() -> dict[str, int]:
    """Return student scores."""
    return {"Alice": 95, "Bob": 87, "Charlie": 92}


def get_coordinates() -> tuple[float, float]:
    """Fixed-length tuple — exactly 2 floats."""
    return (28.6139, 77.2090)  # Delhi coordinates


def get_unique_words(text: str) -> set[str]:
    """Return unique words."""
    return set(text.lower().split())


# --- Nested collections ---
def get_class_scores() -> dict[str, list[int]]:
    """Each student has multiple test scores."""
    return {
        "Alice": [95, 88, 92],
        "Bob": [87, 91, 85],
    }


# --- Variable-length tuple ---
def get_all_scores() -> tuple[int, ...]:
    """Variable-length tuple of ints (like an immutable list)."""
    return (95, 87, 92, 88, 91)


# --- Demo ---
print("Collection type hints:\n")

names = process_names(["alice", "bob", "charlie"])
print(f"  process_names: {names}")

scores = get_scores()
print(f"  get_scores: {scores}")

coords = get_coordinates()
print(f"  get_coordinates: {coords}")

words = get_unique_words("the cat sat on the mat")
print(f"  get_unique_words: {words}")

class_scores = get_class_scores()
print(f"  get_class_scores: {class_scores}")

print("\n--- Python 3.8 and older syntax (you'll see in older code) ---")
print("  from typing import List, Dict, Tuple, Set")
print("  def process_names(names: List[str]) -> List[str]: ...")
print("  Python 3.9+ lets you use list[str] directly — prefer this.")
