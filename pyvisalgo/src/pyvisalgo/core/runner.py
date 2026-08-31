from copy import deepcopy
import json
import random
from pathlib import Path

from .data import Data


_state = {
    "running": True,
    "action": "start",
    "source_file": None,
    "datasets": None,
    "data_index": 0,
    "current_data": None,
}


def reset():
    _state["running"] = True
    _state["action"] = "start"
    _state["source_file"] = None
    _state["datasets"] = None
    _state["data_index"] = 0
    _state["current_data"] = None


def running():
    return _state["running"]


def set_action(action):
    _state["action"] = action
    if action == "quit":
        _state["running"] = False


def next_data(source_file, default_datasets=None, data_file=None):
    source_key = _source_key(source_file, data_file)
    if _state["source_file"] != source_key:
        _state["source_file"] = source_key
        _state["datasets"] = load_datasets(source_file, default_datasets, data_file=data_file)
        _state["data_index"] = 0
        _state["current_data"] = None

    if _state["current_data"] is None:
        _state["current_data"] = _select_data()
    elif _state["action"] == "next_data":
        _state["data_index"] += 1
        _state["current_data"] = _select_data()

    _state["action"] = "restart"
    return _copy_current_data()


def resolve_data(source_file=None, inline_fields=None, data_file=None):
    inline_fields = inline_fields or {}
    source_key = _source_key(source_file, data_file)

    if _state["source_file"] != source_key:
        _state["source_file"] = source_key
        _state["datasets"] = load_datasets(source_file, [
            {"name": "기본", "data": inline_fields},
        ], data_file=data_file)
        _state["data_index"] = -1 if inline_fields else 0
        _state["current_data"] = None

    if _state["current_data"] is None and inline_fields:
        _state["current_data"] = _with_dataset_metadata({
            "name": "코드",
            "data": Data(**inline_fields),
        }, next_name=_prepared_dataset_name(0))
    elif _state["current_data"] is None:
        _state["current_data"] = _select_data()
    elif _state["action"] == "next_data":
        _state["data_index"] += 1
        _state["current_data"] = _select_data()

    _state["action"] = "restart"
    return _copy_current_data()


def run_visualizer(vis, source_file, algorithm, default_datasets=None):
    reset()

    while running():
        values = next_data(source_file, default_datasets)
        result = algorithm(values)
        print("결과:", result)
        action = vis.end()
        if action == "quit":
            break


def load_datasets(source_file, default_datasets=None, data_file=None):
    default_datasets = default_datasets or [
        {"name": "기본", "values": [17, 29, 12, 41, 33, 58, 24, 52, 66, 45]},
    ]
    data_file = _find_data_file(source_file, data_file)
    if data_file is None:
        return {
            "mode": "prepared",
            "datasets": _normalize_datasets(default_datasets),
            "random": None,
        }

    with data_file.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return {
        "mode": data.get("mode", "prepared"),
        "datasets": _normalize_datasets(data.get("datasets", [])) or _normalize_datasets(default_datasets),
        "random": data.get("random"),
    }


def _select_data():
    data_config = _state["datasets"]
    mode = data_config["mode"]

    if mode == "random":
        return _with_dataset_metadata(_make_random_data(data_config["random"]), next_name="랜덤")
    if mode == "shuffle":
        return _with_dataset_metadata(
            random.choice(data_config["datasets"]),
            total=len(data_config["datasets"]),
            next_name="무작위 선택",
        )
    if mode == "mixed":
        choices = data_config["datasets"] + [_make_random_data(data_config["random"])]
        return _with_dataset_metadata(random.choice(choices), total=len(data_config["datasets"]), next_name="무작위 선택")

    datasets = data_config["datasets"]
    index = _state["data_index"] % len(datasets)
    next_index = (index + 1) % len(datasets)
    return _with_dataset_metadata(datasets[index], index=index + 1, total=len(datasets), next_name=datasets[next_index]["name"])


def _with_dataset_metadata(dataset, index=None, total=None, next_name=None):
    data = deepcopy(dataset["data"])
    setattr(data, "_dataset_name", dataset.get("name", ""))
    setattr(data, "_dataset_index", index)
    setattr(data, "_dataset_count", total)
    setattr(data, "_next_dataset_name", next_name or "")
    return {**dataset, "data": data}


def _copy_current_data():
    return deepcopy(_state["current_data"]["data"])


def _prepared_dataset_name(index):
    datasets = (_state["datasets"] or {}).get("datasets", [])
    if not datasets:
        return ""
    return datasets[index % len(datasets)]["name"]


def _find_data_file(source_file, data_file=None):
    source = Path(source_file) if source_file is not None else None
    if data_file is not None:
        direct = Path(data_file)
        candidates = []
        if direct.is_absolute():
            candidates.append(direct)
        else:
            if source is not None:
                candidates.append(source.parent / direct)
            candidates.append(direct)
        for path in candidates:
            if path.exists():
                return path
        return None

    source = Path(source_file)
    candidates = [
        source.parent / "data" / f"{source.stem}.json",
        source.with_suffix(".json"),
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def _source_key(source_file, data_file=None):
    if data_file is None:
        return str(source_file)
    return f"{source_file or ''}|{data_file}"


def _make_random_data(random_config):
    random_config = random_config or {}
    count = int(random_config.get("count", 10))
    low = int(random_config.get("min", 1))
    high = int(random_config.get("max", 99))
    kind = random_config.get("kind", "array")
    rng = random.Random(random_config["seed"]) if "seed" in random_config else random
    values = [rng.randint(low, high) for _ in range(count)]

    if kind == "search_seq":
        target_rule = random_config.get("target", "mixed")
        if target_rule == "present":
            target = rng.choice(values)
        elif target_rule == "absent":
            target = _absent_value(values, low, high)
        elif target_rule == "mixed":
            target = rng.choice(values) if rng.choice([True, False]) else _absent_value(values, low, high)
        else:
            target = target_rule
        return {
            "name": "랜덤",
            "data": Data(array=values, target=target),
        }

    return {
        "name": "랜덤",
        "data": Data(array=values),
    }


def _normalize_datasets(raw_datasets):
    datasets = []
    for index, item in enumerate(raw_datasets, start=1):
        if isinstance(item, list):
            data = Data(array=item)
            name = f"데이터 {index}"
        elif isinstance(item, dict):
            name = item.get("name", f"데이터 {index}")
            if "random" in item and isinstance(item["random"], dict):
                data = _make_random_data(item["random"])["data"]
            elif "data" in item and isinstance(item["data"], dict):
                data = Data(**item["data"])
            elif "values" in item:
                data = Data(array=item["values"])
            else:
                continue
        else:
            continue

        datasets.append({"name": name, "data": data})
    return datasets


def _absent_value(values, low, high):
    for candidate in range(low, high + 2):
        if candidate not in values:
            return candidate
    return high + 1
