from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from .config import COLORS, FIELD_STYLES, FONT, STATUS_TEXT
from .models import Paper
from .storage import PaperRepository
from .window_state import editor_geometry, editor_min_size, save_editor_geometry


class PaperEditor(tk.Toplevel):
    def __init__(self, parent, paper: Paper | None, next_id: int):
        super().__init__(parent)
        self.result: Paper | None = None
        self.paper = paper
        self.next_id = next_id
        self.form_can_scroll = False
        self._geometry_saved = False
        self.title("编辑论文" if paper else "新建论文")
        minimum_width, minimum_height = editor_min_size(parent)
        self.minsize(minimum_width, minimum_height)
        self.geometry(editor_geometry(parent))
        self.configure(bg=COLORS["paper"])
        self.transient(parent)
        self.grab_set()
        self._build()

    def destroy(self):
        if not self._geometry_saved and self.winfo_exists():
            save_editor_geometry(self)
            self._geometry_saved = True
        super().destroy()

    def _build(self):
        outer = tk.Frame(self, bg=COLORS["paper"], padx=30, pady=25)
        outer.pack(fill="both", expand=True)
        tk.Label(outer, text="编辑论文" if self.paper else "新建论文", bg=COLORS["paper"], fg=COLORS["ink"], font=(FONT, 20, "bold")).pack(anchor="w")
        tk.Label(outer, text="把一篇论文整理成可复用的研究资产", bg=COLORS["paper"], fg=COLORS["muted"], font=(FONT, 9)).pack(anchor="w", pady=(5, 18))
        content = tk.Frame(outer, bg=COLORS["paper"])
        content.pack(fill="both", expand=True)
        canvas = tk.Canvas(content, bg=COLORS["paper"], highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(content, orient="vertical", command=canvas.yview, style="Modern.Vertical.TScrollbar")
        self.form_scrollbar = scrollbar
        form = tk.Frame(canvas, bg=COLORS["paper"])
        window_id = canvas.create_window((0, 0), window=form, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        form.bind("<Configure>", lambda _event: self._sync_form_scroll(canvas, form, scrollbar))
        canvas.bind("<Configure>", lambda event: self._on_form_canvas_configure(event, canvas, window_id, form, scrollbar))
        self.fields: dict[str, tk.Entry | ttk.Combobox | tk.Text] = {}
        self.local_scroll_sections = []
        self._entry(form, "title", "论文名称 *", self.paper.title if self.paper else "")
        self._entry(form, "venue", "会议 / 期刊 *", self.paper.venue if self.paper else "")
        meta = tk.Frame(form, bg=COLORS["paper"])
        meta.pack(fill="x")
        year_box = tk.Frame(meta, bg=COLORS["paper"])
        year_box.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._entry(year_box, "year", "年份", str(self.paper.year if self.paper else date.today().year))
        status_box = tk.Frame(meta, bg=COLORS["paper"])
        status_box.pack(side="left", fill="x", expand=True, padx=(8, 0))
        tk.Label(status_box, text="阅读状态", bg=COLORS["paper"], fg="#53655c", font=(FONT, 9, "bold")).pack(anchor="w", pady=(10, 5))
        status = ttk.Combobox(status_box, values=list(STATUS_TEXT.values()), state="readonly", style="Form.TCombobox")
        status.set(STATUS_TEXT.get(self.paper.status, "正在阅读") if self.paper else "正在阅读")
        status.pack(fill="x")
        self.fields["status"] = status
        self._entry(form, "tags", "标签（用逗号分隔）", ", ".join(self.paper.tags) if self.paper else "")
        self._text(form, "summary", "≡  概要", self.paper.summary if self.paper else "", 4)
        self._text(form, "innovations", "✳  创新点（每行一个）", "\n".join(self.paper.innovations) if self.paper else "", 4)
        self._text(form, "notes", "▤  我的笔记", self.paper.notes if self.paper else "", 4)
        self._bind_widget_scroll(canvas, canvas)
        self._bind_form_scroll(form, canvas, self.local_scroll_sections)
        footer = tk.Frame(outer, bg=COLORS["paper"])
        footer.pack(fill="x", pady=(20, 0))
        tk.Button(footer, text="取消", command=self.destroy, relief="solid", bd=1, bg=COLORS["white"], fg=COLORS["muted"], padx=18, pady=8, font=(FONT, 9)).pack(side="right")
        tk.Button(footer, text="保存论文  ↗", command=self._save, relief="flat", bd=0, bg=COLORS["green"], fg="white", activebackground=COLORS["green_hover"], padx=18, pady=9, font=(FONT, 9, "bold")).pack(side="right", padx=(0, 9))

    def _on_form_canvas_configure(self, event, canvas, window_id, form, scrollbar):
        canvas.itemconfigure(window_id, width=event.width)
        self.after_idle(lambda: self._sync_form_scroll(canvas, form, scrollbar))

    def _sync_form_scroll(self, canvas, form, scrollbar):
        if not self.winfo_exists():
            return
        canvas.configure(scrollregion=canvas.bbox("all"))
        bbox = canvas.bbox("all")
        content_height = (bbox[3] - bbox[1]) if bbox else 0
        self.form_can_scroll = content_height > canvas.winfo_height() + 1
        if self.form_can_scroll:
            scrollbar.state(["!disabled"])
        else:
            scrollbar.state(["disabled"])
            canvas.yview_moveto(0)

    def _scroll_amount(self, event):
        if event.num == 4:
            return -3
        if event.num == 5:
            return 3
        return -1 * int(event.delta / 120)

    def _bind_widget_scroll(self, widget, canvas):
        def scroll(event):
            if self.form_can_scroll:
                canvas.yview_scroll(self._scroll_amount(event), "units")
            return "break"

        widget.bind("<MouseWheel>", scroll, add="+")
        widget.bind("<Button-4>", scroll, add="+")
        widget.bind("<Button-5>", scroll, add="+")

    def _bind_form_scroll(self, widget, canvas, excluded):
        if any(widget == section for section in excluded):
            return

        def scroll(event):
            if self.form_can_scroll:
                canvas.yview_scroll(self._scroll_amount(event), "units")
            return "break"

        widget.bind("<MouseWheel>", scroll, add="+")
        widget.bind("<Button-4>", scroll, add="+")
        widget.bind("<Button-5>", scroll, add="+")
        for child in widget.winfo_children():
            self._bind_form_scroll(child, canvas, excluded)

    def _entry(self, parent, key, label, value):
        tk.Label(parent, text=label, bg=COLORS["paper"], fg="#53655c", font=(FONT, 9, "bold")).pack(anchor="w", pady=(10, 5))
        entry = ttk.Entry(parent, style="Form.TEntry")
        entry.insert(0, value)
        entry.pack(fill="x")
        self.fields[key] = entry

    def _text(self, parent, key, label, value, height):
        style = FIELD_STYLES[key]
        section = tk.Frame(parent, bg=style["bg"], highlightbackground=style["border"], highlightthickness=1, padx=12, pady=10)
        section.pack(fill="x", pady=(12, 0))
        tk.Label(section, text=label, bg=style["bg"], fg=style["heading"], font=(FONT, 9, "bold"), anchor="w").pack(fill="x", pady=(0, 7))
        text_area = tk.Frame(section, bg=style["bg"])
        text_area.pack(fill="both", expand=True)
        text = tk.Text(text_area, height=height, wrap="word", relief="flat", bd=0, highlightthickness=0, bg=style["bg"], fg=style["text"], insertbackground=style["heading"], font=(FONT, 10), padx=0, pady=2)
        text_scrollbar = ttk.Scrollbar(text_area, orient="vertical", command=text.yview, style="Modern.Vertical.TScrollbar")
        text.configure(yscrollcommand=text_scrollbar.set)
        text.insert("1.0", value)
        text.pack(side="left", fill="both", expand=True)
        text_scrollbar.pack(side="right", fill="y", padx=(8, 0))
        self._bind_text_scroll(section, text)
        self.local_scroll_sections.append(section)
        self.fields[key] = text

    def _bind_text_scroll(self, section, text):
        def scroll(event):
            if event.num == 4:
                amount = -3
            elif event.num == 5:
                amount = 3
            else:
                amount = -1 * int(event.delta / 120)
            text.yview_scroll(amount, "units")
            return "break"

        self._bind_text_scroll_widget(section, scroll)

    def _bind_text_scroll_widget(self, widget, callback):
        widget.bind("<MouseWheel>", callback, add="+")
        widget.bind("<Button-4>", callback, add="+")
        widget.bind("<Button-5>", callback, add="+")
        for child in widget.winfo_children():
            self._bind_text_scroll_widget(child, callback)

    def _save(self):
        title = self.fields["title"].get().strip()
        venue = self.fields["venue"].get().strip()
        if not title or not venue:
            messagebox.showwarning("信息不完整", "请填写论文名称和会议 / 期刊。", parent=self)
            return
        try:
            year = int(self.fields["year"].get() or date.today().year)
        except ValueError:
            messagebox.showwarning("年份格式错误", "年份必须是数字。", parent=self)
            return
        status = next(key for key, value in STATUS_TEXT.items() if value == self.fields["status"].get())
        tags = [item.strip() for item in self.fields["tags"].get().replace("，", ",").split(",") if item.strip()]
        summary = self.fields["summary"].get("1.0", "end").strip()
        innovations = [item.strip() for item in self.fields["innovations"].get("1.0", "end").splitlines() if item.strip()]
        notes = self.fields["notes"].get("1.0", "end").strip()
        self.result = Paper(self.paper.id if self.paper else self.next_id, title, venue, year, status, tags, summary, innovations, notes, "刚刚更新", date.today().isoformat())
        self.destroy()


def edit_paper(parent, paper: Paper | None, papers: list[Paper]) -> Paper | None:
    dialog = PaperEditor(parent, paper, PaperRepository.next_id(papers))
    parent.wait_window(dialog)
    return dialog.result
