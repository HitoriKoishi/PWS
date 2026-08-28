from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QPushButton

from .config import COLORS, FONT, INPUT_FONT


def build_qss() -> str:
    c = COLORS
    return f"""
    * {{
        font-family: "{FONT}";
        font-size: 10pt;
        color: {c["ink"]};
    }}
    QMainWindow, QWidget#AppRoot {{
        background-color: {c["canvas"]};
    }}
    QFrame#Sidebar {{
        background-color: {c["sidebar"]};
    }}
    QLabel#Brand {{
        color: #ffffff;
        font-size: 18pt;
        font-weight: bold;
        background: transparent;
    }}
    QLabel#BrandSub {{
        color: {c["sidebar_muted"]};
        font-size: 7pt;
        font-family: "Consolas";
        background: transparent;
    }}
    QLabel#SidebarSection {{
        color: {c["sidebar_muted"]};
        font-size: 9pt;
        font-family: "Consolas";
        background: transparent;
    }}
    QPushButton#StatusButton {{
        background-color: {c["sidebar"]};
        color: {c["sidebar_text"]};
        border: none;
        text-align: left;
        padding: 9px 13px;
    }}
    QPushButton#StatusButton:hover {{
        background-color: {c["sidebar_hover"]};
    }}
    QPushButton#StatusButton:checked {{
        background-color: {c["sidebar_hover"]};
        color: #ffffff;
    }}
    QFrame#SidebarDivider {{
        background-color: #2b514b;
        min-height: 1px;
        max-height: 1px;
    }}
    QPushButton#TagMoreButton {{
        background-color: {c["sidebar"]};
        color: {c["green_text"]};
        border: none;
        text-align: left;
        padding: 7px 0px;
    }}
    QPushButton#TagMoreButton:hover {{
        color: #ffffff;
    }}
    QPushButton#TagButton {{
        background-color: {c["sidebar"]};
        color: {c["sidebar_text"]};
        border: none;
        text-align: left;
        padding: 4px 0px;
    }}
    QPushButton#TagButton:hover {{
        color: #ffffff;
    }}
    QFrame#SidebarFooter {{
        background-color: #20483f;
        border-radius: 6px;
    }}
    QLabel#FooterTitle {{
        color: #d8e8df;
        font-size: 9pt;
        background: transparent;
    }}
    QLabel#FooterSub {{
        color: #86a9a0;
        font-size: 8pt;
        background: transparent;
    }}
    QFrame#Topbar {{
        background-color: {c["paper"]};
    }}
    QLabel#Breadcrumb {{
        color: {c["subtle"]};
        font-size: 10pt;
        background: transparent;
    }}
    QLabel#ViewTitle {{
        color: #485753;
        font-size: 10pt;
        font-weight: bold;
        background: transparent;
    }}
    QPushButton#PrimaryButton {{
        background-color: {c["green"]};
        color: #ffffff;
        border: none;
        border-radius: 4px;
        padding: 9px 15px;
        font-weight: bold;
    }}
    QPushButton#PrimaryButton:hover {{
        background-color: {c["green_hover"]};
    }}
    QPushButton#GhostButton {{
        background-color: {c["white"]};
        color: {c["muted"]};
        border: 1px solid {c["line"]};
        border-radius: 4px;
        padding: 8px 12px;
    }}
    QPushButton#GhostButton:hover {{
        background-color: #eef5ef;
    }}
    QPushButton#DangerButton {{
        background-color: {c["white"]};
        color: {c["danger"]};
        border: 1px solid {c["line"]};
        border-radius: 4px;
        padding: 8px 10px;
    }}
    QPushButton#DangerButton:hover {{
        background-color: #fdf1ef;
    }}
    QPushButton#TagPopupButton {{
        background-color: {c["white"]};
        color: {c["ink"]};
        border: 1px solid {c["line"]};
        border-radius: 4px;
        padding: 10px 12px;
        text-align: left;
    }}
    QPushButton#TagPopupButton:hover {{
        background-color: #eef5ef;
    }}
    QLineEdit#SearchBox {{
        background-color: {c["white"]};
        border: 1px solid {c["line"]};
        border-radius: 4px;
        padding: 8px 8px;
        font-family: "{INPUT_FONT}";
        font-size: 9pt;
        color: {c["ink"]};
        selection-background-color: {c["green_light"]};
        selection-color: {c["ink"]};
    }}
    QLineEdit#SearchBox:focus {{
        border-color: {c["green_text"]};
    }}
    QLabel#CollectionHeading {{
        color: {c["subtle"]};
        font-size: 8pt;
        font-family: "Consolas";
        background: transparent;
    }}
    QLabel#LibraryTitle {{
        color: {c["ink"]};
        font-size: 25pt;
        font-weight: bold;
        background: transparent;
    }}
    QLabel#CountPill {{
        background-color: #e5eee6;
        color: #819189;
        font-family: "Consolas";
        font-size: 9pt;
        padding: 3px 7px;
        border-radius: 8px;
    }}
    QFrame#DetailPanel {{
        background-color: {c["paper"]};
        border: 1px solid {c["line"]};
        border-radius: 6px;
    }}
    QLabel#StatusPill {{
        background-color: {c["green_light"]};
        color: {c["green_text"]};
        font-size: 9pt;
        font-weight: bold;
        padding: 5px 9px;
        border-radius: 8px;
    }}
    QLabel#DetailTitle {{
        color: {c["ink"]};
        font-size: 20pt;
        font-weight: bold;
        background: transparent;
    }}
    QLabel#DetailVenue {{
        color: {c["muted"]};
        font-size: 10pt;
        background: transparent;
    }}
    QLabel#TagLine {{
        color: {c["muted"]};
        font-size: 9pt;
        background: transparent;
    }}
    QLabel#ProgressText {{
        color: #456b59;
        font-size: 9pt;
        background: transparent;
    }}
    QFrame#InsightBox {{
        background-color: #f2f7ef;
        border: 1px solid #dfe9df;
        border-radius: 4px;
    }}
    QProgressBar {{
        background-color: #dce9df;
        border: 1px solid #dce9df;
        border-radius: 4px;
        min-height: 10px;
        max-height: 10px;
        padding: 1px;
        text-align: center;
    }}
    QProgressBar::chunk {{
        background-color: #78b78a;
        border-radius: 3px;
    }}
    QScrollArea {{
        border: none;
        background: transparent;
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: #c9d7cd;
        border-radius: 5px;
        min-height: 30px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: transparent;
    }}
    QLineEdit {{
        background-color: {c["white"]};
        border: 1px solid {c["line"]};
        border-radius: 4px;
        padding: 8px;
        font-family: "{INPUT_FONT}";
        font-size: 10pt;
        color: {c["ink"]};
        selection-background-color: {c["green_light"]};
        selection-color: {c["ink"]};
    }}
    QLineEdit:focus {{
        border-color: {c["green_text"]};
    }}
    QComboBox {{
        background-color: {c["white"]};
        border: 1px solid {c["line"]};
        border-radius: 4px;
        padding: 7px;
        font-size: 10pt;
    }}
    QComboBox:focus {{
        border-color: {c["green_text"]};
    }}
    QComboBox QAbstractItemView {{
        background-color: {c["white"]};
        selection-background-color: {c["green_light"]};
        selection-color: {c["ink"]};
    }}
    QDialog {{
        background-color: {c["paper"]};
    }}
    QMessageBox {{
        background-color: {c["paper"]};
    }}
    """


def setup(app: QApplication) -> None:
    app.setStyleSheet(build_qss())


def flat_button(
    parent,
    text: str,
    command,
    *,
    object_name: str | None = None,
    font: QFont | None = None,
    checkable: bool = False,
    checked: bool = False,
):
    button = QPushButton(text, parent)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    if object_name:
        button.setObjectName(object_name)
    if font:
        button.setFont(font)
    if checkable:
        button.setCheckable(True)
        button.setChecked(checked)

    def _on_clicked(*_args):
        command()

    button.clicked.connect(_on_clicked)
    return button
