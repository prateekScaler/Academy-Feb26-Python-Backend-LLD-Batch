"""Step 2: Mutex fixes violations but only allows 1 car at a time."""
import threading, time

booths_in_use = 0
MAX_BOOTHS = 3
lock = threading.Lock()

def pay_toll(car):
    global booths_in_use
    with lock:                          # Only 1 car at a time
        booths_in_use += 1
        print(f"  Car {car}: booth {booths_in_use} of {MAX_BOOTHS}")
        time.sleep(1)
        booths_in_use -= 1

print(f"Highway toll: {MAX_BOOTHS} booths, 6 cars, MUTEX:\n")
start = time.time()
threads = [threading.Thread(target=pay_toll, args=(i,)) for i in range(6)]
[t.start() for t in threads]
[t.join() for t in threads]
print(f"\nTotal: {time.time()-start:.0f}s")
print(f"No violations! But always 'booth 1 of 3' — 2 booths sit empty.")
print(f"Mutex is TOO strict. We have 3 booths but use only 1.")
