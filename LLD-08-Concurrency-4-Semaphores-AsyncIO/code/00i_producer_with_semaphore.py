"""Step 3: Producer-Consumer with SEMAPHORES — proper signalling."""
import threading, time

buffer = []
MAX_SIZE = 3

# Two semaphores for signalling:
space_sem = threading.Semaphore(MAX_SIZE)  # starts at 3 (3 spaces free)
items_sem = threading.Semaphore(0)         # starts at 0 (0 items ready)

lock = threading.Lock()  # just for buffer list safety

def producer():
    for i in range(6):
        space_sem.acquire()         # WAIT if buffer full (count=0 → blocks)
        with lock:
            buffer.append(f"item-{i}")
            print(f"  [PRODUCE] item-{i}  buffer size={len(buffer)}/{MAX_SIZE}")
        items_sem.release()         # SIGNAL consumer: "item ready!"
        time.sleep(0.2)

def consumer():
    for _ in range(6):
        items_sem.acquire()         # WAIT if buffer empty (count=0 → blocks)
        with lock:
            item = buffer.pop(0)
            print(f"  [CONSUME] {item}  buffer size={len(buffer)}/{MAX_SIZE}")
        space_sem.release()         # SIGNAL producer: "space free!"
        time.sleep(0.5)

print(f"Producer-Consumer, SEMAPHORES (max buffer={MAX_SIZE}):\n")
t1 = threading.Thread(target=producer)
t2 = threading.Thread(target=consumer)
t1.start(); t2.start()
t1.join(); t2.join()

print("\nAll 6 items produced and consumed!")
print("No overflow, no empty reads, no busy-waiting.")
print("\nHow it works:")
print("  space_sem(3): producer acquire → waits when full")
print("  items_sem(0): consumer acquire → waits when empty")
print("  Producer release(items_sem) → SIGNALS consumer")
print("  Consumer release(space_sem) → SIGNALS producer")
