"""Fix deadlock by always locking in sorted order."""
import threading, time

locks = {"A": threading.Lock(), "B": threading.Lock(), "C": threading.Lock()}

def book_seats(user, seat1, seat2):
    # ALWAYS lock in sorted order — prevents deadlock
    first, second = sorted([seat1, seat2])
    with locks[first]:
        print(f"{user}: locked seat {first}")
        time.sleep(0.1)
        with locks[second]:
            print(f"{user}: locked seat {second}")
    print(f"{user}: booking complete!\n")

# User 1 wants A,B. User 2 wants B,A. Both sort → lock A first, then B.
t1 = threading.Thread(target=book_seats, args=("User 1", "A", "B"))
t2 = threading.Thread(target=book_seats, args=("User 2", "B", "A"))
t1.start(); t2.start()
t1.join(); t2.join()
print("No deadlock! Sorting ensures consistent lock order.")
