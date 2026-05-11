"""The classic closure gotcha — late binding in loops."""


# --- The bug ---
functions = []
for i in range(5):
    functions.append(lambda: i)   # each lambda captures 'i'

# You'd expect: [0, 1, 2, 3, 4]
results = [f() for f in functions]
print(f"Bug: {results}")    # [4, 4, 4, 4, 4] !!!

# WHY? All 5 lambdas share the SAME variable 'i'.
# When you call them AFTER the loop, i = 4 (the last value).
# The lambda doesn't capture the VALUE of i, it captures the VARIABLE i.


# --- Fix 1: Default argument (captures value at creation time) ---
functions_fixed = []
for i in range(5):
    functions_fixed.append(lambda i=i: i)   # i=i captures current value

results_fixed = [f() for f in functions_fixed]
print(f"Fix: {results_fixed}")   # [0, 1, 2, 3, 4] ✓


# --- Fix 2: Use a factory function ---
def make_func(val):
    return lambda: val   # val is captured by value (new scope each call)

functions_fixed2 = [make_func(i) for i in range(5)]
results_fixed2 = [f() for f in functions_fixed2]
print(f"Fix2: {results_fixed2}")  # [0, 1, 2, 3, 4] ✓


# --- This is a REAL interview question ---
print("\n--- Summary ---")
print("  Lambda in a loop: captures the VARIABLE, not the VALUE")
print("  All lambdas see the final value of the loop variable")
print("  Fix: lambda i=i: i  (default arg captures value at creation)")
print("  Or:  use a factory function that creates a new scope")
