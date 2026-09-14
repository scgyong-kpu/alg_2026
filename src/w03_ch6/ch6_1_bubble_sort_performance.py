import perf


def bubble_sort_improved(array):
    # 기본 버블 정렬과 같은 방식으로 이웃한 두 값을 비교합니다.
    # 여기에 "마지막 교환이 일어난 위치"를 기록하여 다음 pass의 범위를 줄입니다.
    n = len(array)
    sorted_index = n

    # sorted_index는 정렬 완료 구간이 시작되는 위치입니다.
    # sorted_index의 왼쪽만 아직 정렬되지 않은 구간으로 보고 비교합니다.
    while sorted_index > 1:
        compare_until = sorted_index
        sorted_index = 0

        # 이웃한 두 칸을 왼쪽에서 오른쪽으로 차례대로 비교합니다.
        for left in range(compare_until - 1):
            right = left + 1

            # 왼쪽 값이 더 크면 두 값을 바꿉니다.
            # 큰 값은 한 칸 오른쪽으로 이동하고, 작은 값은 한 칸 왼쪽으로 이동합니다.
            if array[left] > array[right]:
                array[left], array[right] = array[right], array[left]
                sorted_index = right

        # 마지막 교환이 일어난 위치의 오른쪽은 이미 정렬된 구간입니다.
        # 마지막 교환 위치부터 오른쪽을 다음 pass에서 제외합니다.

        # sorted_index가 0이면 이번 pass에서 한 번도 교환하지 않았다는 뜻입니다.
        # 이 경우 while 조건이 false가 되어 정렬을 끝냅니다.

    return array


if __name__ == "__main__":
    perf.test(bubble_sort_improved, 50000)

'''
Performance test results:
   Count    Elapsed
     100      0.000
    1000      0.016
    2000      0.078
    3000      0.134
    4000      0.240
    5000      0.376
    6000      0.539
    7000      0.738
    8000      0.969
    9000      1.233
   10000      1.535
   15000      3.434
   20000      6.115
   30000     13.708
   40000     24.393
   50000     38.328
'''
