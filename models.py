from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class DesktopEntry:
    file_path: Path | None = None
    file_name: str = ""
    name: str = ""
    comment: str = ""
    executable_path: str = ""
    no_sandbox: bool = False
    execution_options: str = ""
    exec_value: str = ""
    icon: str = "application-x-executable"
    terminal: bool = False
    categories: list[str] = field(default_factory=lambda: ["Utility"])
    startup_notify: bool = True
    manager_created: bool = True
    desktop_copy_exists: bool = False
    sections: dict[str, dict[str, str]] = field(default_factory=dict)
    source_mtime_ns: int | None = None

    @property
    def primary_category(self) -> str:
        return self.categories[0] if self.categories else ""
