from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from .config import COLORS, FONT, MONO, STATUS_COLOR, STATUS_ICON, STATUS_TEXT
from .models import Paper


class ScrollableFrame(QScrollArea):
    """可滚动容器：body 为内容区，通过 add_widget 添加子控件。"""

    def __init__(self, parent: QWidget | None = None, *, bg: str | None = None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.body = QWidget(self)
        self.body.setStyleSheet(f"background: {bg or COLORS['canvas']};")
        self.setWidget(self.body)
        self.layout = QVBoxLayout(self.body)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(9)
        self.layout.addStretch(1)

    def add_widget(self, widget: QWidget) -> None:
        self.layout.insertWidget(self.layout.count() - 1, widget)

    def clear(self) -> None:
        while self.layout.count() > 1:
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()


class PaperCard(QFrame):
    def __init__(self, parent: QWidget, paper: Paper, selected: bool, on_select: Callable[[int], None]):
        super().__init__(parent)
        self.paper = paper
        self.on_select = on_select
        self.setObjectName("PaperCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 13, 15, 13)
        layout.setSpacing(0)

        top = QHBoxLayout()
        top.setSpacing(0)
        status_label = QLabel(f"{STATUS_ICON.get(paper.status, '●')}  {STATUS_TEXT.get(paper.status, '未分类')}")
        status_label.setStyleSheet(
            f"color: {STATUS_COLOR.get(paper.status, COLORS['muted'])}; font-size: 9pt; font-weight: bold; background: transparent;"
        )
        year_label = QLabel(str(paper.year))
        year_label.setStyleSheet(f"color: {COLORS['subtle']}; font-size: 8pt; font-family: '{MONO}'; background: transparent;")
        top.addWidget(status_label)
        top.addStretch(1)
        top.addWidget(year_label)
        layout.addLayout(top)

        title = paper.title if len(paper.title) <= 78 else paper.title[:78] + "…"
        title_label = QLabel(title)
        title_label.setWordWrap(True)
        title_label.setStyleSheet(f"color: {COLORS['ink']}; font-size: 10pt; font-weight: bold; background: transparent;")
        layout.addWidget(title_label)
        layout.addSpacing(4)

        summary = f"{paper.venue}  ·  {paper.summary}" if paper.summary else paper.venue
        summary_label = QLabel(summary)
        summary_label.setWordWrap(True)
        summary_label.setStyleSheet(f"color: {COLORS['muted']}; font-size: 8pt; background: transparent;")
        layout.addWidget(summary_label)

        if paper.tags:
            tags_row = QHBoxLayout()
            tags_row.setSpacing(5)
            for tag in paper.tags[:3]:
                tag_label = QLabel(tag)
                tag_label.setStyleSheet(
                    "background-color: #edf3ed; color: #6d8278; font-size: 8pt; padding: 3px 6px; border-radius: 3px;"
                )
                tags_row.addWidget(tag_label)
            tags_row.addStretch(1)
            layout.addSpacing(10)
            layout.addLayout(tags_row)

        self.set_selected(selected)

    def set_selected(self, selected: bool) -> None:
        border = COLORS["green_text"] if selected else COLORS["line"]
        surface = COLORS["white"] if selected else COLORS["paper"]
        self.setStyleSheet(
            f"QFrame#PaperCard {{ background-color: {surface}; border: 1px solid {border}; border-radius: 4px; }}"
        )

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_select(self.paper.id)
        super().mousePressEvent(event)
