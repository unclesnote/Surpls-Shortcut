from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from i18n import Translator
from models import DesktopEntry
from services.gnome_service import GnomeShortcutService


def confirm_delete(
    parent: tk.Misc,
    tr: Translator,
    service: GnomeShortcutService,
    entry: DesktopEntry,
) -> bool:
    """Show the complete delete scope and return the user's decision."""
    if entry.file_path is None:
        return False

    desktop_file = service.desktop_dir / entry.file_path.name
    external = "" if entry.manager_created else tr("external_warning")
    return messagebox.askyesno(
        tr("delete_title"),
        tr(
            "delete_question",
            name=entry.name,
            app_file=entry.file_path,
            desktop_file=desktop_file if desktop_file.exists() else "—",
            external=external,
        ),
        parent=parent,
    )


__all__ = ["confirm_delete"]
