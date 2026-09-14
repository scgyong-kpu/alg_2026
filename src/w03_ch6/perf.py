from time import perf_counter

from sort_data import PERFORMANCE_COUNTS, random_values


def test(sort_func, max_count, data_func=random_values):
    # sort_func는 리스트를 받아 정렬하는 함수입니다.
    # 버블 정렬처럼 리스트를 직접 바꾸어도 되고, sorted()처럼 새 리스트를 반환해도 됩니다.
    counts = [count for count in PERFORMANCE_COUNTS if count <= max_count]

    print(f"{'Count':>8} {'Elapsed':>10}")
    for count in counts:
        original = data_func(count)
        array = list(original)

        started_at = perf_counter()
        result = sort_func(array)
        elapsed = perf_counter() - started_at

        sorted_array = array if result is None else result
        if sorted_array != sorted(original):
            raise ValueError(f"{sort_func.__name__} failed to sort {count} values")

        print(f"{count:8d} {elapsed:10.3f}")
