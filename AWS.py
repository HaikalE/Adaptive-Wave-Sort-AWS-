import random
import math
from itertools import chain

def adaptive_wave_sort(arr):
    CACHE_LINE = 16  # Asumsi 16 elemen per cache line (64 byte)
    
    if len(arr) <= CACHE_LINE:
        return branchless_insertion_sort(arr)
    
    # 1. Dynamic Sampling
    sample_size = int(math.sqrt(len(arr))) + 1
    sample = random.sample(arr, sample_size)
    thresholds = calculate_dynamic_thresholds(sample)
    
    # 2. Cache-Blocked Partitioning
    buckets = [[] for _ in range(len(thresholds)+1)]
    
    for block in split_into_cache_blocks(arr, CACHE_LINE):
        for elem in block:
            # Bitwise bucket assignment
            bucket_idx = sum(elem > t for t in thresholds)
            buckets[bucket_idx].append(elem)
        
        # Update thresholds adaptif
        thresholds = adapt_thresholds(thresholds, block)
    
    # 3. Rekursi dan Merging
    result = []
    for bucket in buckets:
        if bucket:
            sorted_bucket = adaptive_wave_sort(bucket)
            result = cache_aware_merge(result, sorted_bucket)
    
    return result

def calculate_dynamic_thresholds(sample):
    sample.sort()
    n = len(sample)
    return [
        sample[n//4],
        sample[n//2],
        sample[3*n//4]
    ]

def split_into_cache_blocks(arr, block_size):
    return [arr[i:i+block_size] for i in range(0, len(arr), block_size)]

def adapt_thresholds(current_thresholds, block):
    if not block:
        return current_thresholds
    
    avg = sum(block) / len(block)
    return [t ^ int(avg) & 0xFFFF for t in current_thresholds]

def branchless_insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i-1
        
        while j >= 0 and arr[j] > key:
            arr[j+1] = arr[j]
            j -= 1
        
        arr[j+1] = key
    return arr

def cache_aware_merge(left, right):
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# Test case
if __name__ == "__main__":
    test_cases = {
        "Random": [random.randint(0, 10000) for _ in range(1000)],
        "Sorted": list(range(1000)),
        "Reversed": list(range(1000, 0, -1)),
        "Skewed": [1]*500 + [1000]*500
    }
    
    for name, case in test_cases.items():
        sorted_arr = adaptive_wave_sort(case.copy())
        assert sorted_arr == sorted(case), f"Test {name} failed!"
        print(f"Test {name} passed!")
