from __future__ import annotations

import os
import stat
from dataclasses import dataclass, field
from pathlib import Path

from models import DesktopEntry


@dataclass(slots=True)
class SandboxDiagnostic:
    level: str
    summary: str
    details: list[str] = field(default_factory=list)
    existing_no_sandbox: bool = False


def _read_flag(path: Path) -> int | None:
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def diagnose_sandbox(
    executable: Path,
    existing_entries: list[DesktopEntry] | None = None,
) -> SandboxDiagnostic:
    executable = executable.expanduser().resolve(strict=False)
    details: list[str] = []
    existing_no_sandbox = False

    for entry in existing_entries or []:
        try:
            same_path = Path(entry.executable_path).expanduser().resolve(strict=False) == executable
        except (OSError, ValueError):
            same_path = entry.executable_path == str(executable)
        if same_path and entry.no_sandbox:
            existing_no_sandbox = True
            details.append("An existing shortcut for this executable uses --no-sandbox.")
            break

    parent = executable.parent
    electron_markers = [
        parent / "resources/app.asar",
        parent / "resources/default_app.asar",
        parent / "chrome-sandbox",
    ]
    likely_chromium = any(path.exists() for path in electron_markers)
    if likely_chromium:
        details.append("Electron/Chromium-related files were found near the executable.")
    else:
        details.append("No obvious Electron/Chromium files were found near the executable.")

    helper = parent / "chrome-sandbox"
    valid_helper = False
    if helper.is_file():
        try:
            helper_stat = helper.stat()
            valid_helper = (
                helper_stat.st_uid == 0
                and bool(helper_stat.st_mode & stat.S_ISUID)
                and os.access(helper, os.X_OK)
            )
            details.append(
                "chrome-sandbox has root ownership, setuid, and execute permission."
                if valid_helper
                else "chrome-sandbox exists but its root/setuid/execute configuration is incomplete."
            )
        except OSError as exc:
            details.append(f"Could not inspect chrome-sandbox: {exc}")

    userns = _read_flag(Path("/proc/sys/kernel/unprivileged_userns_clone"))
    apparmor_restrict = _read_flag(
        Path("/proc/sys/kernel/apparmor_restrict_unprivileged_userns")
    )
    if userns is not None:
        details.append(f"kernel.unprivileged_userns_clone={userns}")
    if apparmor_restrict is not None:
        details.append(f"kernel.apparmor_restrict_unprivileged_userns={apparmor_restrict}")

    profile_found = False
    profile_dir = Path("/etc/apparmor.d")
    if profile_dir.is_dir():
        executable_text = str(executable)
        for profile in profile_dir.iterdir():
            if not profile.is_file():
                continue
            try:
                content = profile.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if executable_text in content and "userns" in content:
                profile_found = True
                details.append(f"A possible AppArmor userns profile was found: {profile.name}")
                break

    if existing_no_sandbox:
        level = "warning"
        summary = "An existing shortcut already uses --no-sandbox."
    elif likely_chromium and userns == 0 and not valid_helper:
        level = "warning"
        summary = "A sandbox startup problem is possible because user namespaces are disabled."
    elif likely_chromium and apparmor_restrict == 1 and not profile_found and not valid_helper:
        level = "warning"
        summary = "A sandbox startup problem is possible under the current AppArmor restriction."
    elif likely_chromium and (valid_helper or profile_found or apparmor_restrict == 0):
        level = "ok"
        summary = "No known sandbox configuration problem was found."
    else:
        level = "unknown"
        summary = "The need for --no-sandbox cannot be determined without running the app."

    return SandboxDiagnostic(level, summary, details, existing_no_sandbox)
