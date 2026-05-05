"""Step 1: Add & subtract WITHOUT threads — always 0."""

balance = 0

def add(n):
    global balance
    for _ in range(n):
        balance += 1

def subtract(n):
    global balance
    for _ in range(n):
        balance -= 1

N = 1_000_000
add(N)
subtract(N)
print(f"Balance: {balance}")  # What do you expect?
