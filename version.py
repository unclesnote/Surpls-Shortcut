from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


MANIFEST_NAME = "manifest.json"


@dataclass(frozen=True, slots=True)
class Release:
    version: str
    date: str
    notes: tuple[str, ...] = ()

    @property
    def label(self) -> str:
        """The version with exactly one leading "v", whether or not the manifest has it."""
        return f"v{self.version.lstrip('vV')}"

    @property
    def dir_name(self) -> str:
        return f"{self.version}_{self.date}"


def manifest_path() -> Path:
    # PyInstaller unpacks bundled data under sys._MEIPASS.
    base = getattr(sys, "_MEIPASS", None)
    return (Path(base) if base else Path(__file__).resolve().parent) / MANIFEST_NAME


def load_releases(path: Path | None = None) -> list[Release]:
    try:
        data = json.loads((path or manifest_path()).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if not isinstance(data, list):
        return []

    releases: list[Release] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        version, date = item.get("version"), item.get("date")
        if not isinstance(version, str) or not isinstance(date, str):
            continue
        notes = item.get("note", [])
        releases.append(
            Release(
                version=version,
                date=date,
                notes=tuple(str(note) for note in notes) if isinstance(notes, list) else (),
            )
        )
    return releases


def _sort_key(release: Release) -> tuple[str, tuple[int, ...]]:
    return release.date, tuple(int(part) for part in re.findall(r"\d+", release.version))


def latest_release(path: Path | None = None) -> Release | None:
    """The newest entry by date, then version, regardless of array order."""
    releases = load_releases(path)
    return max(releases, key=_sort_key) if releases else None


def render_markdown(releases: list[Release]) -> str:
    """Render every release, newest first, as release notes."""
    lines = ["# Release Notes", ""]
    for release in sorted(releases, key=_sort_key, reverse=True):
        lines.append(f"## {release.label} ({release.date})")
        lines.append("")
        lines.extend(f"- {note}" for note in release.notes)
        if release.notes:
            lines.append("")
    return "\n".join(lines)


def render_commit_message(release: Release) -> str:
    """A release commit message: subject plus the release notes as bullets."""
    lines = [f"release: {release.label} ({release.date})"]
    if release.notes:
        lines.extend(["", *(f"- {note}" for note in release.notes)])
    return "\n".join(lines)
