"""Why you need locks: a tale in three acts."""
import threading, sys

sys.setswitchinterval(1e-6)
ITERATIONS = 1_000_000

# ACT 1: Plain int — looks safe (CPython hides the bug)
def act1():
    balance = 0
    def add(): nonlocal balance; [balance := balance + 1 for _ in range(ITERATIONS)] if False else None; 
    # Simpler:
    b = [0]
    def add_simple():
        for _ in range(ITERATIONS): b[0] += 1
    def sub_simple():
        for _ in range(ITERATIONS): b[0] -= 1
    t1 = threading.Thread(target=add_simple)
    t2 = threading.Thread(target=sub_simple)
    t1.start(); t2.start(); t1.join(); t2.join()
    return b[0]

# ACT 2: @property — race exposed
class Account:
    def __init__(self): self._balance = 0
    @property
    def balance(self): return self._balance
    @balance.setter
    def balance(self, v): self._balance = v

def act2():
    acc = Account()
    def add():
        for _ in range(ITERATIONS): acc.balance += 1
    def sub():
        for _ in range(ITERATIONS): acc.balance -= 1
    t1 = threading.Thread(target=add)
    t2 = threading.Thread(target=sub)
    t1.start(); t2.start(); t1.join(); t2.join()
    return acc.balance

# ACT 3: Lock — actually safe
def act3():
    acc = Account()
    lock = threading.Lock()
    def add():
        for _ in range(ITERATIONS):
            with lock: acc.balance += 1
    def sub():
        for _ in range(ITERATIONS):
            with lock: acc.balance -= 1
    t1 = threading.Thread(target=add)
    t2 = threading.Thread(target=sub)
    t1.start(); t2.start(); t1.join(); t2.join()
    return acc.balance

if __name__ == "__main__":
    print(f"Each thread: {ITERATIONS:,} ops. Expected: 0\n")
    r1 = act1()
    print(f"Act 1 — plain int:     {r1:>+10,}  {'looks fine (lie!)' if r1 == 0 else 'race!'}")
    r2 = act2()
    print(f"Act 2 — @property:     {r2:>+10,}  {'ok' if r2 == 0 else 'race exposed!'}")
    r3 = act3()
    print(f"Act 3 — @property+Lock:{r3:>+10,}  {'actually safe' if r3 == 0 else 'bug'}")
    print("\nAct 1 was NEVER safe. CPython was hiding the bug. Always use a Lock.")
