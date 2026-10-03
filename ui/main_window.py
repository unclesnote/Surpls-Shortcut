from __future__ import annotations

import subprocess
import tkinter as tk
from tkinter import messagebox, ttk

from config import AppConfig
from i18n import Translator
from models import DesktopEntry
from services.desktop_entry_service import DesktopEntryError
from services.gnome_service import GnomeShortcutService
from version import latest_release

from .app_editor import AppEditorDialog
from .delete_dialog import confirm_delete
from .icon_picker import load_icon_preview


class ShortcutManagerApp(tk.Tk):
    def __init__(self, service: GnomeShortcutService, config: AppConfig) -> None:
        super().__init__()
        self.service = service
        self.config_data = config
        self.tr = Translator(config.language)
        self.entries: list[DesktopEntry] = []
        self.visible_entries: list[DesktopEntry] = []
        self.icon_cache: dict[tuple[str, int], tk.PhotoImage | None] = {}
        self.detail_icon_image: tk.PhotoImage | None = None
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.language_var = tk.StringVar(
            value="한국어" if config.language == "ko" else "English"
        )
        self.title(self._window_title())
        self.geometry("1000x680")
        self.minsize(820, 560)
        self._build_ui()
        self._bind_shortcuts()
        self.search_var.trace_add("write", lambda *_: self._filter_entries())
        self.refresh_entries()

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)

        toolbar = ttk.Frame(root)
        toolbar.pack(fill="x", pady=(0, 10))
        self.new_button = ttk.Button(toolbar, command=self.new_entry)
        self.new_button.pack(side="left")
        self.edit_button = ttk.Button(
            toolbar, command=self.edit_entry, state="disabled"
        )
        self.edit_button.pack(side="left", padx=(6, 0))
        self.delete_button = ttk.Button(
            toolbar, command=self.delete_entry, state="disabled"
        )
        self.delete_button.pack(side="left", padx=(6, 0))
        self.refresh_button = ttk.Button(toolbar, command=self.refresh_entries)
        self.refresh_button.pack(side="left", padx=(6, 0))

        self.language_combo = ttk.Combobox(
            toolbar,
            textvariable=self.language_var,
            values=["한국어", "English"],
            state="readonly",
            width=9,
        )
        self.language_combo.pack(side="right")
        self.language_combo.bind("<<ComboboxSelected>>", self._change_language)
        self.search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=28)
        self.search_entry.pack(side="right", padx=(6, 12))
        self.search_label = ttk.Label(toolbar)
        self.search_label.pack(side="right")

        table_frame = ttk.Frame(root)
        table_frame.pack(fill="both", expand=True)
        columns = (
            "name",
            "executable",
            "category",
            "terminal",
            "desktop",
            "managed",
        )
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="tree headings",
            selectmode="browse",
            style="Shortcut.Treeview",
        )
        ttk.Style(self).configure("Shortcut.Treeview", rowheight=40)
        self.tree.column("#0", width=64, minwidth=64, stretch=False, anchor="center")
        widths = {
            "name": 180,
            "executable": 300,
            "category": 110,
            "terminal": 105,
            "desktop": 90,
            "managed": 110,
        }
        for column in columns:
            self.tree.column(
                column,
                width=widths[column],
                minwidth=60,
                stretch=column in {"name", "executable"},
            )
        vertical_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview,
        )
        horizontal_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.tree.xview,
        )
        self.tree.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")
        self.tree.bind("<<TreeviewSelect>>", self._selection_changed)
        self.tree.bind("<Double-1>", lambda _event: self.edit_entry())

        detail_frame = ttk.LabelFrame(root, padding=10)
        detail_frame.pack(fill="x", pady=(10, 0))
        self.detail_icon = ttk.Label(
            detail_frame,
            text=self.tr("no_preview"),
            anchor="center",
            width=11,
        )
        self.detail_icon.pack(side="left", padx=(0, 12))
        detail_content = ttk.Frame(detail_frame)
        detail_content.pack(side="left", fill="x", expand=True)
        self.detail_title = ttk.Label(
            detail_content,
            font=("TkDefaultFont", 11, "bold"),
        )
        self.detail_title.pack(anchor="w")
        self.detail_text = ttk.Label(
            detail_content,
            wraplength=820,
            justify="left",
        )
        self.detail_text.pack(anchor="w", pady=(4, 0))

        status = ttk.Frame(root)
        status.pack(fill="x", pady=(10, 0))
        ttk.Label(status, textvariable=self.status_var).pack(side="left")
        self.folder_button = ttk.Button(
            status,
            command=self.open_applications_folder,
        )
        self.folder_button.pack(side="right")
        self._apply_texts()

    def _window_title(self) -> str:
        release = latest_release()
        title = self.tr("app_title")
        return f"{title} ({release.label})" if release else title

    def _apply_texts(self) -> None:
        self.title(self._window_title())
        self.new_button.configure(text=self.tr("new"))
        self.edit_button.configure(text=self.tr("edit"))
        self.delete_button.configure(text=self.tr("delete"))
        self.refresh_button.configure(text=self.tr("refresh"))
        self.search_label.configure(text=self.tr("search"))
        self.folder_button.configure(text=self.tr("open_folder"))
        self.detail_title.configure(text=self.tr("selected"))
        self.tree.heading("#0", text=self.tr("icon"))
        for column, key in {
            "name": "name",
            "executable": "executable",
            "category": "category",
            "terminal": "terminal",
            "desktop": "desktop",
            "managed": "managed",
        }.items():
            self.tree.heading(column, text=self.tr(key))

    def _bind_shortcuts(self) -> None:
        self.bind("<Control-n>", lambda _event: self.new_entry())
        self.bind("<Control-f>", lambda _event: self.search_entry.focus_set())
        self.bind("<F5>", lambda _event: self.refresh_entries())
        self.tree.bind("<Return>", lambda _event: self.edit_entry())
        self.tree.bind("<Delete>", lambda _event: self.delete_entry())

    def _change_language(self, _event: tk.Event) -> None:
        language = "ko" if self.language_var.get() == "한국어" else "en"
        self.config_data.language = language
        try:
            self.config_data.save()
        except OSError:
            pass
        self.tr.language = language
        self._apply_texts()
        self._filter_entries()
        self._set_default_status()

    def refresh_entries(self) -> None:
        try:
            self.entries, errors = self.service.list_entries()
        except OSError as exc:
            messagebox.showerror(self.tr("app_title"), str(exc), parent=self)
            return
        self.icon_cache.clear()
        self._filter_entries()
        if errors:
            self.status_var.set(
                self.tr("parse_errors", count=len(self.entries), errors=len(errors))
            )
        else:
            self._set_default_status()

    def _set_default_status(self) -> None:
        self.status_var.set(self.tr("ready", count=len(self.entries)))

    def _filter_entries(self) -> None:
        query = self.search_var.get().strip().casefold()
        self.visible_entries = [
            entry
            for entry in self.entries
            if not query
            or query in entry.name.casefold()
            or query in entry.executable_path.casefold()
            or query in entry.file_name.casefold()
        ]
        children = self.tree.get_children()
        if children:
            self.tree.delete(*children)
        for index, entry in enumerate(self.visible_entries):
            image = self._get_icon_image(entry.icon, 32)
            if image is None:
                image = self._get_icon_image("application-x-executable", 32)
            self.tree.insert(
                "",
                "end",
                iid=str(index),
                image=image or "",
                values=(
                    entry.name,
                    entry.executable_path,
                    self._category_label(entry.primary_category),
                    self.tr(
                        "launch_terminal" if entry.terminal else "launch_graphical"
                    ),
                    self.tr(
                        "shortcut_present"
                        if entry.desktop_copy_exists
                        else "shortcut_absent"
                    ),
                    self.tr("manager_owned" if entry.manager_created else "external_item"),
                ),
            )
        self._selection_changed()

    def _category_label(self, category: str) -> str:
        key = f"category_{category.casefold()}"
        translated = self.tr(key)
        return category if translated == key else translated

    def _get_icon_image(self, icon: str, size: int) -> tk.PhotoImage | None:
        key = (icon, size)
        if key not in self.icon_cache:
            self.icon_cache[key] = load_icon_preview(self, icon, size)
        return self.icon_cache[key]

    def _selected_entry(self) -> DesktopEntry | None:
        selection = self.tree.selection()
        if not selection:
            return None
        try:
            return self.visible_entries[int(selection[0])]
        except (IndexError, ValueError):
            return None

    def _selection_changed(self, _event: tk.Event | None = None) -> None:
        entry = self._selected_entry()
        state = "normal" if entry else "disabled"
        self.edit_button.configure(state=state)
        self.delete_button.configure(state=state)
        if not entry:
            self.detail_icon_image = None
            self.detail_icon.configure(image="", text="")
            self.detail_text.configure(text="")
            return
        self.detail_icon_image = self._get_icon_image(entry.icon, 64)
        if self.detail_icon_image is None:
            self.detail_icon.configure(image="", text=self.tr("no_preview"))
        else:
            self.detail_icon.configure(image=self.detail_icon_image, text="")
        self.detail_text.configure(
            text=(
                f"{entry.name}\n"
                f"{self.tr('detail_exec')}: {entry.exec_value}\n"
                f"{self.tr('detail_file')}: {entry.file_path}\n"
                f"{self.tr('terminal')}: "
                f"{self.tr('launch_terminal' if entry.terminal else 'launch_graphical')}  ·  "
                f"{self.tr('desktop')}: "
                f"{self.tr('shortcut_present' if entry.desktop_copy_exists else 'shortcut_absent')}  ·  "
                f"{self.tr('managed')}: "
                f"{self.tr('manager_owned' if entry.manager_created else 'external_item')}"
            )
        )

    def new_entry(self) -> None:
        AppEditorDialog(self, None, self._saved)

    def edit_entry(self) -> None:
        entry = self._selected_entry()
        if entry:
            AppEditorDialog(self, entry, self._saved)

    def _saved(self, name: str) -> None:
        self.refresh_entries()
        self.status_var.set(self.tr("saved", name=name))
        self.after(5000, self._set_default_status)

    def delete_entry(self) -> None:
        entry = self._selected_entry()
        if not entry or not confirm_delete(self, self.tr, self.service, entry):
            return
        try:
            warnings = self.service.delete_entry(entry)
        except DesktopEntryError as exc:
            messagebox.showerror(
                self.tr("delete_title"),
                self.tr("delete_error", error=exc),
                parent=self,
            )
            return
        if warnings:
            messagebox.showwarning(
                self.tr("delete_title"),
                "\n".join(warnings),
                parent=self,
            )
        self.refresh_entries()
        self.status_var.set(self.tr("deleted", name=entry.name))
        self.after(5000, self._set_default_status)

    def open_applications_folder(self) -> None:
        try:
            self.service.applications_dir.mkdir(parents=True, exist_ok=True)
            subprocess.Popen(["xdg-open", str(self.service.applications_dir)])
        except OSError as exc:
            messagebox.showerror(
                self.tr("app_title"),
                self.tr("folder_error", error=exc),
                parent=self,
            )


__all__ = ["ShortcutManagerApp"]
