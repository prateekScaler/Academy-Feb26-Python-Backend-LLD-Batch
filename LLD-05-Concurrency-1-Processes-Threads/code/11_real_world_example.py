"""
11 - Real World Example: Restaurant Order Processing

A realistic simulation of what happens when your Django server
processes a restaurant order:

  1. Receive order          (instant)
  2. Call payment API       (I/O - 2 sec)
  3. Prepare the food       (CPU - computation)
  4. Send email notification (I/O - 1 sec)
  5. Send SMS notification   (I/O - 1 sec)

Sequential vs Threaded — see the real difference!

Run: python 11_real_world_example.py
"""

import time
import threading


# ---- Simulated Tasks ----

def receive_order(order_id):
    """Receive and validate the order."""
    print(f"    [Order #{order_id}] Received and validated")
    time.sleep(0.1)


def call_payment_api(order_id):
    """Call Razorpay/Stripe to process payment (I/O-bound)."""
    start = time.time()
    print(f"    [Order #{order_id}] Calling payment API...")
    time.sleep(2)  # Waiting for Razorpay response
    print(f"    [Order #{order_id}] Payment confirmed! ({time.time()-start:.1f}s)")


def prepare_food(order_id):
    """Simulate food preparation (CPU-bound computation)."""
    start = time.time()
    print(f"    [Order #{order_id}] Preparing food...")
    # Simulate some computation (recipe calculations, inventory updates)
    total = sum(i * i for i in range(2_000_000))
    print(f"    [Order #{order_id}] Food ready! ({time.time()-start:.1f}s)")


def send_email(order_id):
    """Send order confirmation email (I/O-bound)."""
    start = time.time()
    print(f"    [Order #{order_id}] Sending email...")
    time.sleep(1)  # Waiting for email service
    print(f"    [Order #{order_id}] Email sent! ({time.time()-start:.1f}s)")


def send_sms(order_id):
    """Send SMS notification (I/O-bound)."""
    start = time.time()
    print(f"    [Order #{order_id}] Sending SMS...")
    time.sleep(1)  # Waiting for SMS gateway
    print(f"    [Order #{order_id}] SMS sent! ({time.time()-start:.1f}s)")


# ---- Approach 1: Sequential ----

def process_order_sequential(order_id):
    """Process everything one step at a time."""
    receive_order(order_id)
    call_payment_api(order_id)
    prepare_food(order_id)
    send_email(order_id)
    send_sms(order_id)


# ---- Approach 2: Threaded (smart) ----

def process_order_threaded(order_id):
    """Use threads for I/O-bound steps that can overlap."""

    # Step 1: Receive order (must happen first)
    receive_order(order_id)

    # Step 2: Payment must succeed before we prepare food
    call_payment_api(order_id)

    # Step 3: Prepare food + send notifications IN PARALLEL
    # (food prep can happen while notifications are sent)
    food_thread = threading.Thread(target=prepare_food, args=(order_id,))
    email_thread = threading.Thread(target=send_email, args=(order_id,))
    sms_thread = threading.Thread(target=send_sms, args=(order_id,))

    food_thread.start()
    email_thread.start()
    sms_thread.start()

    food_thread.join()
    email_thread.join()
    sms_thread.join()


def main():
    print("=" * 60)
    print("  REAL WORLD: Restaurant Order Processing")
    print("=" * 60)
    print()
    print("  Steps: receive -> payment API -> prepare food")
    print("                                -> send email")
    print("                                -> send SMS")
    print()

    # ---- Sequential ----
    print("  APPROACH 1: SEQUENTIAL (one step at a time)")
    print("  " + "-" * 50)
    print()

    start = time.time()
    process_order_sequential(101)
    seq_time = time.time() - start

    print()
    print(f"    Total time: {seq_time:.2f} seconds")
    print()

    # ---- Threaded ----
    print("  APPROACH 2: THREADED (overlap I/O steps)")
    print("  " + "-" * 50)
    print()

    start = time.time()
    process_order_threaded(102)
    thr_time = time.time() - start

    print()
    print(f"    Total time: {thr_time:.2f} seconds")
    print()

    # ---- Comparison ----
    saved = seq_time - thr_time
    print("=" * 60)
    print("  RESULTS")
    print("=" * 60)
    print()
    print(f"    Sequential:  {seq_time:.2f} sec")
    print(f"    Threaded:    {thr_time:.2f} sec")
    print(f"    Time saved:  {saved:.2f} sec ({saved/seq_time*100:.0f}% faster)")
    print()
    print("  Your Django server does something like this for every")
    print("  request. Using threads (or async) for I/O-bound work")
    print("  means your server can handle more users with less waiting.")
    print()
    print("  Next up in Concurrency-2: Thread Pools and Executors")
    print("  (a cleaner way to manage many threads)")
    print()


if __name__ == "__main__":
    main()
