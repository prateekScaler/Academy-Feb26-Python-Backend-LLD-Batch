"""Lambda — a function without a name. That's it. Nothing magical.

A lambda is just a shortcut for writing a tiny function inline.
"""


# --- The long way: define a function, give it a name ---
def double(x):
    return x * 2

print(f"double(5) = {double(5)}")


# --- The short way: lambda ---
double_v2 = lambda x: x * 2

print(f"lambda double(5) = {double_v2(5)}")


# --- They're the SAME thing ---
# def double(x):     ←  keyword 'def', name 'double', parameter 'x'
#     return x * 2   ←  body with 'return'
#
# lambda x: x * 2    ←  keyword 'lambda', parameter 'x', expression after ':'
#                        The expression IS the return value (no 'return' needed)


# --- Lambda with multiple parameters ---
add = lambda a, b: a + b
print(f"\nadd(3, 4) = {add(3, 4)}")

full_name = lambda first, last: f"{first} {last}"
print(f"full_name('John', 'Doe') = '{full_name('John', 'Doe')}'")


# --- Lambda with no parameters ---
get_pi = lambda: 3.14159
print(f"\nget_pi() = {get_pi()}")


# --- Lambda with a condition (ternary) ---
is_even = lambda x: "even" if x % 2 == 0 else "odd"
print(f"\nis_even(4) = '{is_even(4)}'")
print(f"is_even(7) = '{is_even(7)}'")


# --- IMPORTANT: Lambda is for ONE expression only ---
# You CANNOT do this:
# bad = lambda x:
#     if x > 0:
#         return "positive"
#     else:
#         return "negative"
#
# Lambda = one line, one expression. For anything more, use def.


# --- When to use lambda vs def ---
print("\n" + "=" * 50)
print("Lambda rules:")
print("  1. ONE expression only (no if/for/multiple lines)")
print("  2. No name needed (that's the whole point)")
print("  3. Used inline: sorted(key=lambda x: x.age)")
print("  4. If it needs a name, use def instead")
print("  5. If you need to explain it, use def instead")
