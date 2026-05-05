"""
Semaphore as a Rate Limiter
============================
Fetch 20 URLs, but max 5 at a time.
Compare: unlimited vs limited.
"""

import threading
import time

def fetch_url(url_id, semaphore=None):
    """Simulate fetching a URL (takes 1 second)."""
    if semaphore:
        with semaphore:
            print(f"  [{time.strftime('%H:%M:%S')}] Fetching URL-{url_id}...")
            time.sleep(1)
            print(f"  [{time.strftime('%H:%M:%S')}] Done URL-{url_id}")
    else:
        print(f"  [{time.strftime('%H:%M:%S')}] Fetching URL-{url_id}...")
        time.sleep(1)
        print(f"  [{time.strftime('%H:%M:%S')}] Done URL-{url_id}")

NUM_URLS = 20

# --- No limit: all 20 at once ---
print("=" * 50)
print("NO LIMIT - all 20 URLs at once")
print("=" * 50)

start = time.time()
threads = []
for i in range(NUM_URLS):
    t = threading.Thread(target=fetch_url, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

no_limit_time = time.time() - start
print(f"\nNo limit: {no_limit_time:.1f}s (all 20 ran at once)")

# --- With Semaphore(5): max 5 at a time ---
print("\n" + "=" * 50)
print("SEMAPHORE(5) - max 5 URLs at a time")
print("=" * 50)

sem = threading.Semaphore(5)

start = time.time()
threads = []
for i in range(NUM_URLS):
    t = threading.Thread(target=fetch_url, args=(i, sem))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

limited_time = time.time() - start
print(f"\nRate limited: {limited_time:.1f}s (5 at a time, 20/5 = 4 batches x 1s)")

print(f"\n--- Summary ---")
print(f"No limit:     {no_limit_time:.1f}s  (all at once, could overwhelm server!)")
print(f"Semaphore(5): {limited_time:.1f}s  (controlled, 5 at a time)")
print(f"The rate limiter is only {limited_time / no_limit_time:.1f}x slower but much safer.")
