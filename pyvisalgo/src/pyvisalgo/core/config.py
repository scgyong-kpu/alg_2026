import copy
import json
import os
import sys
from pathlib import Path


DEFAULT_CONFIG = {
    "window": {
        "width": 1280,
        "height": 720,
    },
    "font": {
        "scale": 1.0,
    },
    "speed": 1.0,
}


def get_config_path():
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "pyvisalgo" / "config.json"


def load_config(path=None):
    config = copy.deepcopy(DEFAULT_CONFIG)
    path = Path(path) if path is not None else get_config_path()
    if not path.exists():
        return config

    try:
        with path.open("r", encoding="utf-8") as file:
            user_config = json.load(file)
    except (OSError, json.JSONDecodeError):
        return config

    _merge_dict(config, user_config)
    return config


def save_config(config, path=None):
    path = Path(path) if path is not None else get_config_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(config, file, ensure_ascii=False, indent=2)
            file.write("\n")
    except OSError:
        return False
    return True


def _merge_dict(target, source):
    if not isinstance(source, dict):
        return

    for key, value in source.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _merge_dict(target[key], value)
        else:
            target[key] = value
