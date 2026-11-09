"""문자 빈도가 가장 낮은 두 트리를 반복해서 합쳐 허프만 트리를 만든다."""

import pyvisalgo as va


def huffman(text, vis):
    """입력 문자열과 시각화 객체를 받는다. 트리 생성은 다음 단계에서 구현한다."""
    pass


if __name__ == "__main__":
    vis = va.visualizer("huffman")
    while va.running():
        data = va.next_data(__file__)
        # text는 공백과 줄바꿈을 포함한 원문입니다. 아직 빈도는 세지 않습니다.
        vis.setup(data)
        if not vis.stopped():
            huffman(data.text, vis)
        # R: 재실행, D: 다음 데이터, Space: 일시정지, .: 한 단계.
        # Enter: 다음 구간, 1~9: 속도, +/-: 글씨 크기, Esc: 종료.
        vis.wait()
