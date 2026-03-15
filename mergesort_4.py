def merge_4(A, B, C, D):
    """Merge 4 arrays passed in sorted order."""
    # TODO: Your code here.
    result = []

    i = j = k = l = 0

    while i < len(A) or j < len(B) or k < len(C) or l < len(D):
    
        candidates = []

        if i < len(A): candidates.append((A[i], 0))
        if j < len(B): candidates.append((B[j], 1))

        if k < len(C): candidates.append((C[k], 2))
        if l < len(D): candidates.append((D[l], 3))

        min_val, min_src = candidates[0]

        for val, src in candidates[1:]:
            if val < min_val:

                min_val, min_src = val, src

        result.append(min_val)

        if   min_src == 0: i += 1

        elif min_src == 1: j += 1

        elif min_src == 2: k += 1

        else:              l += 1

    return result


def mergesort_4(arr):
    """Sort `arr` using mergesort with 4 instead of 2 subproblems."""
    # TODO: Your code here. You should use `merge_4` to combine
    # solutions from subproblems.
    n = len(arr)

    if n <= 1:
        return arr

    mid1 = n // 4
    mid2 = n // 2
    mid3 = 3 * n // 4

    A = mergesort_4(arr[:mid1])

    B = mergesort_4(arr[mid1:mid2])

    C = mergesort_4(arr[mid2:mid3])
    
    D = mergesort_4(arr[mid3:])

    return merge_4(A, B, C, D)
