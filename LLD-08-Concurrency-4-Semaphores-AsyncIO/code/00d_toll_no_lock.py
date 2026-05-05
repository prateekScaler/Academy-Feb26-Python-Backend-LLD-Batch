"""Step 1: No lock — 6 cars, 3 booths. Cars exceed booth capacity."""
import threading, time

booths_in_use = 0
MAX_BOOTHS = 3
violations = 0

def pay_toll(car):
    global booths_in_use, violations
    booths_in_use += 1
    if booths_in_use > MAX_BOOTHS:
        print(f"  Car {car}: VIOLATION! {booths_in_use} cars in {MAX_BOOTHS} booths!")
        violations += 1
    else:
        print(f"  Car {car}: booth {booths_in_use} of {MAX_BOOTHS}")
    time.sleep(1)
    booths_in_use -= 1

print(f"Highway toll: {MAX_BOOTHS} booths, 6 cars, NO lock:\n")

threads = [threading.Thread(target=pay_toll, args=(i,)) for i in range(6)]

[t.start() for t in threads]
[t.join() for t in threads]

print(f"\n{violations} violations! More cars in booths than booths exist.")

print("We need to control access. Let's try mutex...")
