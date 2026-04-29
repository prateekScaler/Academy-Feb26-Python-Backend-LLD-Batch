"""Normal threads can't return values. This is the ugly workaround."""
import threading, time

results = []  # Shared list — the ugly workaround

def fetch(url):
    time.sleep(0.5)
    return f"{url}: 200 OK"  # This return value is LOST!

# thread.join() returns None, not the function's return value
t = threading.Thread(target=fetch, args=("a.com",))
t.start()
ret = t.join()
print(f"thread.join() returned: {ret}")  # None!

# Workaround: manually append to shared list
def fetch_ugly(url):
    time.sleep(0.5)
    results.append(f"{url}: 200 OK")

threads = [threading.Thread(target=fetch_ugly, args=(u,))
           for u in ["a.com", "b.com", "c.com"]]
[t.start() for t in threads]
[t.join() for t in threads]
print(f"Results (ugly way): {results}")
print("Order is random. No error handling. Ugly.")
