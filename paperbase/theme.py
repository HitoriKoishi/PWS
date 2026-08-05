import tkinter as tk
from tkinter import ttk

from .config import COLORS, FONT


def setup(root: tk.Tk) -> None:
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("App.TFrame", background=COLORS["canvas"])
    style.configure("Panel.TFrame", background=COLORS["paper"])
    style.configure("Form.TEntry", padding=8, fieldbackground=COLORS["white"], foreground=COLORS["ink"])
    style.configure("Form.TCombobox", padding=7, fieldbackground=COLORS["white"])
    style.configure("Modern.Vertical.TScrollbar", troughcolor=COLORS["canvas"], background="#c9d7cd", bordercolor=COLORS["canvas"], arrowcolor=COLORS["muted"])
    style.configure("Modern.Horizontal.TProgressbar", troughcolor="#dce9df", background="#78b78a", bordercolor="#dce9df", lightcolor="#78b78a", darkcolor="#78b78a")
    root.option_add("*Font", (FONT, 10))


def flat_button(parent, text, command, *, bg=None, fg=None, active_bg=None, padx=12, pady=8, font=None):
    bg = bg or COLORS["paper"]
    fg = fg or COLORS["ink"]
    return tk.Button(parent, text=text, command=command, relief="flat", bd=0, bg=bg, fg=fg, activebackground=active_bg or bg, activeforeground=fg, padx=padx, pady=pady, font=font or (FONT, 9), cursor="hand2")
