"""map() — apply a function to every element. Returns a new iterable.

Think of it as a conveyor belt:
  items go in → function runs on each → transformed items come out
"""


# --- The problem: transform every element in a list ---
prices = [100, 250, 50, 400, 175]

# Approach 1: Manual loop
discounted_loop = []
for price in prices:
    discounted_loop.append(price * 0.9)
print(f"Loop:          {discounted_loop}")

# Approach 2: List comprehension
discounted_comp = [price * 0.9 for price in prices]
print(f"Comprehension: {discounted_comp}")

# Approach 3: map()
discounted_map = list(map(lambda price: price * 0.9, prices))
print(f"map():         {discounted_map}")

# All three produce the same result.
# map() is: map(function, iterable) → applies function to each element


# --- map with a named function ---
def to_celsius(fahrenheit):
    return round((fahrenheit - 32) * 5/9, 1)

temps_f = [32, 68, 100, 212]
temps_c = list(map(to_celsius, temps_f))
print(f"\nFahrenheit: {temps_f}")
print(f"Celsius:    {temps_c}")


# --- map with multiple iterables ---
names = ["alice", "bob", "charlie"]
ages = [25, 30, 35]

# zip-like: takes one from each iterable
combined = list(map(lambda name, age: f"{name}({age})", names, ages))
print(f"\nCombined: {combined}")


# --- map is LAZY — it returns an iterator, not a list ---
result = map(lambda x: x ** 2, [1, 2, 3, 4, 5])
print(f"\nmap() returns: {result}")      # <map object at 0x...>
print(f"list(map()):   {list(result)}")  # [1, 4, 9, 16, 25]
# It only computes values when you ask for them.
# This saves memory for large datasets.


# --- map vs list comprehension ---
print("\n--- map vs comprehension ---")
print("  map():          map(func, items)")
print("  comprehension:  [func(x) for x in items]")
print()
print("  Use map when: you already HAVE a function (to_celsius, str.upper)")
print("  Use comp when: the transformation is a simple expression")
print("  Comprehension is more Pythonic and usually preferred")
