"""Step 3: Fixed with a mutex (Lock)."""
import threading

balance = 0
lock = threading.Lock()

def add(n):
    global balance
    for _ in range(n):
        with lock:
            balance += 1

def subtract(n):
    global balance
    for _ in range(n):
        with lock:
            balance -= 1

N = 1_000_000

for run in range(3):
    balance = 0
    t1 = threading.Thread(target=add, args=(N,))
    t2 = threading.Thread(target=subtract, args=(N,))
    t1.start(); t2.start()
    t1.join(); t2.join()
    print(f"Run {run+1}: Expected 0, Got {balance}")

print("\nExactly 0 every time. Lock prevents interleaving.")
