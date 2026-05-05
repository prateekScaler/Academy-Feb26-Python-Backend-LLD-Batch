"""
Merge Sort — A quick primer before we parallelize it
=====================================================
Merge sort splits the array in half, sorts each half, then merges.
This is the PERFECT algorithm for parallelism because the two halves
are INDEPENDENT — they can be sorted at the same time.

ASCII diagram of merge sort on [38, 27, 43, 3, 9, 82, 10]:

            [38, 27, 43, 3, 9, 82, 10]
                   /            \\
          [38, 27, 43, 3]    [9, 82, 10]
            /        \\         /       \\
        [38, 27]  [43, 3]  [9, 82]   [10]
         /   \\     /   \\    /   \\      |
       [38] [27] [43] [3] [9] [82]  [10]
         \\   /     \\   /    \\   /      |
        [27, 38]  [3, 43]  [9, 82]  [10]
            \\        /         \\       /
         [3, 27, 38, 43]    [9, 10, 82]
                   \\            /
          [3, 9, 10, 27, 38, 43, 82]
"""

def merge(left, right):
    """Merge two sorted lists into one sorted list."""
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # Add remaining elements
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def merge_sort(arr, depth=0):
    """Recursively sort using merge sort. Prints each step."""
    indent = "  " * depth

    if len(arr) <= 1:
        print(f"{indent}Base case: {arr}")
        return arr

    mid = len(arr) // 2
    left_half = arr[:mid]
    right_half = arr[mid:]

    print(f"{indent}Split: {arr}")
    print(f"{indent}  Left:  {left_half}")
    print(f"{indent}  Right: {right_half}")

    # Sort each half (these two calls are INDEPENDENT!)
    sorted_left = merge_sort(left_half, depth + 1)
    sorted_right = merge_sort(right_half, depth + 1)

    # Merge the sorted halves
    merged = merge(sorted_left, sorted_right)
    print(f"{indent}Merged: {sorted_left} + {sorted_right} = {merged}")

    return merged


print("=" * 60)
print("MERGE SORT — Step by Step")
print("=" * 60)

data = [38, 27, 43, 3, 9, 82, 10]
print(f"\nOriginal: {data}\n")

sorted_data = merge_sort(data)

print(f"\nSorted:   {sorted_data}")


print("\n" + "=" * 60)
print("WHY THIS IS GOOD FOR PARALLELISM")
print("=" * 60)
print("""
  At each level, the LEFT and RIGHT halves are INDEPENDENT.
  They don't read or write each other's data.

  So we can sort them in PARALLEL:
    - Thread 1 sorts the left half
    - Thread 2 sorts the right half
    - Main thread merges the results

  Next files: we'll try this with ThreadPool and ProcessPool.
""")
