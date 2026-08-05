from pathlib import Path


APP_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = APP_DIR / "paperbase_data.json"
FONT = "Microsoft YaHei UI"
MONO = "Consolas"

COLORS = {
    "sidebar": "#153733",
    "sidebar_hover": "#2a5b50",
    "sidebar_text": "#d7e7df",
    "sidebar_muted": "#76978d",
    "canvas": "#f2f5ef",
    "paper": "#fbfcf8",
    "white": "#ffffff",
    "ink": "#1b2b28",
    "muted": "#7b8a83",
    "subtle": "#a3afa9",
    "line": "#dfe7df",
    "green": "#24564b",
    "green_hover": "#347568",
    "green_light": "#e2f1e6",
    "green_text": "#4f866c",
    "orange": "#e58b58",
    "orange_light": "#f8e9df",
    "yellow": "#e6b65f",
    "yellow_light": "#fff8e7",
    "blue": "#6aa4c5",
    "purple": "#9076bb",
    "danger": "#b85f50",
}

STATUS_TEXT = {"reading": "正在阅读", "read": "已读", "later": "稍后阅读"}
STATUS_ICON = {"all": "▦", "reading": "●", "read": "✓", "later": "◷"}
STATUS_COLOR = {"reading": COLORS["green_text"], "read": COLORS["muted"], "later": "#b3834c"}

FIELD_STYLES = {
    "summary": {"bg": "#edf7ef", "border": "#c9e2cf", "heading": "#3e7956", "text": "#567363"},
    "innovations": {"bg": "#fff1e8", "border": "#efd3c0", "heading": "#b96946", "text": "#80604e"},
    "notes": {"bg": "#fff8e7", "border": "#efdfb6", "heading": "#9a7a3f", "text": "#766348"},
}
