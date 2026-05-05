"""Step 3: Semaphore(3) — allows 3 cars at once. All booths used."""
import threading, time

booths_in_use = 0
MAX_BOOTHS = 3
sem = threading.Semaphore(MAX_BOOTHS)
lock = threading.Lock()  # just for the counter

def pay_toll(car):
    global booths_in_use
    with sem:                           # Up to 3 at a time
        with lock: booths_in_use += 1
        print(f"  Car {car}: booth {booths_in_use} of {MAX_BOOTHS}")
        time.sleep(1)
        with lock: booths_in_use -= 1

print(f"Highway toll: {MAX_BOOTHS} booths, 6 cars, SEMAPHORE(3):\n")
start = time.time()
threads = [threading.Thread(target=pay_toll, args=(i,)) for i in range(6)]
[t.start() for t in threads]
[t.join() for t in threads]
print(f"\nTotal: {time.time()-start:.0f}s")
print("3 cars at once, 2 batches, all booths used. Perfect!")
