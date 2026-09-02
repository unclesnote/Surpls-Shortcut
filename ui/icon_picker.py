from __future__ import annotations

import math
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Callable

from i18n import Translator
from services.icon_service import (
    ICON_EXTENSIONS,
    find_nearby_icons,
    list_system_icons,
    resolve_system_icon,
)


def load_icon_preview(
    master: tk.Misc,
    icon: str,
    size: int = 64,
) -> tk.PhotoImage | None:
    """Load a file or theme icon as a Tk image, with a stdlib fallback."""
    path = Path(icon).expanduser()
    if not path.is_file():
        resolved = resolve_system_icon(icon)
        if resolved is None:
            return None
        path = resolved

    try:
        from PIL import Image, ImageTk

        with Image.open(path) as source:
            image = source.convert("RGBA")
            image.thumbnail((size, size))
            return ImageTk.PhotoImage(image, master=master)
    except (ImportError, OSError, ValueError):
        pass

    try:
        image = tk.PhotoImage(master=master, file=str(path))
    except tk.TclError:
        return None

    largest_side = max(image.width(), image.height())
    if largest_side > size:
        factor = math.ceil(largest_side / size)
        image = image.subsample(factor, factor)
    elif 0 < largest_side < size // 2:
        factor = min(max(size // largest_side, 1), 4)
        image = image.zoom(factor, factor)
    return image


class _ScrollableIconGrid(ttk.Frame):
    """A scrollable grid that keeps each icon preview with its label."""

    def __init__(
        self,
        parent: tk.Misc,
        on_select: Callable[[str], None],
        columns: int = 4,
    ) -> None:
        super().__init__(parent)
        self.on_select = on_select
        self.columns = columns
        self.images: list[tk.PhotoImage] = []

        self.canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.content = ttk.Frame(self.canvas, padding=4)
        self.window_id = self.canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="nw",
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.content.bind("<Configure>", self._update_scroll_region)
        self.canvas.bind("<Configure>", self._resize_content)

    def _update_scroll_region(self, _event: tk.Event) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_content(self, event: tk.Event) -> None:
        self.canvas.itemconfigure(self.window_id, width=event.width)

    def set_items(self, items: list[tuple[str, str]]) -> None:
        for child in self.content.winfo_children():
            child.destroy()
        self.images.clear()

        for column in range(self.columns):
            self.content.columnconfigure(column, weight=1, uniform="icon")

        for index, (value, label) in enumerate(items):
            image = load_icon_preview(self, value, 56)
            if image is not None:
                self.images.append(image)
            button = ttk.Button(
                self.content,
                text=label,
                image=image or "",
                compound="top",
                command=lambda selected=value: self.on_select(selected),
                width=18,
            )
            button.grid(
                row=index // self.columns,
                column=index % self.columns,
                sticky="nsew",
                padx=4,
                pady=4,
            )
        self.canvas.yview_moveto(0)


class IconPickerDialog(tk.Toplevel):
    def __init__(
        self,
        parent: tk.Misc,
        tr: Translator,
        executable: Path,
        current: str,
    ) -> None:
        super().__init__(parent)
        self.tr = tr
        self.executable = executable
        self.result: str | None = None
        self.nearby_results: list[Path] = []
        self.preview_image: tk.PhotoImage | None = None
        self._icon_results: queue.Queue[list[Path]] = queue.Queue(maxsize=1)

        self.title(tr("icon_title"))
        self.geometry("780x620")
        self.minsize(640, 500)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(12, 6))
        self.nearby_frame = ttk.Frame(self.notebook, padding=8)
        self.system_frame = ttk.Frame(self.notebook, padding=8)
        self.custom_frame = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(self.nearby_frame, text=tr("nearby"))
        self.notebook.add(self.system_frame, text=tr("system_icons"))
        self.notebook.add(self.custom_frame, text=tr("custom_file"))

        self._build_nearby_tab()
        self._build_system_tab()
        self._build_custom_tab(current)
        self._build_selection_panel()

        self.bind("<Escape>", lambda _event: self.destroy())
        self.grab_set()
        if current:
            self._select_icon(current)
        threading.Thread(target=self._search_nearby, daemon=True).start()
        self.after(100, self._poll_nearby)

    def _build_nearby_tab(self) -> None:
        header = ttk.Frame(self.nearby_frame)
        header.pack(fill="x", pady=(0, 6))
        self.nearby_status = ttk.Label(header, text=self.tr("searching"))
        self.nearby_status.pack(side="left")
        self.nearby_query = tk.StringVar()
        ttk.Label(header, text=self.tr("search")).pack(side="right")
        ttk.Entry(header, textvariable=self.nearby_query, width=24).pack(
            side="right", padx=(6, 8)
        )
        self.nearby_query.trace_add("write", lambda *_: self._fill_nearby_icons())
        self.nearby_grid = _ScrollableIconGrid(
            self.nearby_frame,
            self._select_icon,
        )
        self.nearby_grid.pack(fill="both", expand=True)

    def _build_system_tab(self) -> None:
        header = ttk.Frame(self.system_frame)
        header.pack(fill="x", pady=(0, 6))
        self.system_search = tk.StringVar()
        ttk.Label(header, text=self.tr("search")).pack(side="left")
        ttk.Entry(header, textvariable=self.system_search).pack(
            side="left", fill="x", expand=True, padx=(6, 0)
        )
        self.system_grid = _ScrollableIconGrid(
            self.system_frame,
            self._select_icon,
        )
        self.system_grid.pack(fill="both", expand=True)
        self.system_search.trace_add("write", lambda *_: self._fill_system_icons())
        self._fill_system_icons()

    def _build_custom_tab(self, current: str) -> None:
        self.custom_var = tk.StringVar(
            value=current if Path(current).is_absolute() else ""
        )
        custom_row = ttk.Frame(self.custom_frame)
        custom_row.pack(fill="x", pady=12)
        ttk.Entry(
            custom_row,
            textvariable=self.custom_var,
            state="readonly",
        ).pack(side="left", fill="x", expand=True)
        ttk.Button(
            custom_row,
            text=self.tr("choose_file"),
            command=self._browse_custom,
        ).pack(side="left", padx=(8, 0))

    def _build_selection_panel(self) -> None:
        selection = ttk.LabelFrame(self, text=self.tr("selected"), padding=8)
        selection.pack(fill="x", padx=12, pady=6)
        self.preview_label = ttk.Label(
            selection,
            text=self.tr("no_preview"),
            anchor="center",
            width=10,
        )
        self.preview_label.pack(side="left", padx=(0, 10))
        self.selected_var = tk.StringVar(value="—")
        ttk.Label(
            selection,
            textvariable=self.selected_var,
            wraplength=590,
        ).pack(side="left", fill="x", expand=True)

        buttons = ttk.Frame(self, padding=(12, 6, 12, 12))
        buttons.pack(fill="x")
        ttk.Button(buttons, text=self.tr("cancel"), command=self.destroy).pack(
            side="right"
        )
        self.use_button = ttk.Button(
            buttons,
            text=self.tr("use_icon"),
            command=self._accept,
            state="disabled",
        )
        self.use_button.pack(side="right", padx=(0, 8))

    def _search_nearby(self) -> None:
        self._icon_results.put(find_nearby_icons(self.executable))

    def _poll_nearby(self) -> None:
        try:
            self.nearby_results = self._icon_results.get_nowait()
        except queue.Empty:
            if self.winfo_exists():
                self.after(100, self._poll_nearby)
            return
        count = len(self.nearby_results)
        self.notebook.tab(self.nearby_frame, text=f"{self.tr('nearby')} ({count})")
        self.nearby_status.configure(
            text="" if count else self.tr("no_icons")
        )
        self._fill_nearby_icons()

    def _fill_nearby_icons(self) -> None:
        query = self.nearby_query.get().strip().casefold()
        items = [
            (str(path), path.name)
            for path in self.nearby_results
            if not query or query in str(path).casefold()
        ]
        self.nearby_grid.set_items(items)

    def _fill_system_icons(self) -> None:
        names = list_system_icons(self.system_search.get().strip())
        self.system_grid.set_items([(name, name) for name in names])

    def _browse_custom(self) -> None:
        path = filedialog.askopenfilename(
            parent=self,
            filetypes=[
                ("Images", "*.png *.svg *.ico *.xpm *.jpg *.jpeg"),
                ("All files", "*"),
            ],
        )
        if not path:
            return
        candidate = Path(path).expanduser()
        if candidate.is_file() and candidate.suffix.lower() in ICON_EXTENSIONS:
            value = str(candidate.resolve())
            self.custom_var.set(value)
            self._select_icon(value)

    def _select_icon(self, value: str) -> None:
        self.selected_var.set(value)
        self.preview_image = load_icon_preview(self, value, 72)
        if self.preview_image is None:
            self.preview_label.configure(image="", text=self.tr("no_preview"))
        else:
            self.preview_label.configure(image=self.preview_image, text="")
        self.use_button.configure(state="normal")

    def _accept(self) -> None:
        value = self.selected_var.get()
        if not value or value == "—":
            messagebox.showwarning(
                self.tr("icon_title"),
                self.tr("select_icon_first"),
                parent=self,
            )
            return
        self.result = value
        self.destroy()

    @classmethod
    def choose(
        cls,
        parent: tk.Misc,
        tr: Translator,
        executable: Path,
        current: str,
    ) -> str | None:
        dialog = cls(parent, tr, executable, current)
        parent.wait_window(dialog)
        return dialog.result


__all__ = ["IconPickerDialog", "load_icon_preview"]
