from __future__ import annotations

import configparser
import io
import os
import re
import secrets
import shlex
import tempfile
from pathlib import Path

from models import DesktopEntry


FIELD_CODES = {"%f", "%F", "%u", "%U"}
MANAGER_TAG = "shortcut-manager"
SAFE_EXEC_ARGUMENT = re.compile(r"^[A-Za-z0-9_./:=+,%@-]+$")


class DesktopEntryError(ValueError):
    """Raised when a desktop entry cannot be parsed or validated."""


class DesktopEntryConflictError(DesktopEntryError):
    """Raised when a desktop entry changed after it was loaded."""


def _parser() -> configparser.ConfigParser:
    parser = configparser.ConfigParser(
        interpolation=None,
        strict=False,
        delimiters=("=",),
        comment_prefixes=("#",),
        empty_lines_in_values=False,
    )
    parser.optionxform = str
    return parser


def tokenize_options(value: str) -> list[str]:
    try:
        return shlex.split(value, posix=True)
    except ValueError as exc:
        raise DesktopEntryError(f"Invalid execution options: {exc}") from exc


def _quote_exec_argument(value: str, *, always: bool = False) -> str:
    if not always and value and SAFE_EXEC_ARGUMENT.fullmatch(value):
        return value
    escaped = (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("`", "\\`")
        .replace("$", "\\$")
    )
    return f'"{escaped}"'


def _join_exec_arguments(tokens: list[str]) -> str:
    return " ".join(_quote_exec_argument(token) for token in tokens)


def split_exec_value(exec_value: str) -> tuple[str, str, bool]:
    """Split a Desktop Entry Exec value into path, editable options, and flag."""
    tokens = tokenize_options(exec_value)
    if not tokens:
        return "", "", False

    executable_path = tokens[0]
    option_tokens = tokens[1:]
    no_sandbox = "--no-sandbox" in option_tokens
    option_tokens = [token for token in option_tokens if token != "--no-sandbox"]

    # The manager adds a single trailing %u automatically. Keep other field
    # codes because the user may have supplied them intentionally.
    if option_tokens and option_tokens[-1] == "%u":
        option_tokens.pop()

    return executable_path, _join_exec_arguments(option_tokens), no_sandbox


def _quote_exec_path(path: str) -> str:
    return _quote_exec_argument(path, always=True)


def build_exec_value(executable_path: str, options: str, no_sandbox: bool) -> str:
    path = executable_path.strip()
    if not path:
        raise DesktopEntryError("Executable path is required.")

    tokens = tokenize_options(options)
    tokens = [token for token in tokens if token != "--no-sandbox"]
    if no_sandbox:
        tokens.insert(0, "--no-sandbox")
    if not any(token in FIELD_CODES for token in tokens):
        tokens.append("%u")

    suffix = f" {_join_exec_arguments(tokens)}" if tokens else ""
    return f"{_quote_exec_path(path)}{suffix}"


def make_file_id(app_name: str, fallback: str | None = None) -> str:
    file_id = re.sub(r"[^a-z0-9]", "-", app_name.lower())
    file_id = re.sub(r"-+", "-", file_id).strip("-")
    return file_id or fallback or f"app-{secrets.token_hex(4)}"


def parse_desktop_entry(path: Path, desktop_dir: Path) -> DesktopEntry:
    parser = _parser()
    try:
        with path.open("r", encoding="utf-8") as stream:
            parser.read_file(stream)
    except (OSError, UnicodeError, configparser.Error) as exc:
        raise DesktopEntryError(f"Could not read {path}: {exc}") from exc

    if not parser.has_section("Desktop Entry"):
        raise DesktopEntryError(f"Missing [Desktop Entry] section: {path}")

    section = parser["Desktop Entry"]
    exec_value = section.get("Exec", "")
    executable_path, options, no_sandbox = split_exec_value(exec_value)
    categories = [value for value in section.get("Categories", "").split(";") if value]
    sections = {
        section_name: dict(parser.items(section_name, raw=True))
        for section_name in parser.sections()
    }

    try:
        mtime_ns = path.stat().st_mtime_ns
    except OSError:
        mtime_ns = None

    return DesktopEntry(
        file_path=path,
        file_name=path.name,
        name=section.get("Name", path.stem),
        comment=section.get("Comment", ""),
        executable_path=executable_path,
        no_sandbox=no_sandbox,
        execution_options=options,
        exec_value=exec_value,
        icon=section.get("Icon", "application-x-executable"),
        terminal=section.get("Terminal", "false").lower() == "true",
        categories=categories or ["Utility"],
        startup_notify=section.get("StartupNotify", "true").lower() == "true",
        manager_created=section.get("X-Created-By", "") == MANAGER_TAG,
        desktop_copy_exists=(desktop_dir / path.name).is_file(),
        sections=sections,
        source_mtime_ns=mtime_ns,
    )


def serialize_desktop_entry(entry: DesktopEntry) -> str:
    parser = _parser()
    if entry.sections:
        parser.read_dict(entry.sections)
    if not parser.has_section("Desktop Entry"):
        parser.add_section("Desktop Entry")

    section = parser["Desktop Entry"]
    section["Version"] = section.get("Version", "1.0")
    section["Type"] = "Application"
    section["Name"] = entry.name
    section["Comment"] = entry.comment
    section["Exec"] = build_exec_value(
        entry.executable_path, entry.execution_options, entry.no_sandbox
    )
    section["Icon"] = entry.icon
    section["Terminal"] = str(entry.terminal).lower()
    section["Categories"] = ";".join(entry.categories) + ";"
    section["StartupNotify"] = str(entry.startup_notify).lower()
    if entry.manager_created:
        section["X-Created-By"] = MANAGER_TAG

    output = io.StringIO()
    parser.write(output, space_around_delimiters=False)
    return output.getvalue()


def write_desktop_entry(
    entry: DesktopEntry,
    target: Path,
    *,
    overwrite: bool = False,
    check_conflict: bool = True,
) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists() and not overwrite:
        raise FileExistsError(target)
    if (
        check_conflict
        and entry.file_path == target
        and entry.source_mtime_ns is not None
        and target.exists()
        and target.stat().st_mtime_ns != entry.source_mtime_ns
    ):
        raise DesktopEntryConflictError(f"The file changed on disk: {target}")

    content = serialize_desktop_entry(entry)
    old_mode = target.stat().st_mode & 0o777 if target.exists() else 0o644
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=target.parent,
            prefix=f".{target.name}.",
            delete=False,
        ) as stream:
            temp_name = stream.name
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp_name, old_mode)
        os.replace(temp_name, target)
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)
