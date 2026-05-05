"""Step 2: Producer-Consumer with MUTEX — protects data but can't WAIT."""
import threading, time

buffer = []
MAX_SIZE = 3
lock = threading.Lock()

def producer():
    for i in range(6):
        with lock:
            if len(buffer) >= MAX_SIZE:
                # Mutex can't make us WAIT until space is free.
                # If we hold the lock and loop, consumer can never acquire it = DEADLOCK!
                print(f"  [PRODUCE] item-{i} SKIPPED — buffer full! Can't wait with mutex.")
            else:
                buffer.append(f"item-{i}")
                print(f"  [PRODUCE] item-{i}  buffer size={len(buffer)}/{MAX_SIZE}")
        time.sleep(0.2)

def consumer():
    for _ in range(6):
        time.sleep(0.5)
        with lock:
            if buffer:
                item = buffer.pop(0)
                print(f"  [CONSUME] {item}  buffer size={len(buffer)}/{MAX_SIZE}")
            else:
                # Same problem: can't WAIT for items with a mutex.
                print(f"  [CONSUME] NOTHING — buffer empty! Can't wait with mutex.")

print(f"Producer-Consumer, MUTEX (max buffer={MAX_SIZE}):\n")
t1 = threading.Thread(target=producer)
t2 = threading.Thread(target=consumer)
t1.start(); t2.start()
t1.join(); t2.join()

print(f"\nFinal buffer: {buffer}")
print("\nMutex protects data but CAN'T signal between threads.")
print("Producer can't say 'hey consumer, item ready!'")
print("Consumer can't say 'hey producer, space free!'")
print("We need a SIGNALLING mechanism → Semaphore!")
