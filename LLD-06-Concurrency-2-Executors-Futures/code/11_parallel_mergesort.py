"""
11 - Parallel Merge Sort
=========================
Merge sort splits work into independent halves — perfect for parallelism.
Compare: sequential vs ThreadPool (GIL blocks!) vs ProcessPool (real speedup).
"""

import time
import random
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


def merge_sort(arr):
    """Standard recursive merge sort."""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)


def merge(left, right):
    """Merge two sorted arrays."""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def sort_chunk(chunk):
    """Sort a single chunk — this is what each worker does."""
    return merge_sort(chunk)


def parallel_merge_sort(data, num_workers, executor_class):
    """Split data into chunks, sort each in parallel, merge results."""
    # Split into chunks
    chunks = [data[i::num_workers] for i in range(num_workers)]

    # Sort chunks in parallel
    with executor_class(max_workers=num_workers) as executor:
        sorted_chunks = list(executor.map(sort_chunk, chunks))

    # Merge all sorted chunks (this is sequential — Amdahl's Law!)
    result = sorted_chunks[0]
    for chunk in sorted_chunks[1:]:
        result = merge(result, chunk)

    return result


if __name__ == "__main__":
    # Generate test data
    SIZE = 500_000
    data = [random.randint(0, 1_000_000) for _ in range(SIZE)]
    print(f"Sorting {SIZE:,} numbers...\n")

    # Sequential
    start = time.time()
    seq_result = merge_sort(data.copy())
    seq_time = time.time() - start
    print(f"Sequential:        {seq_time:.2f}s")

    # ThreadPoolExecutor (CPU-bound — GIL blocks!)
    start = time.time()
    thread_result = parallel_merge_sort(data.copy(), 4, ThreadPoolExecutor)
    thread_time = time.time() - start
    print(f"ThreadPool (4):    {thread_time:.2f}s  {'(GIL — no speedup!)' if thread_time >= seq_time * 0.8 else ''}")

    # ProcessPoolExecutor (bypasses GIL)
    start = time.time()
    proc_result = parallel_merge_sort(data.copy(), 4, ProcessPoolExecutor)
    proc_time = time.time() - start
    print(f"ProcessPool (4):   {proc_time:.2f}s  {'(faster!)' if proc_time < seq_time * 0.8 else ''}")

    # Verify correctness
    expected = sorted(data)
    assert seq_result == expected, "Sequential sort incorrect!"
    assert thread_result == expected, "Thread sort incorrect!"
    assert proc_result == expected, "Process sort incorrect!"
    print(f"\nAll results verified correct.")

    # Explain
    print(f"\n--- Analysis ---")
    print(f"Merge sort is CPU-bound (pure computation).")
    print(f"ThreadPool can't help — GIL prevents parallel Python execution.")
    print(f"ProcessPool helps — each process has its own GIL.")
    print(f"The merge step is sequential — that's Amdahl's Law in action.")
    if seq_time > 0:
        print(f"Theoretical max speedup (4 workers, ~10% merge): 3.1x")
        print(f"Actual ProcessPool speedup: {seq_time/proc_time:.1f}x")
