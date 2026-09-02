from __future__ import annotations

import json
import locale
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


APP_DIR_NAME = "surpls-shortcut"
CATEGORIES = [
    "Utility",
    "Development",
    "Game",
    "Network",
    "AudioVideo",
    "Office",
    "System",
]


def applications_dir() -> Path:
    data_home = os.environ.get("XDG_DATA_HOME")
    base = Path(data_home).expanduser() if data_home else Path.home() / ".local/share"
    return base / "applications"


def desktop_dir() -> Path:
    try:
        result = subprocess.run(
            ["xdg-user-dir", "DESKTOP"],
            check=True,
            capture_output=True,
            text=True,
            timeout=3,
        )
        value = result.stdout.strip()
        if value:
            return Path(value).expanduser()
    except (FileNotFoundError, subprocess.SubprocessError):
        pass
    return Path.home() / "Desktop"


def config_path() -> Path:
    config_home = os.environ.get("XDG_CONFIG_HOME")
    base = Path(config_home).expanduser() if config_home else Path.home() / ".config"
    return base / APP_DIR_NAME / "config.json"


@dataclass(slots=True)
class AppConfig:
    language: str = "ko"

    @classmethod
    def load(cls) -> "AppConfig":
        default_language = "ko" if (locale.getlocale()[0] or "").startswith("ko") else "en"
        path = config_path()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            language = data.get("language", default_language)
            return cls(language=language if language in {"ko", "en"} else default_language)
        except (OSError, ValueError, TypeError):
            return cls(language=default_language)

    def save(self) -> None:
        path = config_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"language": self.language}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
