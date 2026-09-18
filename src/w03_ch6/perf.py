import sys
from time import perf_counter

from sort_data import nearly_sorted_values, random_values, reversed_values, sorted_values


PERFORMANCE_COUNTS = [
    100,
    1000,
    2000,
    3000,
    4000,
    5000,
    6000,
    7000,
    8000,
    9000,
    10000,
    15000,
    20000,
    30000,
    40000,
    50000,
    100000,
    200000,
    300000,
    400000,
    500000,
    750000,
    1000000,
]


DATA_FUNCS = {
    "random": random_values,
    "nearly": nearly_sorted_values,
    "sorted": sorted_values,
    "reversed": reversed_values,
}


def selected_data_func():
    # 실행할 때 데이터 종류를 지정하지 않으면 일반 random 데이터를 사용합니다.
    data_name = sys.argv[1] if len(sys.argv) > 1 else "random"

    if data_name not in DATA_FUNCS:
        names = ", ".join(DATA_FUNCS.keys())
        raise ValueError(f"unknown data: {data_name} (use: {names})")

    return DATA_FUNCS[data_name]


def test(sort_func, max_count, data_func=None):
    # sort_func는 리스트를 받아 정렬하는 함수입니다.
    # 버블 정렬처럼 리스트를 직접 바꾸어도 되고, sorted()처럼 새 리스트를 반환해도 됩니다.
    if data_func is None:
        data_func = selected_data_func()

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
