"""Step 1: Producer-Consumer with NO protection — buffer overflows."""
import threading, time

buffer = []
MAX_SIZE = 3

def producer():
    for i in range(6):
        buffer.append(f"item-{i}")
        print(f"  [PRODUCE] item-{i}  buffer={buffer}  (size {len(buffer)}/{MAX_SIZE})")
        if len(buffer) > MAX_SIZE:
            print(f"  ⚠ OVERFLOW! Buffer has {len(buffer)} items but max is {MAX_SIZE}!")
        time.sleep(0.2)

def consumer():
    for _ in range(6):
        time.sleep(0.5)  # consumer is slower
        if buffer:
            item = buffer.pop(0)
            print(f"  [CONSUME] {item}  buffer={buffer}")
        else:
            print(f"  [CONSUME] CRASH — buffer is empty, nothing to consume!")

print(f"Producer-Consumer, NO protection (max buffer={MAX_SIZE}):\n")
t1 = threading.Thread(target=producer)
t2 = threading.Thread(target=consumer)
t1.start(); t2.start()
t1.join(); t2.join()

print(f"\nFinal buffer: {buffer}")
print("Problems: buffer overflows, consumer may read empty buffer.")
print("We need: producer WAITS when full, consumer WAITS when empty.")
