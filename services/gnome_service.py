from __future__ import annotations

import os
import shutil
import stat
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .desktop_entry_service import (
    DesktopEntryConflictError,
    DesktopEntryError,
    make_file_id,
    parse_desktop_entry,
    write_desktop_entry,
)
from models import DesktopEntry


@dataclass(slots=True)
class SaveResult:
    application_file: Path
    desktop_file: Path | None
    warnings: list[str] = field(default_factory=list)


class GnomeShortcutService:
    def __init__(self, applications_dir: Path, desktop_dir: Path) -> None:
        self.applications_dir = applications_dir
        self.desktop_dir = desktop_dir

    def list_entries(self) -> tuple[list[DesktopEntry], list[str]]:
        self.applications_dir.mkdir(parents=True, exist_ok=True)
        entries: list[DesktopEntry] = []
        errors: list[str] = []
        for path in sorted(self.applications_dir.glob("*.desktop")):
            try:
                entries.append(parse_desktop_entry(path, self.desktop_dir))
            except DesktopEntryError as exc:
                errors.append(str(exc))
        entries.sort(key=lambda item: (item.name.casefold(), item.file_name.casefold()))
        return entries, errors

    def save_entry(
        self,
        entry: DesktopEntry,
        *,
        overwrite: bool = False,
        force_conflict: bool = False,
    ) -> SaveResult:
        if entry.file_path is None:
            file_name = entry.file_name or f"{make_file_id(entry.name)}.desktop"
            if not file_name.endswith(".desktop"):
                file_name += ".desktop"
            target = self.applications_dir / file_name
        else:
            target = entry.file_path
            file_name = target.name

        entry.exec_value = ""
        write_desktop_entry(
            entry,
            target,
            overwrite=overwrite or entry.file_path is not None,
            check_conflict=not force_conflict,
        )

        warnings = self.apply_file_trust(target)
        desktop_target = self.desktop_dir / file_name
        if entry.desktop_copy_exists:
            try:
                self.desktop_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, desktop_target)
                warnings.extend(self.apply_file_trust(desktop_target))
            except OSError as exc:
                warnings.append(f"Could not create Desktop shortcut: {exc}")
                desktop_target = None
        else:
            try:
                desktop_target.unlink(missing_ok=True)
            except OSError as exc:
                warnings.append(f"Could not remove Desktop shortcut: {exc}")
            desktop_target = None

        warnings.extend(self.refresh())
        entry.file_path = target
        entry.file_name = file_name
        try:
            entry.source_mtime_ns = target.stat().st_mtime_ns
        except OSError:
            entry.source_mtime_ns = None
        return SaveResult(target, desktop_target, warnings)

    def delete_entry(self, entry: DesktopEntry) -> list[str]:
        if entry.file_path is None:
            raise DesktopEntryError("The shortcut has no application file.")

        warnings: list[str] = []
        try:
            entry.file_path.unlink()
        except OSError as exc:
            raise DesktopEntryError(f"Could not delete {entry.file_path}: {exc}") from exc

        desktop_target = self.desktop_dir / entry.file_path.name
        try:
            desktop_target.unlink(missing_ok=True)
        except OSError as exc:
            warnings.append(f"Could not remove Desktop shortcut: {exc}")
        warnings.extend(self.refresh())
        return warnings

    def apply_file_trust(self, path: Path) -> list[str]:
        warnings: list[str] = []
        try:
            current_mode = path.stat().st_mode
            path.chmod(current_mode | stat.S_IXUSR)
        except OSError as exc:
            warnings.append(f"Could not add execute permission to {path}: {exc}")

        gio = shutil.which("gio")
        if gio:
            try:
                subprocess.run(
                    [gio, "set", "--type=string", str(path), "metadata::trusted", "true"],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
            except subprocess.SubprocessError as exc:
                warnings.append(
                    f"Could not mark {path.name} as trusted; Allow Launching may be required: {exc}"
                )
        elif path.parent == self.desktop_dir:
            warnings.append("gio is not installed; Allow Launching may be required.")
        return warnings

    def refresh(self) -> list[str]:
        warnings: list[str] = []
        commands: list[list[str]] = []
        update_database = shutil.which("update-desktop-database")
        if update_database:
            commands.append([update_database, str(self.applications_dir)])

        icon_cache = shutil.which("gtk-update-icon-cache")
        user_icons = Path.home() / ".local/share/icons"
        if icon_cache and user_icons.is_dir():
            commands.append([icon_cache, "-f", "-t", str(user_icons)])

        for command in commands:
            try:
                subprocess.run(
                    command,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=20,
                )
            except subprocess.SubprocessError as exc:
                warnings.append(f"Integration command failed ({Path(command[0]).name}): {exc}")

        for directory in (self.applications_dir, self.desktop_dir):
            if directory.is_dir():
                try:
                    os.utime(directory, None)
                except OSError:
                    pass
        return warnings

    @staticmethod
    def grant_execute_permission(path: Path) -> None:
        path.chmod(path.stat().st_mode | stat.S_IXUSR)


__all__ = [
    "DesktopEntryConflictError",
    "GnomeShortcutService",
    "SaveResult",
]
