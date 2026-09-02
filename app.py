#!/usr/bin/env python3
from __future__ import annotations

import sys


def main() -> int:
    try:
        import tkinter  # noqa: F401
    except ModuleNotFoundError:
        print(
            "SurplsShortcut requires Tkinter. Install python3-tk and run again.",
            file=sys.stderr,
        )
        return 1

    from config import AppConfig, applications_dir, desktop_dir
    from services.gnome_service import GnomeShortcutService
    from ui.main_window import ShortcutManagerApp

    service = GnomeShortcutService(applications_dir(), desktop_dir())
    application = ShortcutManagerApp(service, AppConfig.load())
    application.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
