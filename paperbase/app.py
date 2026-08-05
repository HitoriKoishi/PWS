from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from .config import COLORS, DATA_FILE, FONT, MONO, STATUS_COLOR, STATUS_ICON, STATUS_TEXT
from .dialogs import edit_paper
from .models import Paper
from .storage import PaperRepository
from .theme import flat_button, setup
from .widgets import PaperCard, ScrollableFrame


class PaperbaseApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Paperbase · 个人论文工作站")
        self.root.geometry("1420x900")
        self.root.minsize(1080, 700)
        self.root.configure(bg=COLORS["canvas"])
        setup(root)
        self.repository = PaperRepository(DATA_FILE)
        self.papers = self.repository.load()
        self.selected_id = self.papers[0].id if self.papers else None
        self.status_filter = "all"
        self.tag_filter: str | None = None
        self.sort_newest = True
        self.filtered: list[Paper] = []
        self.status_buttons: dict[str, tk.Button] = {}
        self.tag_buttons: dict[str, tk.Button] = {}
        self._build()
        self.render()

    def _build(self):
        sidebar = tk.Frame(self.root, bg=COLORS["sidebar"], width=245)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        self._build_sidebar(sidebar)

        main = tk.Frame(self.root, bg=COLORS["canvas"])
        main.pack(side="left", fill="both", expand=True)
        self._build_topbar(main)
        self._build_workspace(main)

    def _build_sidebar(self, sidebar):
        brand = tk.Frame(sidebar, bg=COLORS["sidebar"])
        brand.pack(fill="x", padx=24, pady=(30, 46))
        mark = tk.Frame(brand, bg=COLORS["sidebar"], width=24, height=25)
        mark.pack(side="left", padx=(0, 10))
        mark.pack_propagate(False)
        for height, color in [(14, "#98d6b1"), (23, "#e0ad67"), (18, "#98d6b1")]:
            tk.Frame(mark, bg=color, width=5, height=height).pack(side="left", anchor="s", padx=1)
        tk.Label(brand, text="paperbase", bg=COLORS["sidebar"], fg="white", font=(FONT, 18, "bold")).pack(anchor="w")
        tk.Label(brand, text="PERSONAL RESEARCH OS", bg=COLORS["sidebar"], fg=COLORS["sidebar_muted"], font=(MONO, 7)).pack(anchor="w", padx=(34, 0), pady=(2, 0))

        tk.Label(sidebar, text="工作区", bg=COLORS["sidebar"], fg=COLORS["sidebar_muted"], font=(MONO, 9), anchor="w").pack(fill="x", padx=24, pady=(0, 9))
        for key, label in [("all", "全部论文"), ("reading", "正在阅读"), ("read", "已读"), ("later", "稍后阅读")]:
            button = tk.Button(sidebar, text=label, anchor="w", relief="flat", bd=0, padx=13, pady=9, bg=COLORS["sidebar"], fg=COLORS["sidebar_text"], activebackground=COLORS["sidebar_hover"], activeforeground="white", font=(FONT, 10), cursor="hand2", command=lambda value=key: self.set_status_filter(value))
            button.pack(fill="x", padx=13, pady=2)
            self.status_buttons[key] = button

        tk.Frame(sidebar, height=1, bg="#2b514b").pack(fill="x", padx=24, pady=(32, 26))
        tk.Label(sidebar, text="标签", bg=COLORS["sidebar"], fg=COLORS["sidebar_muted"], font=(MONO, 9), anchor="w").pack(fill="x", padx=24, pady=(0, 9))
        for tag, color in [("LLM", COLORS["orange"]), ("Agent", COLORS["purple"]), ("RAG", COLORS["blue"]), ("Evaluation", "#74bd91")]:
            row = tk.Frame(sidebar, bg=COLORS["sidebar"])
            row.pack(fill="x", padx=24, pady=2)
            tk.Label(row, text="●", fg=color, bg=COLORS["sidebar"], font=(FONT, 9)).pack(side="left", padx=(0, 9))
            button = tk.Button(row, text=tag, anchor="w", relief="flat", bd=0, bg=COLORS["sidebar"], fg=COLORS["sidebar_text"], activebackground=COLORS["sidebar"], activeforeground="white", font=(FONT, 10), cursor="hand2", command=lambda value=tag: self.set_tag_filter(value))
            button.pack(side="left", fill="x", expand=True)
            self.tag_buttons[tag] = button

        footer = tk.Frame(sidebar, bg=COLORS["sidebar"])
        footer.pack(side="bottom", fill="x", padx=20, pady=20)
        tk.Label(footer, text="本地存储  ·  自动保存", bg="#20483f", fg="#d8e8df", font=(FONT, 9), anchor="w", padx=12, pady=10).pack(fill="x")
        tk.Label(footer, text="数据只保存在当前电脑", bg="#20483f", fg="#86a9a0", font=(FONT, 8), anchor="w", padx=12).pack(fill="x", pady=(0, 10))

    def _build_topbar(self, parent):
        bar = tk.Frame(parent, height=76, bg=COLORS["paper"])
        bar.pack(fill="x")
        bar.pack_propagate(False)
        breadcrumb = tk.Frame(bar, bg=COLORS["paper"])
        breadcrumb.pack(side="left", padx=30)
        tk.Label(breadcrumb, text="我的研究库  /  ", bg=COLORS["paper"], fg=COLORS["subtle"], font=(FONT, 10)).pack(side="left")
        self.view_title = tk.Label(breadcrumb, text="全部论文", bg=COLORS["paper"], fg="#485753", font=(FONT, 10, "bold"))
        self.view_title.pack(side="left")
        actions = tk.Frame(bar, bg=COLORS["paper"])
        actions.pack(side="right", padx=27)
        tk.Label(actions, text="⌘ K", bg=COLORS["paper"], fg=COLORS["subtle"], font=(MONO, 8)).pack(side="left", padx=(0, 18))
        flat_button(actions, "＋  新建论文", self.new_paper, bg=COLORS["green"], fg="white", active_bg=COLORS["green_hover"], padx=15, pady=9, font=(FONT, 10, "bold")).pack(side="left")

    def _build_workspace(self, parent):
        body = tk.Frame(parent, bg=COLORS["canvas"])
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, minsize=430, weight=0)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)
        self._build_library(body).grid(row=0, column=0, sticky="nsew", padx=(27, 13), pady=(25, 27))
        self._build_detail(body).grid(row=0, column=1, sticky="nsew", padx=(13, 27), pady=(25, 27))

    def _build_library(self, parent):
        panel = tk.Frame(parent, bg=COLORS["canvas"])
        heading = tk.Frame(panel, bg=COLORS["canvas"])
        heading.pack(fill="x", pady=(0, 18))
        tk.Label(heading, text="COLLECTION / 2026", bg=COLORS["canvas"], fg=COLORS["subtle"], font=(MONO, 8)).pack(anchor="w")
        title_line = tk.Frame(heading, bg=COLORS["canvas"])
        title_line.pack(fill="x", pady=(5, 0))
        tk.Label(title_line, text="论文库", bg=COLORS["canvas"], fg=COLORS["ink"], font=(FONT, 25, "bold")).pack(side="left")
        self.count_label = tk.Label(title_line, text="0", bg="#e5eee6", fg="#819189", font=(MONO, 9), padx=7, pady=3)
        self.count_label.pack(side="left", padx=9, pady=4)
        toolbar = tk.Frame(panel, bg=COLORS["canvas"])
        toolbar.pack(fill="x", pady=(0, 14))
        search_wrap = tk.Frame(toolbar, bg=COLORS["white"], highlightbackground=COLORS["line"], highlightthickness=1)
        search_wrap.pack(side="left", fill="x", expand=True)
        tk.Label(search_wrap, text="⌕", bg=COLORS["white"], fg=COLORS["subtle"], font=(FONT, 19)).pack(side="left", padx=(9, 3))
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_wrap, textvariable=self.search_var, relief="flat", bd=0, bg=COLORS["white"], fg=COLORS["ink"], insertbackground=COLORS["ink"], font=(FONT, 9))
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        self.search_var.trace_add("write", lambda *_args: self.render_list())
        flat_button(toolbar, "最近更新  ↕", self.toggle_sort, bg=COLORS["white"], fg=COLORS["muted"], padx=10, pady=9).pack(side="left", padx=(8, 0))
        self.list_surface = tk.Frame(panel, bg=COLORS["canvas"])
        self.list_surface.pack(fill="both", expand=True)
        self.card_list = ScrollableFrame(self.list_surface, bg=COLORS["canvas"])
        self.card_list.pack(fill="both", expand=True)
        self.empty_label = tk.Label(self.list_surface, text="没有找到论文\n尝试调整搜索词或新建一篇论文", bg=COLORS["canvas"], fg=COLORS["muted"], font=(FONT, 10), justify="center")
        return panel

    def _build_detail(self, parent):
        panel = tk.Frame(parent, bg=COLORS["paper"], padx=31, pady=28, highlightbackground=COLORS["line"], highlightthickness=1)
        header = tk.Frame(panel, bg=COLORS["paper"])
        header.pack(fill="x")
        title_area = tk.Frame(header, bg=COLORS["paper"])
        title_area.pack(side="left", fill="x", expand=True)
        self.status_pill = tk.Label(title_area, text="", bg=COLORS["green_light"], fg=COLORS["green_text"], font=(FONT, 9, "bold"), padx=9, pady=5)
        self.status_pill.pack(anchor="w")
        self.detail_title = tk.Label(title_area, text="", bg=COLORS["paper"], fg=COLORS["ink"], font=(FONT, 20, "bold"), justify="left", anchor="w", wraplength=720)
        self.detail_title.pack(fill="x", pady=(14, 6))
        self.detail_venue = tk.Label(title_area, text="", bg=COLORS["paper"], fg=COLORS["muted"], font=(FONT, 10), anchor="w")
        self.detail_venue.pack(anchor="w")
        action_area = tk.Frame(header, bg=COLORS["paper"])
        action_area.pack(side="right", anchor="n", padx=(15, 0), pady=1)
        flat_button(action_area, "编辑", self.edit_paper, bg=COLORS["white"], fg=COLORS["green_text"], padx=12, pady=6).pack(side="left")
        flat_button(action_area, "删除", self.delete_paper, bg=COLORS["white"], fg=COLORS["danger"], padx=10, pady=6).pack(side="left", padx=(7, 0))
        self.tag_line = tk.Label(panel, text="", bg=COLORS["paper"], fg=COLORS["muted"], font=(FONT, 9), anchor="w")
        self.tag_line.pack(fill="x", pady=(19, 19))
        insight = tk.Frame(panel, bg="#f2f7ef", highlightbackground="#dfe9df", highlightthickness=1)
        insight.pack(fill="x", pady=(0, 28))
        self.progress_text = tk.Label(insight, text="", bg="#f2f7ef", fg="#456b59", font=(FONT, 9), anchor="w", padx=12, pady=12)
        self.progress_text.pack(side="left")
        self.progress_bar = ttk.Progressbar(insight, style="Modern.Horizontal.TProgressbar", mode="determinate", length=180)
        self.progress_bar.pack(side="right", padx=14)
        self.summary_text = self._section(panel, "≡", "概要")
        self.innovation_text = self._section(panel, "✳", "创新点")
        notes = tk.Frame(panel, bg=COLORS["yellow_light"], padx=15, pady=13)
        notes.pack(fill="x", pady=(0, 18))
        tk.Label(notes, text="▤  我的笔记", bg=COLORS["yellow_light"], fg="#8d7443", font=(FONT, 10, "bold"), anchor="w").pack(fill="x", pady=(0, 8))
        self.notes_text = self._readonly_text(notes, height=4, bg=COLORS["yellow_light"])
        self.notes_text.pack(fill="x")
        footer = tk.Frame(panel, bg=COLORS["paper"])
        footer.pack(fill="x")
        self.date_label = tk.Label(footer, text="", bg=COLORS["paper"], fg=COLORS["subtle"], font=(MONO, 8), anchor="w")
        self.date_label.pack(side="left")
        flat_button(footer, "复制这篇论文  ↗", self.duplicate_paper, bg=COLORS["paper"], fg=COLORS["green_text"], padx=5, pady=2).pack(side="right")
        return panel

    def _section(self, parent, symbol, title):
        section = tk.Frame(parent, bg=COLORS["paper"])
        section.pack(fill="x", pady=(0, 23))
        tk.Label(section, text=f"{symbol}  {title}", bg=COLORS["paper"], fg=COLORS["ink"], font=(FONT, 10, "bold"), anchor="w").pack(fill="x", pady=(0, 8))
        text = self._readonly_text(section, height=4)
        text.pack(fill="x")
        return text

    def _readonly_text(self, parent, height, bg=None):
        return tk.Text(parent, height=height, wrap="word", relief="flat", bd=0, highlightthickness=0, bg=bg or COLORS["paper"], fg="#65776e", font=(FONT, 10), padx=0, pady=0, spacing1=3, state="disabled")

    def set_status_filter(self, value):
        self.status_filter, self.tag_filter = value, None
        self.view_title.configure(text={"all": "全部论文", "reading": "正在阅读", "read": "已读", "later": "稍后阅读"}[value])
        self.render()

    def set_tag_filter(self, value):
        self.status_filter, self.tag_filter = "all", value
        self.view_title.configure(text=value)
        self.render()

    def toggle_sort(self):
        self.sort_newest = not self.sort_newest
        self.render_list()

    def filtered_papers(self):
        query = self.search_var.get().strip().lower()
        papers = [paper for paper in self.papers if self.status_filter == "all" or paper.status == self.status_filter]
        if self.tag_filter:
            papers = [paper for paper in papers if self.tag_filter.lower() in [tag.lower() for tag in paper.tags]]
        if query:
            papers = [paper for paper in papers if query in paper.search_text()]
        return sorted(papers, key=lambda paper: paper.id, reverse=self.sort_newest)

    def render(self):
        self.render_list()
        self.render_detail()
        self.update_sidebar()

    def render_list(self):
        self.filtered = self.filtered_papers()
        self.card_list.clear()
        if not self.filtered:
            self.empty_label.place(relx=0.5, rely=0.45, anchor="center")
        else:
            self.empty_label.place_forget()
            for paper in self.filtered:
                card = PaperCard(self.card_list.body, paper, paper.id == self.selected_id, self.select_paper)
                card.pack(fill="x", pady=(0, 9))

    def render_detail(self):
        paper = self.find_selected()
        if not paper:
            self.status_pill.configure(text="选择一篇论文")
            self.detail_title.configure(text="从左侧列表选择论文")
            self.detail_venue.configure(text="开始整理你的研究思路")
            self.tag_line.configure(text="")
            self._set_text(self.summary_text, "还没有选择论文。")
            self._set_text(self.innovation_text, "")
            self._set_text(self.notes_text, "")
            return
        self.status_pill.configure(text=STATUS_TEXT.get(paper.status, "未分类"))
        self.detail_title.configure(text=paper.title)
        self.detail_venue.configure(text=f"{paper.venue}  ·  {paper.year}")
        self.tag_line.configure(text="   ".join(f"#{tag}" for tag in paper.tags) or "暂无标签")
        self._set_text(self.summary_text, paper.summary or "还没有添加概要。")
        self._set_text(self.innovation_text, "\n".join(f"•  {item}" for item in paper.innovations) or "还没有添加创新点。")
        self._set_text(self.notes_text, paper.notes or "还没有添加笔记。")
        self.date_label.configure(text=f"最后编辑于 {paper.date}  ·  {paper.updated}")
        progress = 100 if paper.status == "read" else 57 if paper.status == "reading" else 0
        self.progress_bar.configure(value=progress)
        self.progress_text.configure(text="✓  已完成阅读" if progress == 100 else "↗  正在形成初步理解" if progress else "◷  加入阅读队列")

    def _set_text(self, widget, value):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", value)
        widget.configure(state="disabled")

    def find_selected(self) -> Paper | None:
        return next((paper for paper in self.papers if paper.id == self.selected_id), None)

    def select_paper(self, paper_id: int):
        self.selected_id = paper_id
        self.render_list()
        self.render_detail()

    def update_sidebar(self):
        labels = {"all": "全部论文", "reading": "正在阅读", "read": "已读", "later": "稍后阅读"}
        for key, button in self.status_buttons.items():
            count = len(self.papers) if key == "all" else sum(paper.status == key for paper in self.papers)
            active = key == self.status_filter and not self.tag_filter
            button.configure(text=f"{STATUS_ICON[key]}  {labels[key]}  ·  {count}", bg=COLORS["sidebar_hover"] if active else COLORS["sidebar"], fg="white" if active else COLORS["sidebar_text"])
        for tag, button in self.tag_buttons.items():
            button.configure(fg="white" if tag == self.tag_filter else COLORS["sidebar_text"])
        self.count_label.configure(text=str(len(self.papers)))

    def persist(self):
        self.repository.save(self.papers)

    def new_paper(self):
        result = edit_paper(self.root, None, self.papers)
        if result:
            self.papers.insert(0, result)
            self.selected_id = result.id
            self.persist()
            self.render()

    def edit_paper(self):
        paper = self.find_selected()
        if not paper:
            return
        result = edit_paper(self.root, paper, self.papers)
        if result:
            index = self.papers.index(paper)
            self.papers[index] = result
            self.selected_id = result.id
            self.persist()
            self.render()

    def delete_paper(self):
        paper = self.find_selected()
        if not paper or not messagebox.askyesno("删除论文", f"确定删除《{paper.title}》吗？", parent=self.root):
            return
        self.papers.remove(paper)
        self.selected_id = self.papers[0].id if self.papers else None
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
    root = tk.Tk()
    PaperbaseApp(root)
    root.mainloop()
