"""The fix: Semaphore(3) limits to 3 concurrent DB connections."""
import threading, time

sem = threading.Semaphore(3)

def query_database(thread_id):
    with sem:
        print(f"  Thread {thread_id}: querying DB")
        time.sleep(1)
    print(f"  Thread {thread_id}: done, released spot")

threads = [threading.Thread(target=query_database, args=(i,)) for i in range(10)]
[t.start() for t in threads]
[t.join() for t in threads]
print("\nNever more than 3 at a time. No DB errors.")
