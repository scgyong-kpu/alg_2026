"""주어진 순서대로 물건을 통에 담는 빈 패킹 실습."""

from dataclasses import dataclass, field

@dataclass
class Bin:
    free: int
    items: list[int] = field(default_factory=list)

    def add(self, size):
        self.items.append(size)
        self.free -= size


def pack(items, capacity):
    pass


if __name__ == "__main__":
    sample = Bin(100)
    sample.add(30)
    assert sample.items == [30]
    assert sample.free == 70
    print(sample)

    sample.add(45)
    assert sample.items == [30, 45]
    assert sample.free == 25
    print(sample)
