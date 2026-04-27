"""GIL + I/O: threads DO help here (GIL released during sleep/network)."""
import time, threading

def call_api(name):
    time.sleep(1)

print("4 API calls (1s each)...\n")

start = time.time()
for _ in range(4): call_api("api")
print(f"Sequential: {time.time()-start:.1f}s")

start = time.time()

ts = [threading.Thread(target=call_api, args=("api",)) for _ in range(4)]

[t.start() for t in ts];
[t.join() for t in ts]
print(f"Threaded:   {time.time()-start:.1f}s")

print("\nI/O releases the GIL → threads overlap their waiting time.")
