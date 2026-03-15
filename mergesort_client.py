"""
Test client for merge_4 and mergesort_4.

Run with:
    pytest test_mergesort_4.py -v
"""

import time
import pytest
from mergesort_4 import merge_4, mergesort_4


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_sorted(arr):
    return all(arr[i] <= arr[i + 1] for i in range(len(arr) - 1))

def naive_sort(arr):
    """Reference sort using only builtins — no imported sort libraries."""
    out = list(arr)
    for i in range(len(out)):
        for j in range(i + 1, len(out)):
            if out[j] < out[i]:
                out[i], out[j] = out[j], out[i]
    return out


# ---------------------------------------------------------------------------
# merge_4 — correctness
# ---------------------------------------------------------------------------

class TestMerge4Correctness:

    def test_basic(self):
        result = merge_4([1, 5, 9], [2, 6], [3, 7, 10], [4, 8])
        assert result == list(range(1, 11))

    def test_equal_length_arrays(self):
        result = merge_4([1, 2], [3, 4], [5, 6], [7, 8])
        assert result == list(range(1, 9))

    def test_interleaved_values(self):
        result = merge_4([1, 4, 7], [2, 5, 8], [3, 6, 9], [10, 11, 12])
        assert result == list(range(1, 13))

    def test_output_is_sorted(self):
        result = merge_4([10, 20, 30], [5, 15, 25], [1, 100], [50, 60])
        assert is_sorted(result)

    def test_preserves_all_elements(self):
        A, B, C, D = [1, 5], [2, 6], [3, 7], [4, 8]
        result = merge_4(A, B, C, D)
        assert sorted(result) == sorted(A + B + C + D)


# ---------------------------------------------------------------------------
# merge_4 — edge cases
# ---------------------------------------------------------------------------

class TestMerge4EdgeCases:

    def test_all_empty(self):
        assert merge_4([], [], [], []) == []

    def test_one_non_empty(self):
        assert merge_4([1, 2, 3], [], [], []) == [1, 2, 3]
        assert merge_4([], [4, 5], [], []) == [4, 5]

    def test_two_non_empty(self):
        assert merge_4([], [1, 3], [], [2, 4]) == [1, 2, 3, 4]

    def test_three_non_empty(self):
        assert merge_4([1], [2], [3], []) == [1, 2, 3]

    def test_single_element_each(self):
        assert merge_4([3], [1], [4], [2]) == [1, 2, 3, 4]

    def test_duplicates(self):
        result = merge_4([1, 1], [1, 2], [2, 3], [3, 3])
        assert result == [1, 1, 1, 2, 2, 3, 3, 3]

    def test_all_same_value(self):
        result = merge_4([5, 5], [5], [5, 5, 5], [5])
        assert result == [5] * 7

    def test_negative_numbers(self):
        result = merge_4([-5, -1], [-4, 0], [-3, 2], [-2, 3])
        assert result == [-5, -4, -3, -2, -1, 0, 2, 3]

    def test_large_value_range(self):
        result = merge_4([-10**9], [0], [10**9], [2 * 10**9])
        assert result == [-10**9, 0, 10**9, 2 * 10**9]


# ---------------------------------------------------------------------------
# mergesort_4 — correctness
# ---------------------------------------------------------------------------

class TestMergesort4Correctness:

    def test_basic(self):
        assert mergesort_4([3, 1, 2]) == [1, 2, 3]

    def test_five_elements(self):
        assert mergesort_4([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

    def test_matches_reference_sort(self):
        data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
        assert mergesort_4(data) == naive_sort(data)

    def test_already_sorted(self):
        data = list(range(20))
        assert mergesort_4(data) == data

    def test_reverse_sorted(self):
        data = list(range(19, -1, -1))
        assert mergesort_4(data) == list(range(20))

    def test_output_is_sorted(self):
        data = [17, 3, 99, 1, 45, 22, 8, 56, 0, 73]
        assert is_sorted(mergesort_4(data))

    def test_preserves_all_elements(self):
        data = [17, 3, 99, 1, 45, 22, 8, 56, 0, 73]
        assert sorted(mergesort_4(data)) == sorted(data)


# ---------------------------------------------------------------------------
# mergesort_4 — edge cases
# ---------------------------------------------------------------------------

class TestMergesort4EdgeCases:

    def test_empty(self):
        assert mergesort_4([]) == []

    def test_single_element(self):
        assert mergesort_4([42]) == [42]

    def test_two_elements_sorted(self):
        assert mergesort_4([1, 2]) == [1, 2]

    def test_two_elements_unsorted(self):
        assert mergesort_4([2, 1]) == [1, 2]

    def test_three_elements(self):
        assert mergesort_4([3, 1, 2]) == [1, 2, 3]

    def test_all_duplicates(self):
        assert mergesort_4([7] * 10) == [7] * 10

    def test_some_duplicates(self):
        data = [4, 2, 4, 1, 2, 3]
        assert mergesort_4(data) == naive_sort(data)

    def test_negative_numbers(self):
        data = [-3, -1, -4, -1, -5, -9]
        assert mergesort_4(data) == naive_sort(data)

    def test_mixed_positive_negative(self):
        data = [-5, 3, -2, 0, 8, -1]
        assert mergesort_4(data) == naive_sort(data)

    def test_exactly_four_elements(self):
        assert mergesort_4([4, 3, 2, 1]) == [1, 2, 3, 4]

    def test_power_of_four_length(self):
        data = list(range(15, -1, -1))  # 16 elements
        assert mergesort_4(data) == list(range(16))

    def test_non_power_of_four_length(self):
        data = list(range(13, -1, -1))  # 14 elements — uneven splits
        assert mergesort_4(data) == list(range(14))


# ---------------------------------------------------------------------------
# Performance tests
# ---------------------------------------------------------------------------

class TestPerformance:
    """Loose upper-bound timing checks. Thresholds are intentionally generous
    to avoid flakiness on slow machines; the goal is catching catastrophic
    regressions (e.g. accidentally O(n²) behaviour), not micro-benchmarking."""

    @pytest.mark.parametrize("n, max_seconds", [
        (1_000,   0.1),
        (10_000,  0.5),
        (100_000, 5.0),
    ])
    def test_mergesort_4_timing(self, n, max_seconds):
        # Worst-case-ish input: reverse sorted
        data = list(range(n, 0, -1))
        start = time.perf_counter()
        result = mergesort_4(data)
        elapsed = time.perf_counter() - start

        assert is_sorted(result), "Result is not sorted"
        assert len(result) == n, "Element count changed"
        assert elapsed < max_seconds, (
            f"mergesort_4(n={n}) took {elapsed:.3f}s, limit is {max_seconds}s"
        )

    @pytest.mark.parametrize("n, max_seconds", [
        (1_000,   0.05),
        (10_000,  0.2),
        (100_000, 2.0),
    ])
    def test_merge_4_timing(self, n, max_seconds):
        # Pre-sort four equal-length chunks so we're only timing the merge.
        quarter = n // 4
        A = list(range(0,         quarter))
        B = list(range(quarter,   2*quarter))
        C = list(range(2*quarter, 3*quarter))
        D = list(range(3*quarter, n))

        start = time.perf_counter()
        result = merge_4(A, B, C, D)
        elapsed = time.perf_counter() - start

        assert is_sorted(result)
        assert elapsed < max_seconds, (
            f"merge_4(n={n}) took {elapsed:.3f}s, limit is {max_seconds}s"
        )