import pyvisalgo as va


DATA_FILE = "data/elementary_sort.json"

vis = va.visualizer("heap_sort")


def heap_sort(array):
    # 정렬 함수는 전달받은 리스트를 직접 바꿉니다.
    # 힙 정렬은 배열을 Max Heap으로 만든 뒤 최대값을 뒤로 보냅니다.
    count = len(array)

    return array


while va.running():
    data = va.next_data(__file__, data_file=DATA_FILE)
    array = list(data.array)

    vis.setup(data)
    print("정렬 전:", array)
    print("정렬 후:", heap_sort(array))
    # vis.finish()
    vis.wait()
