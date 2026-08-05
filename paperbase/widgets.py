from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from .config import COLORS, FONT, MONO, STATUS_COLOR, STATUS_ICON, STATUS_TEXT
from .models import Paper


class ScrollableFrame(tk.Frame):
    def __init__(self, parent, *, bg=None):
        super().__init__(parent, bg=bg or COLORS["canvas"])
        self.canvas = tk.Canvas(self, bg=bg or COLORS["canvas"], highlightthickness=0, bd=0)
        self.body = tk.Frame(self.canvas, bg=bg or COLORS["canvas"])
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview, style="Modern.Vertical.TScrollbar")
        self.can_scroll = False
        self.window_id = self.canvas.create_window((0, 0), window=self.body, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.body.bind("<Configure>", self._on_body_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.bind_scroll_tree(self.canvas)
        self.bind_scroll_tree(self.body)

    def _on_mousewheel(self, event):
        if not self.winfo_exists() or not self.can_scroll:
            return
        if event.num == 4:
            amount = -3
        elif event.num == 5:
            amount = 3
        else:
            amount = -1 * int(event.delta / 120)
        self.canvas.yview_scroll(amount, "units")

    def _on_body_configure(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.after_idle(self._sync_scroll_state)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.window_id, width=event.width)
        self.after_idle(self._sync_scroll_state)

    def _sync_scroll_state(self):
        if not self.winfo_exists():
            return
        bbox = self.canvas.bbox("all")
        content_height = (bbox[3] - bbox[1]) if bbox else 0
        self.can_scroll = content_height > self.canvas.winfo_height() + 1
        if self.can_scroll:
            self.scrollbar.state(["!disabled"])
        else:
            self.scrollbar.state(["disabled"])
            self.canvas.yview_moveto(0)

    def bind_scroll_tree(self, widget):
        """只给当前滚动容器的控件树绑定滚轮，避免多个容器同时滚动。"""
        widget.bind("<MouseWheel>", self._on_mousewheel, add="+")
        widget.bind("<Button-4>", self._on_mousewheel, add="+")
        widget.bind("<Button-5>", self._on_mousewheel, add="+")
        for child in widget.winfo_children():
            self.bind_scroll_tree(child)

    def clear(self):
        for child in self.body.winfo_children():
            child.destroy()
        self.can_scroll = False
        self.after_idle(self._sync_scroll_state)


class PaperCard(tk.Frame):
    def __init__(self, parent, paper: Paper, selected: bool, on_select: Callable[[int], None]):
        super().__init__(parent, bg=COLORS["line"], padx=1, pady=1, cursor="hand2")
        self.paper = paper
        self.on_select = on_select
        self.inner = tk.Frame(self, bg=COLORS["paper"], padx=15, pady=13)
        self.inner.pack(fill="both", expand=True)
        top = tk.Frame(self.inner, bg=COLORS["paper"])
        top.pack(fill="x")
        tk.Label(top, text=f"{STATUS_ICON.get(paper.status, '●')}  {STATUS_TEXT.get(paper.status, '未分类')}", bg=COLORS["paper"], fg=STATUS_COLOR.get(paper.status, COLORS["muted"]), font=(FONT, 9, "bold")).pack(side="left")
        tk.Label(top, text=str(paper.year), bg=COLORS["paper"], fg=COLORS["subtle"], font=(MONO, 8)).pack(side="right")
        title = paper.title if len(paper.title) <= 78 else paper.title[:78] + "…"
        tk.Label(self.inner, text=title, bg=COLORS["paper"], fg=COLORS["ink"], justify="left", anchor="w", wraplength=420, font=(FONT, 10, "bold")).pack(fill="x", pady=(9, 4))
        summary = f"{paper.venue}  ·  {paper.summary}" if paper.summary else paper.venue
        tk.Label(self.inner, text=summary, bg=COLORS["paper"], fg=COLORS["muted"], justify="left", anchor="w", wraplength=420, font=(FONT, 8)).pack(fill="x")
        tags = tk.Frame(self.inner, bg=COLORS["paper"])
        tags.pack(fill="x", pady=(10, 0))
        self.tag_labels = []
        for tag in paper.tags[:3]:
            label = tk.Label(tags, text=tag, bg="#edf3ed", fg="#6d8278", font=(FONT, 8), padx=6, pady=3)
            label.pack(side="left", padx=(0, 5))
            self.tag_labels.append(label)
        self.set_selected(selected)
        self._bind_recursive(self, self._click)

    def set_selected(self, selected: bool):
        border = COLORS["green_text"] if selected else COLORS["line"]
        surface = COLORS["white"] if selected else COLORS["paper"]
        self.configure(bg=border)
        self._set_surface_color(self.inner, surface)

    def _set_surface_color(self, widget, color):
        if widget not in self.tag_labels:
            try:
                widget.configure(bg=color)
            except tk.TclError:
                pass
        for child in widget.winfo_children():
            self._set_surface_color(child, color)

    def _bind_recursive(self, widget, callback):
        widget.bind("<Button-1>", callback)
        for child in widget.winfo_children():
            self._bind_recursive(child, callback)

    def _click(self, _event):
        self.on_select(self.paper.id)
