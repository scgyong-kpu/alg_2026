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


def test(sort_func, max_count, data_func=None, measure_creation=False):
    # sort_func는 리스트를 받아 정렬하는 함수입니다.
    # 버블 정렬처럼 리스트를 직접 바꾸어도 되고, sorted()처럼 새 리스트를 반환해도 됩니다.
    if data_func is None:
        data_func = selected_data_func()

    counts = [count for count in PERFORMANCE_COUNTS if count <= max_count]

    if measure_creation:
        print(f"{'Count':>8} {'Create':>10} {'Elapsed':>10}")
    else:
        print(f"{'Count':>8} {'Elapsed':>10}")

    for count in counts:
        create_started_at = perf_counter()
        original = data_func(count)
        create_elapsed = perf_counter() - create_started_at
        array = list(original)

        started_at = perf_counter()
        result = sort_func(array)
        elapsed = perf_counter() - started_at

        sorted_array = array if result is None else result
        if sorted_array != sorted(original):
            raise ValueError(f"{sort_func.__name__} failed to sort {count} values")

        if measure_creation:
            print(f"{count:8d} {create_elapsed:10.3f} {elapsed:10.3f}")
        else:
            print(f"{count:8d} {elapsed:10.3f}")


def test_generated(sort_func, counts, data_func, value_count_func):
    # 큰 입력은 원본 배열을 별도로 복사하지 않고, 생성한 배열 자체를 정렬합니다.
    # 이렇게 하면 측정용 원본과 복사본이 동시에 차지하는 메모리를 줄일 수 있습니다.
    print(f"{'Count':>10} {'Values':>8} {'Create':>10} {'Elapsed':>10}")
    for count in counts:
        create_started_at = perf_counter()
        array = data_func(count)
        create_elapsed = perf_counter() - create_started_at

        started_at = perf_counter()
        result = sort_func(array)
        elapsed = perf_counter() - started_at

        sorted_array = array if result is None else result
        if not _is_sorted(sorted_array):
            raise ValueError(f"{sort_func.__name__} failed to sort {count} values")

        value_count = value_count_func(count)
        print(f"{count:10d} {value_count:8d} {create_elapsed:10.3f} {elapsed:10.3f}")


def _is_sorted(values):
    # values[1:]처럼 큰 임시 배열을 만들지 않고 오름차순 여부를 확인합니다.
    iterator = iter(values)
    try:
        previous = next(iterator)
    except StopIteration:
        return True

    for value in iterator:
        if previous > value:
            return False
        previous = value
    return True
