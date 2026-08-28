from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtWidgets import QWidget

from .config import WINDOW_STATE_FILE


DEFAULT_WIDTH = 820
DEFAULT_HEIGHT = 860
MIN_WIDTH = 720
MIN_HEIGHT = 700


def _screen_limits(parent: QWidget):
    screen = parent.screen() or parent.window().screen()
    geometry = screen.availableGeometry()
    return geometry.width(), geometry.height(), max(620, geometry.width() - 40), max(560, geometry.height() - 90)


def editor_min_size(parent: QWidget) -> tuple[int, int]:
    _, _, available_width, available_height = _screen_limits(parent)
    return min(MIN_WIDTH, available_width), min(MIN_HEIGHT, available_height)


def editor_geometry(parent: QWidget) -> tuple[int, int, int, int]:
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
    return width, height, x, y


def save_editor_geometry(window: QWidget) -> None:
    rect = window.geometry()
    temporary = Path(f"{WINDOW_STATE_FILE}.tmp")
    temporary.write_text(
        json.dumps({"width": rect.width(), "height": rect.height(), "x": rect.x(), "y": rect.y()}, indent=2),
        encoding="utf-8",
    )
    temporary.replace(WINDOW_STATE_FILE)


def _load_state() -> dict:
    try:
        payload = json.loads(WINDOW_STATE_FILE.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}
