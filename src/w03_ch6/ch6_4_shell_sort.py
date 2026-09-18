import pyvisalgo as va


DATA_FILE = "data/elementary_sort.json"

vis = va.visualizer("shell_sort")


def shell_sort(array):
    # 정렬 함수는 전달받은 리스트를 직접 바꿉니다.
    # 셸 정렬은 gap 간격으로 나눈 부분 배열에 삽입 정렬을 적용합니다.
    count = len(array)

    return array


while va.running():
    data = va.next_data(__file__, data_file=DATA_FILE)
    array = list(data.array)

    vis.setup(data)
    print("정렬 전:", array)
    print("정렬 후:", shell_sort(array))
    vis.finish()
    vis.wait()
