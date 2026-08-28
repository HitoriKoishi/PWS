from __future__ import annotations

import sys
from collections import Counter

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .config import COLORS, DATA_FILE, FIELD_STYLES, FONT, MONO, STATUS_COLOR, STATUS_ICON, STATUS_TEXT
from .dialogs import edit_paper
from .models import Paper
from .storage import PaperRepository
from .theme import flat_button, setup
from .widgets import PaperCard, ScrollableFrame


class PaperbaseApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paperbase · 个人论文工作站")
        self.resize(1420, 900)
        self.setMinimumSize(1080, 700)
        self.setObjectName("AppRoot")
        self.repository = PaperRepository(DATA_FILE)
        self.papers = self.repository.load()
        self.selected_id = self.papers[0].id if self.papers else None
        self.status_filter = "all"
        self.tag_filter: str | None = None
        self.sort_newest = True
        self.filtered: list[Paper] = []
        self.card_widgets: dict[int, PaperCard] = {}
        self.status_buttons: dict[str, QPushButton] = {}
        self.tag_buttons: dict[str, QPushButton] = {}
        self.visible_tag_keys: tuple[str, ...] | None = None
        self._build()
        self.render()

    # ---------- 布局 ----------

    def _build(self):
        central = QWidget()
        central.setObjectName("AppRoot")
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(245)
        root_layout.addWidget(sidebar)
        self._build_sidebar(sidebar)

        main = QWidget()
        main.setObjectName("AppRoot")
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        root_layout.addWidget(main, 1)
        self._build_topbar(main_layout)
        self._build_workspace(main_layout)

    def _build_sidebar(self, sidebar):
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        brand = QWidget()
        brand_layout = QVBoxLayout(brand)
        brand_layout.setContentsMargins(24, 30, 24, 0)
        brand_layout.setSpacing(2)
        brand_label = QLabel("paperbase")
        brand_label.setObjectName("Brand")
        brand_sub = QLabel("PERSONAL RESEARCH OS")
        brand_sub.setObjectName("BrandSub")
        brand_sub.setContentsMargins(34, 0, 0, 0)
        brand_layout.addWidget(brand_label)
        brand_layout.addWidget(brand_sub)
        layout.addWidget(brand)
        layout.addSpacing(46)

        workspace_label = QLabel("工作区")
        workspace_label.setObjectName("SidebarSection")
        workspace_label.setContentsMargins(24, 0, 0, 0)
        layout.addWidget(workspace_label)
        layout.addSpacing(9)
        for key, label in [("all", "全部论文"), ("reading", "正在阅读"), ("read", "已读"), ("later", "稍后阅读")]:
            button = flat_button(
                None, label, lambda value=key: self.set_status_filter(value),
                object_name="StatusButton", checkable=True,
            )
            button.setContentsMargins(13, 0, 13, 0)
            layout.addWidget(button)
            layout.addSpacing(2)
            self.status_buttons[key] = button

        divider = QFrame()
        divider.setObjectName("SidebarDivider")
        divider.setContentsMargins(24, 0, 24, 0)
        layout.addWidget(divider)
        layout.addSpacing(26)

        tags_label = QLabel("标签")
        tags_label.setObjectName("SidebarSection")
        tags_label.setContentsMargins(24, 0, 0, 0)
        layout.addWidget(tags_label)
        layout.addSpacing(9)
        self.tag_list_frame = QWidget()
        self.tag_list_layout = QVBoxLayout(self.tag_list_frame)
        self.tag_list_layout.setContentsMargins(24, 0, 24, 0)
        self.tag_list_layout.setSpacing(2)
        layout.addWidget(self.tag_list_frame)
        self.tag_more_button = flat_button(None, "查看全部标签", self.show_all_tags, object_name="TagMoreButton")
        self.tag_more_button.setContentsMargins(24, 0, 24, 0)
        layout.addWidget(self.tag_more_button)
        layout.addStretch(1)

        footer_wrap = QWidget()
        footer_wrap_layout = QVBoxLayout(footer_wrap)
        footer_wrap_layout.setContentsMargins(20, 0, 20, 20)
        footer = QFrame()
        footer.setObjectName("SidebarFooter")
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(12, 10, 12, 10)
        footer_layout.setSpacing(0)
        footer_title = QLabel("本地存储  ·  自动保存")
        footer_title.setObjectName("FooterTitle")
        footer_sub = QLabel("数据只保存在当前电脑")
        footer_sub.setObjectName("FooterSub")
        footer_layout.addWidget(footer_title)
        footer_layout.addWidget(footer_sub)
        footer_wrap_layout.addWidget(footer)
        layout.addWidget(footer_wrap)

    def _build_topbar(self, layout):
        bar = QFrame()
        bar.setObjectName("Topbar")
        bar.setFixedHeight(76)
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(30, 0, 27, 0)
        breadcrumb = QWidget()
        breadcrumb_layout = QHBoxLayout(breadcrumb)
        breadcrumb_layout.setContentsMargins(0, 0, 0, 0)
        breadcrumb_layout.setSpacing(0)
        crumb = QLabel("我的研究库  /  ")
        crumb.setObjectName("Breadcrumb")
        self.view_title = QLabel("全部论文")
        self.view_title.setObjectName("ViewTitle")
        breadcrumb_layout.addWidget(crumb)
        breadcrumb_layout.addWidget(self.view_title)
        bar_layout.addWidget(breadcrumb)
        bar_layout.addStretch(1)
        new_button = flat_button(None, "＋  新建论文", self.new_paper, object_name="PrimaryButton")
        bar_layout.addWidget(new_button)
        layout.addWidget(bar)

    def _build_workspace(self, layout):
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(27, 25, 27, 27)
        body_layout.setSpacing(13)
        library = self._build_library()
        detail = self._build_detail()
        body_layout.addWidget(library, 0)
        body_layout.addWidget(detail, 1)
        layout.addWidget(body, 1)

    def _build_library(self):
        panel = QWidget()
        panel.setObjectName("AppRoot")
        panel.setMinimumWidth(430)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        heading = QWidget()
        heading_layout = QVBoxLayout(heading)
        heading_layout.setContentsMargins(0, 0, 0, 0)
        heading_layout.setSpacing(0)
        collection = QLabel("COLLECTION / 2026")
        collection.setObjectName("CollectionHeading")
        heading_layout.addWidget(collection)
        title_line = QWidget()
        title_line_layout = QHBoxLayout(title_line)
        title_line_layout.setContentsMargins(0, 5, 0, 0)
        title_line_layout.setSpacing(9)
        library_title = QLabel("论文库")
        library_title.setObjectName("LibraryTitle")
        self.count_label = QLabel("0")
        self.count_label.setObjectName("CountPill")
        title_line_layout.addWidget(library_title)
        title_line_layout.addWidget(self.count_label, 0, Qt.AlignmentFlag.AlignVCenter)
        title_line_layout.addStretch(1)
        heading_layout.addWidget(title_line)
        layout.addWidget(heading)
        layout.addSpacing(18)

        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(8)
        search_wrap = QWidget()
        search_wrap.setStyleSheet(
            f"background: {COLORS['white']}; border: 1px solid {COLORS['line']}; border-radius: 4px;"
        )
        search_wrap_layout = QHBoxLayout(search_wrap)
        search_wrap_layout.setContentsMargins(9, 0, 8, 0)
        search_wrap_layout.setSpacing(3)
        search_icon = QLabel("⌕")
        search_icon.setStyleSheet(f"color: {COLORS['subtle']}; font-size: 19pt; background: transparent;")
        self.search_entry = QLineEdit()
        self.search_entry.setObjectName("SearchBox")
        self.search_entry.textChanged.connect(lambda *_: self.render_list())
        search_wrap_layout.addWidget(search_icon)
        search_wrap_layout.addWidget(self.search_entry, 1)
        toolbar_layout.addWidget(search_wrap, 1)
        sort_button = flat_button(None, "最近更新  ↕", self.toggle_sort, object_name="GhostButton")
        toolbar_layout.addWidget(sort_button)
        layout.addWidget(toolbar)
        layout.addSpacing(14)

        self.list_stack = QStackedWidget()
        self.card_list = ScrollableFrame(bg=COLORS["canvas"])
        self.empty_label = QLabel("没有找到论文\n尝试调整搜索词或新建一篇论文")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(f"color: {COLORS['muted']}; font-size: 10pt; background: transparent;")
        self.list_stack.addWidget(self.card_list)
        self.list_stack.addWidget(self.empty_label)
        layout.addWidget(self.list_stack, 1)
        return panel

    def _build_detail(self):
        panel = QFrame()
        panel.setObjectName("DetailPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(31, 28, 31, 28)
        layout.setSpacing(0)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(15)
        title_area = QWidget()
        title_area_layout = QVBoxLayout(title_area)
        title_area_layout.setContentsMargins(0, 0, 0, 0)
        title_area_layout.setSpacing(0)
        self.status_pill = QLabel("")
        self.status_pill.setObjectName("StatusPill")
        title_area_layout.addWidget(self.status_pill, 0, Qt.AlignmentFlag.AlignLeft)
        self.detail_title = QLabel("")
        self.detail_title.setObjectName("DetailTitle")
        self.detail_title.setWordWrap(True)
        title_area_layout.addWidget(self.detail_title)
        title_area_layout.addSpacing(6)
        self.detail_venue = QLabel("")
        self.detail_venue.setObjectName("DetailVenue")
        title_area_layout.addWidget(self.detail_venue)
        header_layout.addWidget(title_area, 1)
        action_area = QWidget()
        action_area_layout = QHBoxLayout(action_area)
        action_area_layout.setContentsMargins(0, 0, 0, 0)
        action_area_layout.setSpacing(7)
        edit_button = flat_button(None, "编辑", self.edit_paper, object_name="GhostButton")
        delete_button = flat_button(None, "删除", self.delete_paper, object_name="DangerButton")
        action_area_layout.addWidget(edit_button)
        action_area_layout.addWidget(delete_button)
        header_layout.addWidget(action_area, 0, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(header)
        layout.addSpacing(19)

        self.tag_line = QLabel("")
        self.tag_line.setObjectName("TagLine")
        layout.addWidget(self.tag_line)
        layout.addSpacing(16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        content.setStyleSheet(f"background: {COLORS['paper']};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        insight = QFrame()
        insight.setObjectName("InsightBox")
        insight_layout = QHBoxLayout(insight)
        insight_layout.setContentsMargins(12, 12, 12, 12)
        self.progress_text = QLabel("")
        self.progress_text.setObjectName("ProgressText")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedWidth(180)
        insight_layout.addWidget(self.progress_text)
        insight_layout.addStretch(1)
        insight_layout.addWidget(self.progress_bar)
        content_layout.addWidget(insight)
        content_layout.addSpacing(28)

        self.summary_text = self._section(content_layout, "summary", "≡  概要")
        self.innovation_text = self._section(content_layout, "innovations", "✳  创新点")
        self.notes_text = self._section(content_layout, "notes", "▤  我的笔记")
        content_layout.addStretch(1)

        self.date_label = QLabel("")
        self.date_label.setStyleSheet(
            f"color: {COLORS['subtle']}; font-size: 8pt; font-family: '{MONO}'; background: transparent;"
        )
        layout.addWidget(self.date_label)
        layout.addSpacing(8)
        return panel

    def _section(self, layout, key, title):
        style = FIELD_STYLES[key]
        section = QFrame()
        section.setStyleSheet(
            f"QFrame {{ background-color: {style['bg']}; border: 1px solid {style['border']}; border-radius: 4px; }}"
        )
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(15, 13, 15, 13)
        section_layout.setSpacing(8)
        label = QLabel(title)
        label.setStyleSheet(f"color: {style['heading']}; font-size: 10pt; font-weight: bold; background: transparent;")
        section_layout.addWidget(label)
        text = self._readonly_text(style["bg"], style["text"])
        section_layout.addWidget(text)
        layout.addWidget(section)
        layout.addSpacing(23)
        return text

    def _readonly_text(self, bg, fg):
        text = QTextEdit()
        text.setReadOnly(True)
        text.setStyleSheet(
            f"QTextEdit {{ background-color: {bg}; border: none; color: {fg}; font-family: '{FONT}'; font-size: 10pt; }}"
        )
        text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        return text

    # ---------- 交互 ----------

    def set_status_filter(self, value):
        self.status_filter, self.tag_filter = value, None
        self.view_title.setText({"all": "全部论文", "reading": "正在阅读", "read": "已读", "later": "稍后阅读"}[value])
        self.render()

    def set_tag_filter(self, value):
        self.status_filter, self.tag_filter = "all", value
        self.view_title.setText(value)
        self.render()

    def toggle_sort(self):
        self.sort_newest = not self.sort_newest
        self.render_list()

    def filtered_papers(self):
        query = self.search_entry.text().strip().lower()
        papers = [paper for paper in self.papers if self.status_filter == "all" or paper.status == self.status_filter]
        if self.tag_filter:
            papers = [paper for paper in papers if self.tag_filter.lower() in [tag.lower() for tag in paper.tags]]
        if query:
            papers = [paper for paper in papers if query in paper.search_text()]
        return sorted(papers, key=lambda paper: paper.id, reverse=self.sort_newest)

    def render(self):
        self.normalize_tag_filter()
        self.render_list()
        self.render_detail()
        self.update_sidebar()

    def normalize_tag_filter(self):
        available = {tag.casefold() for paper in self.papers for tag in paper.tags}
        if self.tag_filter and self.tag_filter.casefold() not in available:
            self.tag_filter = None
            self.status_filter = "all"
            self.view_title.setText("全部论文")

    def render_list(self, preserve_scroll=False):
        self.filtered = self.filtered_papers()
        visible_ids = {paper.id for paper in self.filtered}
        if self.selected_id not in visible_ids:
            self.selected_id = self.filtered[0].id if self.filtered else None
        self.card_list.clear()
        self.card_widgets = {}
        if not self.filtered:
            self.list_stack.setCurrentWidget(self.empty_label)
        else:
            self.list_stack.setCurrentWidget(self.card_list)
            for paper in self.filtered:
                card = PaperCard(self.card_list.body, paper, paper.id == self.selected_id, self.select_paper)
                self.card_list.add_widget(card)
                self.card_widgets[paper.id] = card

    def render_detail(self):
        paper = self.find_selected()
        if not paper:
            self.status_pill.setText("选择一篇论文")
            self.detail_title.setText("从左侧列表选择论文")
            self.detail_venue.setText("开始整理你的研究思路")
            self.tag_line.setText("")
            self._set_text(self.summary_text, "还没有选择论文。")
            self._set_text(self.innovation_text, "")
            self._set_text(self.notes_text, "")
            return
        self.status_pill.setText(STATUS_TEXT.get(paper.status, "未分类"))
        self.detail_title.setText(paper.title)
        self.detail_venue.setText(f"{paper.venue}  ·  {paper.year}")
        self.tag_line.setText("   ".join(f"#{tag}" for tag in paper.tags) or "暂无标签")
        self._set_text(self.summary_text, paper.summary or "还没有添加概要。")
        self._set_text(self.innovation_text, "\n".join(f"•  {item}" for item in paper.innovations) or "还没有添加创新点。")
        self._set_text(self.notes_text, paper.notes or "还没有添加笔记。")
        self.date_label.setText(f"最后编辑于 {paper.date}")
        progress = 100 if paper.status == "read" else 57 if paper.status == "reading" else 0
        self.progress_bar.setValue(progress)
        self.progress_text.setText("✓  已完成阅读" if progress == 100 else "↗  正在形成初步理解" if progress else "◷  加入阅读队列")

    def _set_text(self, widget, value):
        widget.setPlainText(value)
        logical_lines = value.splitlines() or [""]
        estimated_lines = sum(max(1, (len(line) // 62) + 1) for line in logical_lines)
        height = min(32, max(4, estimated_lines))
        widget.setFixedHeight(height * 18 + 12)

    def find_selected(self) -> Paper | None:
        return next((paper for paper in self.papers if paper.id == self.selected_id), None)

    def select_paper(self, paper_id: int):
        if paper_id == self.selected_id:
            return
        self.selected_id = paper_id
        for card_id, card in self.card_widgets.items():
            card.set_selected(card_id == paper_id)
        self.render_detail()

    def update_sidebar(self):
        labels = {"all": "全部论文", "reading": "正在阅读", "read": "已读", "later": "稍后阅读"}
        for key, button in self.status_buttons.items():
            count = len(self.papers) if key == "all" else sum(paper.status == key for paper in self.papers)
            active = key == self.status_filter and not self.tag_filter
            button.setText(f"{STATUS_ICON[key]}  {labels[key]}  ·  {count}")
            button.setChecked(active)
        tag_counts = Counter(tag for paper in self.papers for tag in paper.tags)
        tags = sorted(tag_counts, key=lambda tag: (-tag_counts[tag], tag.casefold()))
        visible_tags = tags[:8]
        if self.tag_filter and self.tag_filter not in visible_tags and self.tag_filter in tag_counts:
            visible_tags = (visible_tags[:7] if len(visible_tags) >= 8 else visible_tags) + [self.tag_filter]
        visible_keys = tuple(visible_tags)
        if visible_keys != self.visible_tag_keys:
            self._clear_layout(self.tag_list_layout)
            self.tag_buttons = {}
            if not visible_tags:
                empty = QLabel("暂无标签")
                empty.setObjectName("SidebarSection")
                self.tag_list_layout.addWidget(empty)
            for index, tag in enumerate(visible_tags):
                row = QWidget()
                row_layout = QHBoxLayout(row)
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(9)
                dot = QLabel("●")
                dot.setStyleSheet(f"color: {self.tag_color(tag, index)}; font-size: 9pt; background: transparent;")
                button = flat_button(None, "", lambda value=tag: self.set_tag_filter(value), object_name="TagButton")
                row_layout.addWidget(dot)
                row_layout.addWidget(button, 1)
                self.tag_list_layout.addWidget(row)
                self.tag_buttons[tag] = button
            self.visible_tag_keys = visible_keys
        for tag, button in self.tag_buttons.items():
            button.setText(f"{tag}  ·  {tag_counts[tag]}")
            color = "#ffffff" if tag == self.tag_filter else COLORS["sidebar_text"]
            button.setStyleSheet(
                f"QPushButton#TagButton {{ background-color: {COLORS['sidebar']}; color: {color}; "
                "border: none; text-align: left; padding: 4px 0px; }"
            )
        if len(tags) > len(visible_tags):
            self.tag_more_button.setText(f"查看全部标签  ·  {len(tags)}")
            self.tag_more_button.setVisible(True)
        else:
            self.tag_more_button.setVisible(False)
        self.count_label.setText(str(len(self.papers)))

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def tag_color(self, tag, index=0):
        palette = [COLORS["orange"], COLORS["purple"], COLORS["blue"], "#74bd91", "#d680a0", "#9b9b63"]
        return palette[(sum(ord(char) for char in tag) + index) % len(palette)]

    def tag_counts(self):
        return Counter(tag for paper in self.papers for tag in paper.tags)

    def show_all_tags(self):
        tags = sorted(self.tag_counts(), key=lambda tag: (-self.tag_counts()[tag], tag.casefold()))
        window = QDialog(self)
        window.setWindowTitle("全部标签")
        window.resize(360, 520)
        window.setMinimumSize(300, 360)
        layout = QVBoxLayout(window)
        layout.setContentsMargins(22, 22, 22, 20)
        layout.setSpacing(0)
        title = QLabel("全部标签")
        title.setStyleSheet(f"color: {COLORS['ink']}; font-size: 17pt; font-weight: bold; background: transparent;")
        layout.addWidget(title)
        subtitle = QLabel("按使用次数排序，选择标签查看对应论文")
        subtitle.setStyleSheet(f"color: {COLORS['muted']}; font-size: 9pt; background: transparent;")
        layout.addWidget(subtitle)
        layout.addSpacing(14)
        tag_scroll = ScrollableFrame(bg=COLORS["paper"])
        layout.addWidget(tag_scroll, 1)
        counts = self.tag_counts()
        for index, tag in enumerate(tags):
            button = flat_button(
                None,
                f"●  {tag}    ·    {counts[tag]} 篇论文",
                lambda value=tag, w=window: self.choose_tag_from_popup(w, value),
                object_name="TagPopupButton",
            )
            tag_scroll.add_widget(button)
        window.exec()

    def choose_tag_from_popup(self, window, tag):
        window.accept()
        self.set_tag_filter(tag)

    def persist(self):
        self.repository.save(self.papers)

    def new_paper(self):
        result = edit_paper(self, None, self.papers)
        if result:
            self.papers.insert(0, result)
            self.selected_id = result.id
            self.persist()
            self.render()

    def edit_paper(self):
        paper = self.find_selected()
        if not paper:
            return
        result = edit_paper(self, paper, self.papers)
        if result:
            self.papers = [result if item.id == paper.id else item for item in self.papers]
            self.selected_id = result.id
            self.persist()
            self.render()

    def delete_paper(self):
        paper = self.find_selected()
        if not paper:
            return
        answer = QMessageBox.question(self, "删除论文", f"确定删除《{paper.title}》吗？")
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.papers = [item for item in self.papers if item.id != paper.id]
        remaining = self.filtered_papers()
        self.selected_id = remaining[0].id if remaining else (self.papers[0].id if self.papers else None)
        self.persist()
        self.render()

    def duplicate_paper(self):
        paper = self.find_selected()
        if not paper:
            return
        copy = Paper.from_dict(paper.to_dict())
        copy.id = self.repository.next_id(self.papers)
        copy.title = f"{paper.title}（副本）"
        copy.status = "later"
        copy.updated = "刚刚更新"
        self.papers.insert(0, copy)
        self.selected_id = copy.id
        self.persist()
        self.render()


def run():
    app = QApplication(sys.argv)
    setup(app)
    window = PaperbaseApp()
    window.show()
    sys.exit(app.exec())
