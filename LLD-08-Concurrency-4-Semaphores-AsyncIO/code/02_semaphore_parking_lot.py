"""
Semaphore as a Parking Lot
==========================
5 parking spots, 10 cars trying to park.
Only 5 cars fit at a time -- others must wait.
"""

import threading
import time

TOTAL_SPOTS = 5
parking_lot = threading.Semaphore(TOTAL_SPOTS)

# Track who is parked right now (for display)
parked_cars = []
parked_lock = threading.Lock()

def try_to_park(car_id):
    print(f"[{time.strftime('%H:%M:%S')}] Car-{car_id} arriving... ", end="")

    if parking_lot._value == 0:
        print("LOT FULL -- waiting!")
    else:
        print("spots available.")

    parking_lot.acquire()

    # Car is now parked
    with parked_lock:
        parked_cars.append(car_id)
        currently = parked_cars.copy()
    print(f"[{time.strftime('%H:%M:%S')}] Car-{car_id} PARKED.    Currently in lot: {currently}")

    time.sleep(2)  # Stay parked for 2 seconds

    # Car leaves
    with parked_lock:
        parked_cars.remove(car_id)
        currently = parked_cars.copy()
    print(f"[{time.strftime('%H:%M:%S')}] Car-{car_id} LEAVING.   Currently in lot: {currently}")

    parking_lot.release()

print(f"Parking lot: {TOTAL_SPOTS} spots, 10 cars arriving\n")

start = time.time()

threads = []
for i in range(10):
    t = threading.Thread(target=try_to_park, args=(i,))
    threads.append(t)
    t.start()
    time.sleep(0.1)  # Cars arrive slightly staggered

for t in threads:
    t.join()

elapsed = time.time() - start
print(f"\nAll cars done in {elapsed:.1f}s")
print(f"10 cars, 5 spots, 2s each = minimum ~4s (2 batches of 5)")
