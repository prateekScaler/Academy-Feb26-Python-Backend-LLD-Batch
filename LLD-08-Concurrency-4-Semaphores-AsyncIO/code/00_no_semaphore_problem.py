"""The problem: 10 threads hit a DB that allows max 3 connections. Without semaphore."""
import threading, time

active = 0
lock = threading.Lock()
errors = 0

def query_database(thread_id):
    global active, errors
    with lock: active += 1
    current = active
    if current > 3:
        print(f"  Thread {thread_id}: DB ERROR! {current} connections (max 3)")
        errors += 1
    else:
        print(f"  Thread {thread_id}: querying... ({current} active)")
    time.sleep(1)
    with lock: active -= 1

threads = [threading.Thread(target=query_database, args=(i,)) for i in range(10)]
[t.start() for t in threads]
[t.join() for t in threads]
print(f"\n{errors} connection errors! We need to limit to 3 at a time.")
print("Fix: use a Semaphore(3)")
