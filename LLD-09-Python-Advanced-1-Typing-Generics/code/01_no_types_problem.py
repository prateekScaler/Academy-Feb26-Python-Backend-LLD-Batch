"""Why types matter — the bug that takes 30 minutes to find."""


# --- A real codebase scenario ---
def calculate_total(items):
    total = 0
    for item in items:
        total += item["price"] * item["quantity"]
    return total


def apply_discount(total, discount):
    return total - (total * discount)


def process_order(order):
    items = order["items"]
    total = calculate_total(items)
    # Bug: someone passes discount as "10" (string percentage) instead of 0.1
    final = apply_discount(total, order["discount"])
    return final


# This works fine
order1 = {
    "items": [{"price": 100, "quantity": 2}, {"price": 50, "quantity": 1}],
    "discount": 0.1,
}
print(f"Order 1: ₹{process_order(order1)}")  # ₹225.0 ✓

# This breaks at RUNTIME — not at write time
order2 = {
    "items": [{"price": 100, "quantity": 2}, {"price": 50, "quantity": 1}],
    "discount": "10%",  # Oops! String, not float.
}

try:
    print(f"Order 2: ₹{process_order(order2)}")
except TypeError as e:
    print(f"Order 2: CRASHED — {e}")
    print("  This bug sat in code for weeks. No one caught it until production.")
    print("  With type hints + mypy, this is caught BEFORE you even run the code.")
