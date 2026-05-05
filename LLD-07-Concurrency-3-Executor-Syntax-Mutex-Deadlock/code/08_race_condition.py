import threading

balance = 0

def add(n):
    global balance
    for _ in range(n):
        balance += 1

def subtract(n):
    global balance
    for _ in range(n):
        balance -= 1

t1 = threading.Thread(target=add, args=(1_000_00000,))
t2 = threading.Thread(target=subtract, args=(1_000_00000,))
t1.start(); t2.start()
t1.join(); t2.join()

print(f"Expected: 0")
print(f"Actual:   {balance}")