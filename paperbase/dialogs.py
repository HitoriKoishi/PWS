from __future__ import annotations

from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .config import COLORS, FIELD_STYLES, FONT, INPUT_FONT, STATUS_TEXT
from .models import Paper
from .storage import PaperRepository
from .theme import flat_button
from .window_state import editor_geometry, editor_min_size, save_editor_geometry


class PaperEditor(QDialog):
    def __init__(self, parent, paper: Paper | None, next_id: int):
        super().__init__(parent)
        self.result: Paper | None = None
        self.paper = paper
        self.next_id = next_id
        self._geometry_saved = False
        self.setWindowTitle("编辑论文" if paper else "新建论文")
        minimum_width, minimum_height = editor_min_size(self)
        self.setMinimumSize(minimum_width, minimum_height)
        width, height, x, y = editor_geometry(self)
        self.resize(width, height)
        self.move(x, y)
        self.setModal(True)
        self._build()

    def closeEvent(self, event) -> None:
        self._save_geometry()
        super().closeEvent(event)

    def _save_geometry(self) -> None:
        if not self._geometry_saved:
            save_editor_geometry(self)
            self._geometry_saved = True

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(30, 25, 30, 25)
        outer.setSpacing(0)

        title = QLabel("编辑论文" if self.paper else "新建论文")
        title.setStyleSheet(f"color: {COLORS['ink']}; font-size: 20pt; font-weight: bold; background: transparent;")
        outer.addWidget(title)
        subtitle = QLabel("把一篇论文整理成可复用的研究资产")
        subtitle.setStyleSheet(f"color: {COLORS['muted']}; font-size: 9pt; background: transparent;")
        outer.addWidget(subtitle)
        outer.addSpacing(18)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        form = QWidget()
        form.setStyleSheet(f"background: {COLORS['paper']};")
        form_layout = QVBoxLayout(form)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(0)
        scroll.setWidget(form)
        outer.addWidget(scroll, 1)

        self.fields: dict[str, QLineEdit | QComboBox | QTextEdit] = {}
        self._entry(form_layout, "title", "论文名称 *", self.paper.title if self.paper else "")
        self._entry(form_layout, "venue", "会议 / 期刊 *", self.paper.venue if self.paper else "")

        meta = QHBoxLayout()
        meta.setSpacing(8)
        year_box = QVBoxLayout()
        year_box.setSpacing(5)
        year_label = QLabel("年份")
        year_label.setStyleSheet(f"color: #53655c; font-size: 9pt; font-weight: bold; background: transparent;")
        year_box.addWidget(year_label)
        year_entry = QLineEdit(str(self.paper.year if self.paper else date.today().year))
        year_entry.setObjectName("FormEntry")
        year_box.addWidget(year_entry)
        self.fields["year"] = year_entry
        meta.addLayout(year_box, 1)

        status_box = QVBoxLayout()
        status_box.setSpacing(5)
        status_label = QLabel("阅读状态")
        status_label.setStyleSheet(f"color: #53655c; font-size: 9pt; font-weight: bold; background: transparent;")
        status_box.addWidget(status_label)
        status = QComboBox()
        status.addItems(list(STATUS_TEXT.values()))
        status.setCurrentText(STATUS_TEXT.get(self.paper.status, "正在阅读") if self.paper else "正在阅读")
        status_box.addWidget(status)
        self.fields["status"] = status
        meta.addLayout(status_box, 1)
        form_layout.addLayout(meta)

        self._entry(form_layout, "tags", "标签（用逗号分隔）", ", ".join(self.paper.tags) if self.paper else "")
        self._pdf_picker(form_layout, self.paper.pdf_path if self.paper else "")
        self._text(form_layout, "summary", "≡  概要", self.paper.summary if self.paper else "", 4)
        self._text(form_layout, "innovations", "✳  创新点（每行一个）", "\n".join(self.paper.innovations) if self.paper else "", 4)
        self._text(form_layout, "notes", "▤  我的笔记", self.paper.notes if self.paper else "", 4)

        footer = QHBoxLayout()
        footer.setSpacing(9)
        footer.addStretch(1)
        cancel = flat_button(None, "取消", self.reject, object_name="GhostButton")
        footer.addWidget(cancel)
        save = flat_button(None, "保存论文  ↗", self._save, object_name="PrimaryButton")
        footer.addWidget(save)
        outer.addSpacing(20)
        outer.addLayout(footer)

    def _entry(self, layout, key: str, label: str, value: str) -> None:
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"color: #53655c; font-size: 9pt; font-weight: bold; background: transparent;")
        layout.addWidget(label_widget)
        layout.addSpacing(5)
        entry = QLineEdit(value)
        entry.setObjectName("FormEntry")
        layout.addWidget(entry)
        layout.addSpacing(10)
        self.fields[key] = entry

    def _pdf_picker(self, layout, value: str) -> None:
        label_widget = QLabel("PDF 文件")
        label_widget.setStyleSheet("color: #53655c; font-size: 9pt; font-weight: bold; background: transparent;")
        layout.addWidget(label_widget)
        layout.addSpacing(5)
        row = QHBoxLayout()
        row.setSpacing(8)
        self.pdf_path_edit = QLineEdit(value)
        self.pdf_path_edit.setObjectName("FormEntry")
        self.pdf_path_edit.setPlaceholderText("选择本地 PDF 文件（可选）")
        row.addWidget(self.pdf_path_edit, 1)
        browse = flat_button(None, "浏览…", self._browse_pdf, object_name="GhostButton")
        row.addWidget(browse)
        layout.addLayout(row)
        layout.addSpacing(10)

    def _browse_pdf(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "选择 PDF 文件", "", "PDF 文件 (*.pdf)")
        if path:
            self.pdf_path_edit.setText(path)

    def _text(self, layout, key: str, label: str, value: str, height: int) -> None:
        style = FIELD_STYLES[key]
        section = QFrame()
        section.setStyleSheet(
            f"QFrame {{ background-color: {style['bg']}; border: 1px solid {style['border']}; border-radius: 4px; }}"
        )
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(12, 10, 12, 10)
        section_layout.setSpacing(7)
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"color: {style['heading']}; font-size: 9pt; font-weight: bold; background: transparent;")
        section_layout.addWidget(label_widget)
        text = QTextEdit(value)
        text.setFrameShape(QFrame.Shape.NoFrame)
        text.setStyleSheet(
            f"QTextEdit {{ background-color: {style['border']}; border: none; color: {style['text']}; "
            f"font-family: '{INPUT_FONT}'; font-size: 10pt; selection-background-color: {style['heading']}; "
            f"selection-color: #ffffff; background-clip: border; }} "
            f"QTextEdit {{ background-clip: border; }} "
            f"QTextEdit > QWidget {{ background-color: {style['border']}; border: none; }}"
        )
        text.setMinimumHeight(height * 22)
        section_layout.addWidget(text)
        layout.addWidget(section)
        layout.addSpacing(12)
        self.fields[key] = text

    def _save(self) -> None:
        title = self.fields["title"].text().strip()
        venue = self.fields["venue"].text().strip()
        if not title or not venue:
            QMessageBox.warning(self, "信息不完整", "请填写论文名称和会议 / 期刊。")
            return
        try:
            year = int(self.fields["year"].text() or date.today().year)
        except ValueError:
            QMessageBox.warning(self, "年份格式错误", "年份必须是数字。")
            return
        status = next(key for key, value in STATUS_TEXT.items() if value == self.fields["status"].currentText())
        tags = [item.strip() for item in self.fields["tags"].text().replace("，", ",").split(",") if item.strip()]
        summary = self.fields["summary"].toPlainText().strip()
        innovations = [item.strip() for item in self.fields["innovations"].toPlainText().splitlines() if item.strip()]
        notes = self.fields["notes"].toPlainText().strip()
        self.result = Paper(
            self.paper.id if self.paper else self.next_id,
            title,
            venue,
            year,
            status,
            tags,
            summary,
            innovations,
            notes,
            "刚刚更新",
            date.today().isoformat(),
            self.pdf_path_edit.text().strip(),
        )
        self.accept()


def edit_paper(parent, paper: Paper | None, papers: list[Paper]) -> Paper | None:
    dialog = PaperEditor(parent, paper, PaperRepository.next_id(papers))
    dialog.exec()
    return dialog.result
