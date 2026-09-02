from __future__ import annotations

import copy
import os
import queue
import secrets
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import TYPE_CHECKING, Callable

from config import CATEGORIES
from models import DesktopEntry
from services.desktop_entry_service import (
    DesktopEntryConflictError,
    DesktopEntryError,
    build_exec_value,
    make_file_id,
)
from services.gnome_service import SaveResult
from services.sandbox_service import diagnose_sandbox

from .icon_picker import IconPickerDialog, load_icon_preview

if TYPE_CHECKING:
    from .main_window import ShortcutManagerApp


class AppEditorDialog(tk.Toplevel):
    def __init__(
        self,
        parent: ShortcutManagerApp,
        entry: DesktopEntry | None,
        on_saved: Callable[[str], None],
    ) -> None:
        super().__init__(parent)
        self.app = parent
        self.tr = parent.tr
        self.service = parent.service
        self.original = entry
        self.entry = copy.deepcopy(entry) if entry else DesktopEntry()
        self.fallback_file_id = f"app-{secrets.token_hex(4)}"
        self.saving = False
        self._save_results: queue.Queue[
            tuple[SaveResult | None, Exception | None]
        ] = queue.Queue(maxsize=1)
        self.on_saved = on_saved
        self.title(self.tr("edit_title") if entry else self.tr("new_title"))
        self.geometry("760x690")
        self.minsize(650, 600)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self._request_close)

        self.name_var = tk.StringVar(value=self.entry.name)
        self.comment_var = tk.StringVar(value=self.entry.comment)
        self.path_var = tk.StringVar(value=self.entry.executable_path)
        self.no_sandbox_var = tk.BooleanVar(value=self.entry.no_sandbox)
        self.options_var = tk.StringVar(value=self.entry.execution_options)
        self.terminal_var = tk.BooleanVar(value=self.entry.terminal)
        self.icon_var = tk.StringVar(
            value=self.entry.icon or "application-x-executable"
        )
        self.category_var = tk.StringVar(
            value=self.entry.primary_category or "Utility"
        )
        self.desktop_var = tk.BooleanVar(
            value=self.entry.desktop_copy_exists if entry else True
        )
        self.preview_var = tk.StringVar()
        self.target_var = tk.StringVar()

        outer = ttk.Frame(self, padding=14)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        self._build_form(outer)

        for variable in (
            self.name_var,
            self.path_var,
            self.options_var,
            self.no_sandbox_var,
        ):
            variable.trace_add("write", lambda *_: self._update_derived())
        self.path_var.trace_add("write", lambda *_: self._update_path_status())
        self.no_sandbox_var.trace_add(
            "write", lambda *_: self._update_sandbox_warning()
        )
        self.icon_var.trace_add("write", lambda *_: self._update_icon_preview())
        self._update_derived()
        self._update_path_status()
        self._update_sandbox_warning()
        self._update_icon_preview()

        self.bind("<Escape>", lambda _event: self._request_close())
        self.bind("<Control-Return>", lambda _event: self._save())
        self.grab_set()
        self.name_entry.focus_set()

    def _build_form(self, outer: ttk.Frame) -> None:
        basic = ttk.LabelFrame(outer, text=self.tr("basic_info"), padding=10)
        basic.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        basic.columnconfigure(1, weight=1)
        ttk.Label(basic, text=f"{self.tr('name')} *").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=5
        )
        self.name_entry = ttk.Entry(basic, textvariable=self.name_var)
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=5)
        ttk.Label(basic, text=self.tr("description")).grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=5
        )
        ttk.Entry(basic, textvariable=self.comment_var).grid(
            row=1, column=1, sticky="ew", pady=5
        )

        execution = ttk.LabelFrame(outer, text=self.tr("execution"), padding=10)
        execution.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        execution.columnconfigure(1, weight=1)
        ttk.Label(execution, text=f"{self.tr('executable')} *").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=5
        )
        ttk.Entry(execution, textvariable=self.path_var).grid(
            row=0, column=1, sticky="ew", pady=5
        )
        ttk.Button(
            execution,
            text=self.tr("browse"),
            command=self._browse_executable,
        ).grid(row=0, column=2, padx=(8, 0), pady=5)
        self.path_status = ttk.Label(execution)
        self.path_status.grid(row=1, column=1, columnspan=2, sticky="w")

        sandbox_row = ttk.Frame(execution)
        sandbox_row.grid(row=2, column=1, columnspan=2, sticky="ew", pady=(9, 2))
        ttk.Checkbutton(
            sandbox_row,
            text=self.tr("no_sandbox"),
            variable=self.no_sandbox_var,
        ).pack(side="left")
        ttk.Label(sandbox_row, text=self.tr("no_sandbox_hint")).pack(
            side="left", padx=8
        )
        ttk.Button(
            sandbox_row,
            text=self.tr("diagnose"),
            command=self._diagnose,
        ).pack(side="right")
        self.sandbox_warning = ttk.Label(execution, wraplength=570)
        self.sandbox_warning.grid(row=3, column=1, columnspan=2, sticky="w")

        ttk.Label(execution, text=self.tr("options")).grid(
            row=4, column=0, sticky="w", padx=(0, 10), pady=5
        )
        ttk.Entry(execution, textvariable=self.options_var).grid(
            row=4, column=1, columnspan=2, sticky="ew", pady=5
        )
        ttk.Label(execution, text=self.tr("exec_preview")).grid(
            row=5, column=0, sticky="nw", padx=(0, 10), pady=5
        )
        ttk.Label(
            execution,
            textvariable=self.preview_var,
            wraplength=570,
        ).grid(row=5, column=1, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(
            execution,
            text=self.tr("run_terminal"),
            variable=self.terminal_var,
        ).grid(row=6, column=1, sticky="w", pady=(6, 2))

        display = ttk.LabelFrame(outer, text=self.tr("display"), padding=10)
        display.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        display.columnconfigure(2, weight=1)
        self.icon_preview_image: tk.PhotoImage | None = None
        self.icon_preview = ttk.Label(
            display,
            text=self.tr("no_preview"),
            anchor="center",
            width=11,
        )
        self.icon_preview.grid(
            row=0,
            column=0,
            rowspan=3,
            sticky="nsew",
            padx=(0, 12),
        )
        ttk.Label(display, text=self.tr("icon")).grid(
            row=0, column=1, sticky="w", padx=(0, 10), pady=5
        )
        ttk.Entry(
            display,
            textvariable=self.icon_var,
            state="readonly",
        ).grid(row=0, column=2, sticky="ew", pady=5)
        ttk.Button(
            display,
            text=self.tr("choose_icon"),
            command=self._choose_icon,
        ).grid(row=0, column=3, padx=(8, 0), pady=5)
        ttk.Label(display, text=self.tr("category")).grid(
            row=1, column=1, sticky="w", padx=(0, 10), pady=5
        )
        ttk.Combobox(
            display,
            textvariable=self.category_var,
            values=CATEGORIES,
            state="readonly",
        ).grid(row=1, column=2, sticky="ew", pady=5)
        ttk.Checkbutton(
            display,
            text=self.tr("desktop_copy"),
            variable=self.desktop_var,
        ).grid(row=2, column=2, sticky="w", pady=5)

        target = ttk.Frame(outer)
        target.grid(row=3, column=0, sticky="ew")
        ttk.Label(target, text=f"{self.tr('target_file')}:").pack(side="left")
        ttk.Label(target, textvariable=self.target_var).pack(side="left", padx=(6, 0))

        buttons = ttk.Frame(outer)
        buttons.grid(row=4, column=0, sticky="e", pady=(16, 0))
        self.cancel_button = ttk.Button(
            buttons,
            text=self.tr("cancel"),
            command=self._request_close,
        )
        self.cancel_button.pack(side="left")
        self.save_button = ttk.Button(
            buttons,
            text=self.tr("save"),
            command=self._save,
        )
        self.save_button.pack(side="left", padx=(8, 0))

    def _browse_executable(self) -> None:
        path = filedialog.askopenfilename(parent=self)
        if not path:
            return
        self.path_var.set(str(Path(path).resolve()))
        if not self.name_var.get().strip():
            name = Path(path).stem.replace("-", " ").replace("_", " ").title()
            self.name_var.set(name)

    def _update_path_status(self) -> None:
        path = Path(self.path_var.get()).expanduser()
        if path.is_file() and os.access(path, os.X_OK):
            text = self.tr("path_valid")
        elif path.is_file():
            text = self.tr("path_not_executable")
        else:
            text = self.tr("path_invalid")
        self.path_status.configure(text=text)

    def _update_sandbox_warning(self) -> None:
        self.sandbox_warning.configure(
            text=self.tr("sandbox_warning") if self.no_sandbox_var.get() else ""
        )

    def _update_icon_preview(self) -> None:
        self.icon_preview_image = load_icon_preview(
            self,
            self.icon_var.get().strip(),
            64,
        )
        if self.icon_preview_image is None:
            self.icon_preview.configure(image="", text=self.tr("no_preview"))
        else:
            self.icon_preview.configure(image=self.icon_preview_image, text="")

    def _update_derived(self) -> None:
        try:
            preview = build_exec_value(
                self.path_var.get(),
                self.options_var.get(),
                self.no_sandbox_var.get(),
            )
        except DesktopEntryError:
            preview = "—"
        self.preview_var.set(preview)
        if self.entry.file_path:
            target = self.entry.file_path
        else:
            target = self.service.applications_dir / (
                f"{make_file_id(self.name_var.get(), self.fallback_file_id)}.desktop"
            )
        self.target_var.set(str(target))

    def _choose_icon(self) -> None:
        selected = IconPickerDialog.choose(
            self,
            self.tr,
            Path(self.path_var.get()).expanduser(),
            self.icon_var.get(),
        )
        if selected:
            self.icon_var.set(selected)

    def _diagnose(self) -> None:
        path = Path(self.path_var.get()).expanduser()
        if not path.is_file():
            messagebox.showerror(
                self.tr("diagnostic_title"),
                self.tr("invalid_path"),
                parent=self,
            )
            return
        result = diagnose_sandbox(path, self.app.entries)
        body = result.summary + "\n\n" + "\n".join(
            f"• {item}" for item in result.details
        )
        if result.existing_no_sandbox and not self.no_sandbox_var.get():
            if messagebox.askyesno(
                self.tr("diagnostic_title"),
                body + self.tr("diagnostic_import"),
                parent=self,
            ):
                self.no_sandbox_var.set(True)
        else:
            messagebox.showinfo(self.tr("diagnostic_title"), body, parent=self)

    def _validate(self) -> bool:
        if not self.name_var.get().strip():
            messagebox.showerror(
                self.tr("edit_title"),
                self.tr("required_name"),
                parent=self,
            )
            self.name_entry.focus_set()
            return False
        path = Path(self.path_var.get()).expanduser()
        if not path.is_file():
            messagebox.showerror(
                self.tr("edit_title"), self.tr("invalid_path"), parent=self
            )
            return False
        icon = self.icon_var.get().strip()
        if Path(icon).is_absolute() and not Path(icon).is_file():
            messagebox.showerror(
                self.tr("edit_title"), self.tr("invalid_icon"), parent=self
            )
            return False
        try:
            build_exec_value(
                str(path.resolve()),
                self.options_var.get(),
                self.no_sandbox_var.get(),
            )
        except DesktopEntryError as exc:
            messagebox.showerror(
                self.tr("edit_title"),
                self.tr("invalid_options", error=exc),
                parent=self,
            )
            return False
        if not os.access(path, os.X_OK):
            answer = messagebox.askyesnocancel(
                self.tr("permission_title"),
                self.tr("permission_question"),
                parent=self,
            )
            if answer is None:
                return False
            if answer:
                try:
                    self.service.grant_execute_permission(path)
                except OSError as exc:
                    messagebox.showerror(
                        self.tr("permission_title"), str(exc), parent=self
                    )
                    return False
        return True

    def _populate_entry(self) -> None:
        self.entry.name = self.name_var.get().strip()
        self.entry.comment = (
            self.comment_var.get().strip() or f"{self.entry.name} Application"
        )
        self.entry.executable_path = str(
            Path(self.path_var.get()).expanduser().resolve()
        )
        self.entry.no_sandbox = self.no_sandbox_var.get()
        self.entry.execution_options = self.options_var.get().strip()
        self.entry.icon = self.icon_var.get().strip() or "application-x-executable"
        self.entry.terminal = self.terminal_var.get()
        self.entry.categories = [self.category_var.get() or "Utility"]
        self.entry.desktop_copy_exists = self.desktop_var.get()
        if self.entry.file_path is None:
            self.entry.file_name = (
                f"{make_file_id(self.entry.name, self.fallback_file_id)}.desktop"
            )
        self.entry.exec_value = build_exec_value(
            self.entry.executable_path,
            self.entry.execution_options,
            self.entry.no_sandbox,
        )

    def _save(self) -> None:
        if self.saving or not self._validate():
            return
        self._populate_entry()
        self._attempt_save(False, False)

    def _attempt_save(self, overwrite: bool, force_conflict: bool) -> None:
        self.saving = True
        self.save_button.configure(state="disabled", text=self.tr("saving"))
        self.cancel_button.configure(state="disabled")

        def worker() -> None:
            try:
                result = self.service.save_entry(
                    self.entry,
                    overwrite=overwrite,
                    force_conflict=force_conflict,
                )
                error: Exception | None = None
            except Exception as exc:  # Reported on the Tk main thread.
                result = None
                error = exc
            self._save_results.put((result, error))

        threading.Thread(target=worker, daemon=True).start()
        self.after(100, lambda: self._poll_save(overwrite, force_conflict))

    def _poll_save(self, overwrite: bool, force_conflict: bool) -> None:
        try:
            result, error = self._save_results.get_nowait()
        except queue.Empty:
            if self.winfo_exists():
                self.after(100, lambda: self._poll_save(overwrite, force_conflict))
            return
        self._finish_save(result, error, overwrite, force_conflict)

    def _finish_save(
        self,
        result: SaveResult | None,
        error: Exception | None,
        overwrite: bool,
        force_conflict: bool,
    ) -> None:
        if not self.winfo_exists():
            return
        self.saving = False
        self.save_button.configure(state="normal", text=self.tr("save"))
        self.cancel_button.configure(state="normal")
        if isinstance(error, FileExistsError):
            if messagebox.askyesno(
                self.tr("overwrite_title"),
                self.tr("overwrite_question", path=error.filename or error.args[0]),
                parent=self,
            ):
                self._attempt_save(True, force_conflict)
            return
        if isinstance(error, DesktopEntryConflictError):
            if messagebox.askyesno(
                self.tr("conflict_title"),
                self.tr("conflict_question"),
                parent=self,
            ):
                self._attempt_save(overwrite, True)
            return
        if error is not None:
            messagebox.showerror(
                self.tr("edit_title"),
                self.tr("save_error", error=error),
                parent=self,
            )
            return
        if result is None:
            return
        if result.warnings:
            messagebox.showwarning(
                self.tr("edit_title"),
                self.tr("saved_warning", warnings="\n".join(result.warnings)),
                parent=self,
            )
        self.on_saved(self.entry.name)
        self.destroy()

    def _request_close(self) -> None:
        if not self.saving:
            self.destroy()


__all__ = ["AppEditorDialog"]
