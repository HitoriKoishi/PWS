from __future__ import annotations

import json
import re
from pathlib import Path

from .config import WINDOW_STATE_FILE


DEFAULT_WIDTH = 820
DEFAULT_HEIGHT = 860
MIN_WIDTH = 720
MIN_HEIGHT = 700


def _screen_limits(parent):
    screen_width = parent.winfo_screenwidth()
    screen_height = parent.winfo_screenheight()
    return screen_width, screen_height, max(620, screen_width - 40), max(560, screen_height - 90)


def editor_min_size(parent) -> tuple[int, int]:
    _, _, available_width, available_height = _screen_limits(parent)
    return min(MIN_WIDTH, available_width), min(MIN_HEIGHT, available_height)


def editor_geometry(parent) -> str:
    screen_width, screen_height, available_width, available_height = _screen_limits(parent)
    minimum_width, minimum_height = editor_min_size(parent)
    width = min(DEFAULT_WIDTH, available_width)
    height = min(DEFAULT_HEIGHT, available_height)
    x = max(10, (screen_width - width) // 2)
    y = max(10, (screen_height - height) // 2)
    saved = _load_state()
    if saved:
        width = max(minimum_width, min(saved.get("width", width), available_width))
        height = max(minimum_height, min(saved.get("height", height), available_height))
        x = max(10, min(saved.get("x", x), screen_width - width - 10))
        y = max(10, min(saved.get("y", y), screen_height - height - 50))
    return f"{width}x{height}+{x}+{y}"


def save_editor_geometry(window) -> None:
    match = re.match(r"^(\d+)x(\d+)\+(-?\d+)\+(-?\d+)$", window.geometry())
    if not match:
        return
    width, height, x, y = (int(value) for value in match.groups())
    temporary = Path(f"{WINDOW_STATE_FILE}.tmp")
    temporary.write_text(json.dumps({"width": width, "height": height, "x": x, "y": y}, indent=2), encoding="utf-8")
    temporary.replace(WINDOW_STATE_FILE)


def _load_state() -> dict:
    try:
        payload = json.loads(WINDOW_STATE_FILE.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}
