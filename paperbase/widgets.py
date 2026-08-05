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
        self.window_id = self.canvas.create_window((0, 0), window=self.body, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.body.bind("<Configure>", lambda _event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda event: self.canvas.itemconfigure(self.window_id, width=event.width))
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel, add="+")

    def _on_mousewheel(self, event):
        if self.winfo_exists():
            self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    def clear(self):
        for child in self.body.winfo_children():
            child.destroy()


class PaperCard(tk.Frame):
    def __init__(self, parent, paper: Paper, selected: bool, on_select: Callable[[int], None]):
        border = COLORS["green_text"] if selected else COLORS["line"]
        super().__init__(parent, bg=border, padx=1, pady=1, cursor="hand2")
        self.paper = paper
        self.on_select = on_select
        inner_bg = COLORS["white"] if selected else COLORS["paper"]
        inner = tk.Frame(self, bg=inner_bg, padx=15, pady=13)
        inner.pack(fill="both", expand=True)
        top = tk.Frame(inner, bg=inner_bg)
        top.pack(fill="x")
        tk.Label(top, text=f"{STATUS_ICON.get(paper.status, '●')}  {STATUS_TEXT.get(paper.status, '未分类')}", bg=inner_bg, fg=STATUS_COLOR.get(paper.status, COLORS["muted"]), font=(FONT, 9, "bold")).pack(side="left")
        tk.Label(top, text=str(paper.year), bg=inner_bg, fg=COLORS["subtle"], font=(MONO, 8)).pack(side="right")
        title = paper.title if len(paper.title) <= 78 else paper.title[:78] + "…"
        tk.Label(inner, text=title, bg=inner_bg, fg=COLORS["ink"], justify="left", anchor="w", wraplength=420, font=(FONT, 10, "bold")).pack(fill="x", pady=(9, 4))
        summary = f"{paper.venue}  ·  {paper.summary}" if paper.summary else paper.venue
        tk.Label(inner, text=summary, bg=inner_bg, fg=COLORS["muted"], justify="left", anchor="w", wraplength=420, font=(FONT, 8)).pack(fill="x")
        tags = tk.Frame(inner, bg=inner_bg)
        tags.pack(fill="x", pady=(10, 0))
        for tag in paper.tags[:3]:
            tk.Label(tags, text=tag, bg="#edf3ed", fg="#6d8278", font=(FONT, 8), padx=6, pady=3).pack(side="left", padx=(0, 5))
        self._bind_recursive(self, self._click)

    def _bind_recursive(self, widget, callback):
        widget.bind("<Button-1>", callback)
        for child in widget.winfo_children():
            self._bind_recursive(child, callback)

    def _click(self, _event):
        self.on_select(self.paper.id)
