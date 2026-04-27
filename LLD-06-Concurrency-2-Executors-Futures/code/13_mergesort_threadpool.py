"""Merge sort with ThreadPoolExecutor — does it help? (Spoiler: GIL)"""
import time, random
from concurrent.futures import ThreadPoolExecutor

def merge_sort(arr):
    if len(arr) <= 1: return arr
    mid = len(arr) // 2
    return merge(merge_sort(arr[:mid]), merge_sort(arr[mid:]))

def merge(left, right):
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]: result.append(left[i]); i += 1
        else: result.append(right[j]); j += 1
    return result + left[i:] + right[j:]

data = [random.randint(0, 1_000_000) for _ in range(500_000)]
chunks = [data[i::4] for i in range(4)]

start = time.time()
[merge_sort(c) for c in chunks]
print(f"Sequential:  {time.time()-start:.2f}s")

start = time.time()
with ThreadPoolExecutor(4) as ex:
    list(ex.map(merge_sort, chunks))
print(f"ThreadPool:  {time.time()-start:.2f}s  (GIL — no speedup)")
