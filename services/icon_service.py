from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from resources.system_icons import SYSTEM_ICONS


ICON_EXTENSIONS = {".png", ".svg", ".ico", ".xpm", ".jpg", ".jpeg"}
ICON_THEME_ROOTS = (Path.home() / ".icons", Path.home() / ".local/share/icons", Path("/usr/share/icons"))
ICON_THEMES = ("Yaru", "Adwaita", "hicolor", "HighContrast", "Humanity")
ICON_SIZES = (
    "64x64",
    "128x128",
    "256x256",
    "48x48@2x",
    "48x48",
    "scalable",
    "32x32",
    "24x24",
)
ICON_CONTEXTS = ("apps", "mimetypes", "categories", "actions", "devices", "places", "status")


def find_nearby_icons(
    executable: Path,
    max_depth: int = 3,
    limit: int = 100,
) -> list[Path]:
    root = executable if executable.is_dir() else executable.parent
    if not root.is_dir():
        return []

    results: list[Path] = []
    try:
        for current_root, directories, files in os.walk(root):
            current_path = Path(current_root)
            depth = len(current_path.relative_to(root).parts)
            if depth >= max_depth:
                directories.clear()
            for file_name in files:
                path = current_path / file_name
                if path.suffix.lower() in ICON_EXTENSIONS:
                    results.append(path.resolve())
                    if len(results) >= limit:
                        return _sort_icons(results)
    except OSError:
        pass
    return _sort_icons(results)


def list_system_icons(query: str = "") -> list[str]:
    normalized_query = query.casefold()
    return [name for name in SYSTEM_ICONS if normalized_query in name.casefold()]


@lru_cache(maxsize=256)
def resolve_system_icon(name: str) -> Path | None:
    """Resolve a Freedesktop icon name to a previewable theme file."""
    for extension in (".png", ".gif", ".svg", ".xpm"):
        for root in ICON_THEME_ROOTS:
            for theme in ICON_THEMES:
                theme_root = root / theme
                for size in ICON_SIZES:
                    for context in ICON_CONTEXTS:
                        candidates = (
                            theme_root / size / context / f"{name}{extension}",
                            theme_root / context / size / f"{name}{extension}",
                        )
                        for candidate in candidates:
                            if candidate.is_file():
                                return candidate
    return None


def _sort_icons(paths: list[Path]) -> list[Path]:
    return sorted(paths, key=lambda path: (len(path.parts), str(path).casefold()))


__all__ = [
    "ICON_EXTENSIONS",
    "find_nearby_icons",
    "list_system_icons",
    "resolve_system_icon",
]
