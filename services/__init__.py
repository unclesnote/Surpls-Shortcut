"""Application services for desktop entries and GNOME integration."""

from .gnome_service import GnomeShortcutService, SaveResult

__all__ = ["GnomeShortcutService", "SaveResult"]
