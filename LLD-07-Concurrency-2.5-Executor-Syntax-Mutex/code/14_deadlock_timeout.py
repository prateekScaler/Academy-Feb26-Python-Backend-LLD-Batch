"""Fix deadlock with timeout and retry (backoff)."""
import threading, time, random

lock_A = threading.Lock()
lock_B = threading.Lock()

def book_with_retry(user, first, second):
    attempts = 0
    while True:
        attempts += 1
        first.acquire()
        if second.acquire(timeout=0.1):
            print(f"{user}: got both locks! (attempt {attempts})")
            second.release()
            first.release()
            return
        else:
            first.release()
            wait = random.uniform(0, 0.1)
            print(f"{user}: retry (attempt {attempts}, backing off {wait:.3f}s)")
            time.sleep(wait)

t1 = threading.Thread(target=book_with_retry, args=("User 1", lock_A, lock_B))
t2 = threading.Thread(target=book_with_retry, args=("User 2", lock_B, lock_A))
t1.start(); t2.start()
t1.join(); t2.join()
print("Both succeeded eventually via timeout + retry.")
