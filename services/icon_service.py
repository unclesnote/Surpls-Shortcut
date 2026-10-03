from __future__ import annotations

import os
import shutil
import subprocess
import zlib
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
ICON_CACHE_DIR = "icon_cache"
ICON_CACHE_SIZE = 256


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
            elif ICON_CACHE_DIR in directories:
                directories.remove(ICON_CACHE_DIR)
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


def icon_cache_dir(executable: Path | None) -> Path | None:
    """Return the icon_cache folder beside the executable, if it has a location."""
    if executable is None or executable == Path() or not executable.exists():
        return None
    root = executable if executable.is_dir() else executable.parent
    return root / ICON_CACHE_DIR


def ensure_png_icon(source: Path, cache_dir: Path | None) -> Path | None:
    """Return a PNG for `source`, converting into `cache_dir` as name_crc.png."""
    if source.suffix.lower() == ".png":
        return source
    if cache_dir is None:
        return None

    try:
        crc = zlib.crc32(source.read_bytes()) & 0xFFFFFFFF
        target = cache_dir / f"{source.stem}_{crc:08x}.png"
        if target.is_file():
            return target
        cache_dir.mkdir(parents=True, exist_ok=True)
        if not _convert_to_png(source, target):
            return None
    except OSError:
        return None
    return target


def resolve_preview_png(icon: str, cache_dir: Path | None) -> Path | None:
    """Resolve a file path or theme icon name to a PNG that Tk can display."""
    path = Path(icon).expanduser()
    if not path.is_file():
        resolved = resolve_system_icon(icon)
        if resolved is None:
            return None
        path = resolved
    return ensure_png_icon(path, cache_dir)


def _convert_to_png(source: Path, target: Path) -> bool:
    temporary = target.with_suffix(".tmp")
    try:
        if source.suffix.lower() == ".svg":
            converter = shutil.which("rsvg-convert")
            if converter is None:
                return False
            subprocess.run(
                [
                    converter,
                    "-w",
                    str(ICON_CACHE_SIZE),
                    "-h",
                    str(ICON_CACHE_SIZE),
                    "--keep-aspect-ratio",
                    "-f",
                    "png",
                    "-o",
                    str(temporary),
                    str(source),
                ],
                check=True,
                capture_output=True,
                timeout=20,
            )
        else:
            from PIL import Image

            with Image.open(source) as image:
                converted = image.convert("RGBA")
                converted.thumbnail((ICON_CACHE_SIZE, ICON_CACHE_SIZE))
                converted.save(temporary, format="PNG")
        temporary.replace(target)
        return True
    except (ImportError, OSError, ValueError, subprocess.SubprocessError):
        return False
    finally:
        temporary.unlink(missing_ok=True)


def _sort_icons(paths: list[Path]) -> list[Path]:
    return sorted(paths, key=lambda path: (len(path.parts), str(path).casefold()))


__all__ = [
    "ICON_EXTENSIONS",
    "ensure_png_icon",
    "icon_cache_dir",
    "find_nearby_icons",
    "list_system_icons",
    "resolve_preview_png",
    "resolve_system_icon",
]
