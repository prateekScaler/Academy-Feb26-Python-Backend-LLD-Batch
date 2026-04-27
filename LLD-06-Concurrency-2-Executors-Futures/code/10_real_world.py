"""
10_real_world.py — Real-world example: Django background job
=============================================================
Imagine your Django app needs to:
  1. Verify 20 payments via an external API (I/O-bound)
  2. Generate 8 invoice PDFs (CPU-bound)

This is what a background job (like Celery) does internally.
"""

import time
import os
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed


def timestamp():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


# ---------------------------------------------------------------------------
# TASK 1: Verify payments via API (I/O-bound — use threads)
# ---------------------------------------------------------------------------
def verify_payment(payment_id):
    """Call payment gateway API to verify a transaction."""
    delay = random.uniform(0.3, 1.5)  # Network latency varies
    time.sleep(delay)

    # Simulate: most succeed, a few fail
    if payment_id in [5, 13]:
        raise ConnectionError(f"Payment #{payment_id}: Gateway timeout after {delay:.1f}s")

    amount = random.randint(10, 500)
    return {
        "payment_id": payment_id,
        "status": "verified",
        "amount": amount,
        "latency": round(delay, 2),
    }


# ---------------------------------------------------------------------------
# TASK 2: Generate invoice PDFs (CPU-bound — use processes)
# ---------------------------------------------------------------------------
def generate_invoice_pdf(invoice_id):
    """Generate a PDF invoice (CPU-heavy: layout, rendering, compression)."""
    # Simulate CPU work with actual computation
    total = 0
    for i in range(2_000_000):
        total += i * i

    pages = random.randint(1, 5)
    return {
        "invoice_id": invoice_id,
        "pages": pages,
        "size_kb": pages * random.randint(50, 200),
    }


def run_demo():
    print("=" * 60)
    print("REAL-WORLD SCENARIO: End-of-day batch job")
    print("=" * 60)
    print(f"  Machine: {os.cpu_count()} CPU cores")
    print(f"  Tasks:   20 payment verifications + 8 invoice PDFs\n")

    overall_start = time.perf_counter()

    # ===================================================================
    # PHASE 1: Verify 20 payments (I/O-bound -> ThreadPoolExecutor)
    # ===================================================================
    print("-" * 60)
    print("PHASE 1: Verifying 20 payments (ThreadPoolExecutor)")
    print("-" * 60)

    payment_ids = list(range(1, 21))
    verified = 0
    failed = 0

    phase1_start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_id = {
            executor.submit(verify_payment, pid): pid
            for pid in payment_ids
        }

        for future in as_completed(future_to_id):
            pid = future_to_id[future]
            try:
                result = future.result()
                print(f"  [{timestamp()}] Payment #{pid:2d}: "
                      f"VERIFIED ${result['amount']} ({result['latency']}s)")
                verified += 1
            except Exception as e:
                print(f"  [{timestamp()}] Payment #{pid:2d}: FAILED - {e}")
                failed += 1

    phase1_time = time.perf_counter() - phase1_start
    print(f"\n  Phase 1 done: {verified} verified, {failed} failed in {phase1_time:.2f}s")

    # How long would sequential take?
    print(f"  (Sequential would take ~{20 * 0.9:.0f}s — we did it in {phase1_time:.2f}s)\n")

    # ===================================================================
    # PHASE 2: Generate 8 invoice PDFs (CPU-bound -> ProcessPoolExecutor)
    # ===================================================================
    print("-" * 60)
    print("PHASE 2: Generating 8 invoice PDFs (ProcessPoolExecutor)")
    print("-" * 60)

    invoice_ids = list(range(1001, 1009))
    workers = min(os.cpu_count(), len(invoice_ids))

    phase2_start = time.perf_counter()

    with ProcessPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(generate_invoice_pdf, invoice_ids))

    for r in results:
        print(f"  Invoice #{r['invoice_id']}: {r['pages']} pages, {r['size_kb']}KB")

    phase2_time = time.perf_counter() - phase2_start
    print(f"\n  Phase 2 done: {len(results)} PDFs generated in {phase2_time:.2f}s")

    # Sequential estimate
    seq_start = time.perf_counter()
    generate_invoice_pdf(9999)  # Time one task
    one_task_time = time.perf_counter() - seq_start
    print(f"  (Sequential would take ~{one_task_time * 8:.1f}s — we did it in {phase2_time:.2f}s)")

    # ===================================================================
    # SUMMARY
    # ===================================================================
    overall_time = time.perf_counter() - overall_start

    print()
    print("=" * 60)
    print("BATCH JOB COMPLETE")
    print("=" * 60)
    print(f"""
  Payments verified:  {verified}/{len(payment_ids)} ({failed} failed)
  Invoices generated: {len(results)}/{len(invoice_ids)}
  Total time:         {overall_time:.2f}s

  Without concurrency, this would take ~{20 * 0.9 + one_task_time * 8:.0f}s
  With concurrency:   {overall_time:.2f}s

  THIS IS WHAT YOUR DJANGO BACKGROUND JOBS DO:
    - Celery uses process pools for CPU tasks
    - Async views use thread pools for I/O tasks
    - Same concepts, same tools!
""")


if __name__ == "__main__":
    run_demo()
