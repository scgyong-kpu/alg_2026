import pyvisalgo as va


DATA_FILE = "data/elementary_sort.json"

vis = va.visualizer("bubble_sort")


def bubble_sort(array):
    # 정렬 함수는 전달받은 리스트를 직접 바꿉니다.
    # Python에서 리스트는 mutable 객체이므로, 함수 안에서 바꾼 내용이 호출한 쪽에도 보입니다.
    return array


while va.running():
    data = va.next_data(__file__, data_file=DATA_FILE)
    array = list(data.array)

    vis.setup(data)
    print("정렬 전:", array)
    print("정렬 후:", bubble_sort(array))
    vis.finish()
    vis.wait()
