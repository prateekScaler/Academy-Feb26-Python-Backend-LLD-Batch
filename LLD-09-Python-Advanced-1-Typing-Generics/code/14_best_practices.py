"""Best practices — when to type, when not to, and common patterns."""
from typing import Any


# --- Rule 1: Type function signatures (always) ---
# Good: clear contract
def calculate_tax(income: float, rate: float = 0.3) -> float:
    return income * rate


# Bad: what are these? who knows
def calculate_tax_bad(income, rate=0.3):
    return income * rate


# --- Rule 2: Type variables when the type isn't obvious ---
# Not needed: obvious from assignment
name = "Alice"  # mypy infers str
count = 0       # mypy infers int
items = []      # ← THIS one needs a hint! mypy can't infer element type

# Needed:
items_typed: list[str] = []
scores: dict[str, int] = {}


# --- Rule 3: Don't over-type internal/private code ---
# Over-typed (unnecessary for a 3-line helper):
def _parse_line(line: str) -> tuple[str, int]:
    name, score = line.split(",")
    return name.strip(), int(score.strip())


# --- Rule 4: Use 'Any' as an escape hatch, not a default ---
def bad_function(data: Any) -> Any:  # Defeats the purpose!
    return data


def better_function(data: dict[str, Any]) -> str:
    """At least we know it's a dict with str keys."""
    return str(data.get("name", "unknown"))


# --- Rule 5: Gradually type existing code ---
# Start with:
#   1. Public API functions (the ones others call)
#   2. Data classes and models
#   3. Function return types (most value for least effort)
#   4. Complex functions where bugs are likely
# Skip:
#   - Tests (usually not worth typing)
#   - One-off scripts
#   - Internal helpers where types are obvious


# --- Rule 6: Use reveal_type() for debugging ---
x = [1, 2, 3]
# Uncomment and run mypy to see what type mypy infers:
# reveal_type(x)  # note: Revealed type is "builtins.list[builtins.int]"


# --- Summary ---
print("Typing Best Practices:\n")
print("  DO type:")
print("    ✓ All public function signatures")
print("    ✓ Class attributes and __init__ parameters")
print("    ✓ Variables where type isn't obvious (empty containers)")
print("    ✓ Return types (biggest bang for buck)")
print()
print("  DON'T type:")
print("    ✗ Obvious assignments (name = 'Alice')")
print("    ✗ Test files (diminishing returns)")
print("    ✗ Throwaway scripts")
print("    ✗ Every single local variable")
print()
print("  Tools:")
print("    • mypy — the standard type checker (pip install mypy)")
print("    • pyright — Microsoft's checker (used in VS Code/Pylance)")
print("    • ruff — fast linter that checks some type issues")
print("    • pydantic — runtime type validation (FastAPI uses this)")
print()
print("  Pro tip: Add to CI/CD pipeline:")
print("    mypy src/ --strict")
print("    This catches bugs before they reach production.")
