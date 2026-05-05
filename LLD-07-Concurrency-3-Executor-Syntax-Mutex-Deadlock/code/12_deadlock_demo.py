"""Deadlock: two threads each wait for the other's lock. Hangs forever.
WARNING: This program WILL hang. Press Ctrl+C to stop."""
import threading, time

lock_A = threading.Lock()
lock_B = threading.Lock()

def user1():
    with lock_A:
        print("User 1: got seat A")
        time.sleep(0.1)
        print("User 1: waiting for seat B...")
        with lock_B:
            print("User 1: got seat B")

def user2():
    with lock_B:
        print("User 2: got seat B")
        time.sleep(0.1)
        print("User 2: waiting for seat A...")
        with lock_A:
            print("User 2: got seat A")

t1 = threading.Thread(target=user1)
t2 = threading.Thread(target=user2)
t1.start(); t2.start()

# Wait 3 seconds then report
t1.join(timeout=3)
t2.join(timeout=3)

if t1.is_alive() or t2.is_alive():
    print("\nDEADLOCK! Both threads are stuck waiting for each other.")
    print("User 1 holds A, wants B. User 2 holds B, wants A.")
    print("Press Ctrl+C to exit.")
