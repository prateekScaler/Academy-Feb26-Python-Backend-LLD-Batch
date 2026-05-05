"""Step 2: Add & subtract WITH threads — race condition.
We add a tiny sleep to force context switching and expose the bug.
In real code, the "sleep" is any slow operation (DB call, API call, etc.)."""
import threading
import time

balance = 0

def add(n):
    global balance
    for _ in range(n):
        temp = balance        # READ
        time.sleep(0)         # Force context switch (simulates real work)
        balance = temp + 1    # WRITE (may overwrite subtract's work!)

def subtract(n):
    global balance
    for _ in range(n):
        temp = balance
        time.sleep(0)
        balance = temp - 1

N = 1000  # Small N because sleep(0) makes it slow

for run in range(3):
    balance = 0
    t1 = threading.Thread(target=add, args=(N,))
    t2 = threading.Thread(target=subtract, args=(N,))
    t1.start(); t2.start()
    t1.join(); t2.join()
    print(f"Run {run+1}: Expected 0, Got {balance}")

print("\nWith time.sleep(0), the OS forces a context switch between")
print("READ and WRITE. This is what happens in real code when there's")
print("a DB call or API call between reading and writing shared data.")
