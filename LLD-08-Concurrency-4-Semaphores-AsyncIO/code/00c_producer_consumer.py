"""Producer-Consumer pattern with semaphores."""
import threading, time, queue

buffer = queue.Queue(maxsize=5)
items_sem = threading.Semaphore(0)   # 0 items available
space_sem = threading.Semaphore(5)   # 5 empty spaces

def producer():
    for i in range(8):
        space_sem.acquire()
        buffer.put(f"item-{i}")
        print(f"  [PRODUCE] item-{i}  (buffer: {buffer.qsize()})")
        items_sem.release()
        time.sleep(0.3)

def consumer():
    for _ in range(8):
        items_sem.acquire()
        item = buffer.get()
        print(f"  [CONSUME] {item}")
        space_sem.release()
        time.sleep(0.5)

t1 = threading.Thread(target=producer)
t2 = threading.Thread(target=consumer)
t1.start(); t2.start()
t1.join(); t2.join()
print("\nProducer-consumer coordinated via semaphores.")
