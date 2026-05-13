"""Context managers — the 'with' statement. Automatic cleanup."""


# --- Problem: forgetting to close resources ---
# BAD: what if process_data raises an error? File never closes!
# f = open("data.txt")
# data = process_data(f.read())
# f.close()  # never reached if process_data crashes!

# OK but verbose:
# f = open("data.txt")
# try:
#     data = process_data(f.read())
# finally:
#     f.close()

# BEST: 'with' statement
# with open("data.txt") as f:
#     data = process_data(f.read())
# # f.close() is called automatically, even if exception occurs!


# --- How 'with' works ---
# The 'with' statement calls:
#   __enter__() when entering the block
#   __exit__()  when leaving (even on exception)

class ManagedFile:
    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        print(f"  Opening {self.filename}")
        self.file = open(self.filename, "w")
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"  Closing {self.filename} (exc_type={exc_type})")
        self.file.close()
        return False  # False = don't suppress exceptions

# Usage:
print("Context manager demo:")
with ManagedFile("/tmp/cm_demo.txt") as f:
    f.write("hello context manager")
    print(f"  Writing...")
print("  After 'with' block — file is closed!\n")


# --- The easy way: contextlib ---
from contextlib import contextmanager

@contextmanager
def timer(label):
    import time
    start = time.time()
    print(f"  [{label}] starting...")
    yield   # ← the 'with' block runs here
    elapsed = time.time() - start
    print(f"  [{label}] done in {elapsed:.4f}s")

print("@contextmanager demo:")
with timer("computation"):
    total = sum(range(1_000_000))
    print(f"  sum = {total}")


# --- Real-world context managers ---
print("\n--- Common context managers ---")
print("  with open(...)         → auto-close file")
print("  with db.connection()   → auto-close DB connection")
print("  with lock:             → auto-release threading.Lock")
print("  with timer('label'):   → auto-measure time")
print("  with suppress(Error):  → ignore specific exceptions")
print("  with tempfile.Temp():  → auto-delete temp file")

# --- suppress: ignore specific exceptions ---
from contextlib import suppress

print("\nsuppress demo:")
with suppress(FileNotFoundError):
    open("/tmp/definitely_doesnt_exist_12345.txt")
    print("this line never runs")
print("  No crash! FileNotFoundError was suppressed.")
