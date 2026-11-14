from math import isfinite
from types import SimpleNamespace


class Data(SimpleNamespace):
    def __init__(self, file=None, data_file=None, **kwargs):
        if file is None and data_file is None:
            if "pos_verts" in kwargs:
                if "vertices" in kwargs or "positions" in kwargs:
                    raise ValueError("pos_verts와 vertices 또는 positions를 함께 지정할 수 없습니다.")
                entries = kwargs.pop("pos_verts")
                if not isinstance(entries, (list, tuple)):
                    raise ValueError("pos_verts는 [이름, [x, y]] 항목의 목록이어야 합니다.")
                vertices, positions = [], []
                for entry in entries:
                    if (not isinstance(entry, (list, tuple)) or len(entry) != 2
                            or not isinstance(entry[0], str)
                            or not isinstance(entry[1], (list, tuple)) or len(entry[1]) != 2
                            or not all(type(c) in (int, float) and isfinite(c) for c in entry[1])):
                        raise ValueError("pos_verts 항목에는 정점 이름과 유한한 좌표 두 개가 필요합니다.")
                    name, point = entry
                    vertices.append(name)
                    positions.append(list(point))
                kwargs.update(vertices=vertices, positions=positions)
            super().__init__(**kwargs)
            return

        from .runner import resolve_data

        data = resolve_data(file, kwargs, data_file=data_file)
        super().__init__(**data.__dict__)
