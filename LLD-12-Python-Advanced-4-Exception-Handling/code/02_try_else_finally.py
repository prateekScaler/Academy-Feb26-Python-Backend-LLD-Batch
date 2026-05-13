"""try / except / else / finally — when does each block run?"""


def read_config(filename):
    """Demonstrates all 4 blocks."""
    try:
        f = open(filename)
        print(f"  try: opened {filename}")
    except FileNotFoundError:
        print(f"  except: {filename} not found!")
        return None
    else:
        # Runs ONLY if try succeeded (no exception)
        data = f.read()
        f.close()
        print(f"  else: read {len(data)} chars")
        return data
    finally:
        # ALWAYS runs — exception or not, return or not
        print(f"  finally: cleanup done")


print("=== File exists ===")
# Create a temp file for demo
with open("/tmp/test_config.txt", "w") as f:
    f.write("debug=true\nport=8000")
read_config("/tmp/test_config.txt")

print("\n=== File doesn't exist ===")
read_config("/tmp/nonexistent.txt")


# --- When to use else ---
# else runs ONLY if try succeeded.
# Why not just put code after try?
# Because: code after try runs even if except handled an error.
print("\n=== Why else matters ===")

# WITHOUT else (bug):
print("Without else:")
try:
    value = int("42")
except ValueError:
    print("  except: bad input")
print(f"  after try: value = {value}")  # this runs even after except!

# WITH else (correct):
print("\nWith else:")
try:
    value = int("hello")
except ValueError:
    print("  except: bad input")
else:
    print(f"  else: value = {value}")   # only runs if try succeeded


# --- finally with return (tricky!) ---
def tricky():
    try:
        return "from try"
    finally:
        print("  finally runs EVEN with return in try!")

print(f"\ntricky() = '{tricky()}'")
# finally runs before the return value is passed back


# --- Summary ---
print("\n" + "=" * 50)
print("Block execution:")
print("  try:     always runs first")
print("  except:  runs if try raised an exception")
print("  else:    runs ONLY if try had NO exception")
print("  finally: ALWAYS runs (cleanup)")
print()
print("  try + except           → basic error handling")
print("  try + except + else    → separate success path")
print("  try + except + finally → cleanup guarantee")
print("  try + finally          → cleanup without catching")
