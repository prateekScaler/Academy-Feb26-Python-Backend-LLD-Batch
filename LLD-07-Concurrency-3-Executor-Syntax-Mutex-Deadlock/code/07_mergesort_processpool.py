"""
Merge Sort: Sequential vs ThreadPool vs ProcessPool
=====================================================
Pure Python merge sort to keep it CPU-bound.

KEY CONCEPTS DEMONSTRATED:
1. Split data into chunks (divide the work)
2. Sort each chunk in parallel (workers do independent work)
3. Merge sorted chunks back (sequential step — Amdahl's Law)

WHY heapq.merge?
- After sorting 4 chunks independently, we need to combine them
- heapq.merge does a k-way merge of already-sorted iterables
- It's efficient: O(n log k) where k = number of chunks
"""

import time
import random
import heapq
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


def merge_sort(arr):
    """Standard recursive merge sort."""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left_sorted = merge_sort(arr[:mid])
    right_sorted = merge_sort(arr[mid:])
    return merge(left_sorted, right_sorted)


def merge(left, right):
    """Merge two already-sorted lists into one sorted list."""
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


def split_into_chunks(data, num_chunks):
    """Split a list into num_chunks contiguous, roughly-equal pieces."""
    chunk_size = len(data) // num_chunks
    chunks = []
    for i in range(num_chunks):
        start = i * chunk_size
        end = len(data) if i == num_chunks - 1 else start + chunk_size
        chunks.append(data[start:end])
    return chunks


def parallel_sort_with(executor_class, chunks, workers):
    """Sort each chunk in parallel, then merge the sorted chunks."""
    with executor_class(max_workers=workers) as executor:
        sorted_chunks = list(executor.map(merge_sort, chunks))
    # heapq.merge does a k-way merge of already-sorted iterables
    return list(heapq.merge(*sorted_chunks))


def sequential_sort(chunks):
    """Sort each chunk one after another, then merge."""
    sorted_chunks = [merge_sort(c) for c in chunks]
    return list(heapq.merge(*sorted_chunks))


if __name__ == "__main__":
    SIZE = 800_000
    WORKERS = 4

    print(f"Sorting {SIZE:,} numbers with pure Python merge sort\n")

    data = [random.randint(0, 1_000_000) for _ in range(SIZE)]
    chunks = split_into_chunks(data, WORKERS)

    start = time.time()
    seq_result = sequential_sort(chunks)
    seq_time = time.time() - start
    print(f"Sequential : {seq_time:.2f}s")

    start = time.time()
    thr_result = parallel_sort_with(ThreadPoolExecutor, chunks, WORKERS)
    thr_time = time.time() - start
    print(f"ThreadPool : {thr_time:.2f}s  ({seq_time/thr_time:.1f}x)  — GIL blocks")

    start = time.time()
    proc_result = parallel_sort_with(ProcessPoolExecutor, chunks, WORKERS)
    proc_time = time.time() - start
    print(f"ProcessPool: {proc_time:.2f}s  ({seq_time/proc_time:.1f}x)  — bypasses GIL")

    expected = sorted(data)
    assert seq_result == expected, "Sequential sort is wrong!"
    assert thr_result == expected, "ThreadPool sort is wrong!"
    assert proc_result == expected, "ProcessPool sort is wrong!"
    print("\nAll three results are correctly sorted.")
