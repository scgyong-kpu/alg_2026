import pyvisalgo as va


DATA_FILE = "data/radix_lsd.json"

vis = va.visualizer("radix_lsd")


def radix_sort_lsd(array):
    # LSD 기수 정렬은 1의 자리부터 각 자릿수를 안정적으로 정렬합니다.
    # 이후 커밋에서 각 자리수에 계수 정렬을 적용합니다.
    return array


while va.running():
    data = va.next_data(__file__, data_file=DATA_FILE)
    array = list(data.array)

    vis.setup(data)
    print("정렬 전:", array)
    print("정렬 후:", radix_sort_lsd(array))
    vis.wait()
