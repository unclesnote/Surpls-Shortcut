#!/usr/bin/env python3
"""Build a single-file executable that needs no Python on the target machine.

    ./env.sh dist.py

Output: dist/<version>_<date>/SurplsShortcut and dist/<version>_<date>/release.md
The version and date come from the newest entry in manifest.json; release.md
lists every entry of manifest.json.

When the build finishes it offers to commit and push the working tree using the
release notes as the commit message, and then to tag the commit with the
version label (for example v1.0.0). Prompts are skipped without a terminal.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

from version import (
    latest_release,
    load_releases,
    render_commit_message,
    render_markdown,
)

ROOT = Path(__file__).resolve().parent
APP_NAME = "SurplsShortcut"
BUILD_VENV = ROOT / ".build-venv"
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"


def run(*command: object, check: bool = True, **kwargs: object) -> subprocess.CompletedProcess:
    return subprocess.run([str(part) for part in command], check=check, cwd=ROOT, **kwargs)


def git(*args: str, **kwargs: object) -> subprocess.CompletedProcess:
    return run("git", "--no-pager", *args, **kwargs)


def ensure_build_python() -> Path:
    python = BUILD_VENV / "bin" / "python"
    if not python.exists():
        shutil.rmtree(BUILD_VENV, ignore_errors=True)
        # System site packages keep Tkinter visible so it gets bundled.
        command = (sys.executable, "-m", "venv", "--system-site-packages", BUILD_VENV)
        try:
            run(*command, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            # python3-venv (ensurepip) is missing: create it bare and fetch pip.
            shutil.rmtree(BUILD_VENV, ignore_errors=True)
            run(*command, "--without-pip")
            with urllib.request.urlopen(GET_PIP_URL, timeout=60) as response:
                run(python, "-", "--quiet", input=response.read())
    run(
        python, "-m", "pip", "install", "--quiet", "--upgrade",
        "pyinstaller", "-r", ROOT / "requirement.txt",
    )
    # PyInstaller only bundles Tcl/Tk when the build Python can import tkinter;
    # otherwise the binary builds fine and then fails at launch.
    if run(python, "-c", "import tkinter", check=False, stderr=subprocess.DEVNULL).returncode:
        raise SystemExit(
            "Tkinter is not importable by the build Python, so it would be missing from "
            "the executable. Install it with: sudo apt install python3-tk"
        )
    return python


def build(out_dir: Path) -> None:
    python = ensure_build_python()
    out_dir.mkdir(parents=True, exist_ok=True)
    # --add-data paths are relative to --specpath (build/).
    run(
        python, "-m", "PyInstaller",
        "--noconfirm", "--clean", "--onefile",
        "--name", APP_NAME,
        "--add-data", "../manifest.json:.",
        "--distpath", out_dir,
        "--workpath", "build",
        "--specpath", "build",
        "app.py",
    )
    notes = render_markdown(load_releases()).rstrip("\n") + "\n"
    (out_dir / "release.md").write_text(notes, encoding="utf-8")
    print(f"Built:   {out_dir / APP_NAME}")
    print(f"Notes:   {out_dir / 'release.md'}")


def ask(question: str) -> bool:
    try:
        return input(f"{question} [y/N] ").strip().lower() in {"y", "yes"}
    except EOFError:
        return False


def publish(label: str, message: str) -> None:
    print()
    git("status", "--short")
    print("\nCommit message:")
    print("\n".join(f"    {line}" for line in message.splitlines()), "\n", sep="\n")

    if not ask("Commit these changes with the release notes and push?"):
        return

    git("add", "-A")
    if git("diff", "--cached", "--quiet", check=False).returncode == 0:
        print("Nothing to commit.")
    else:
        git("commit", "-q", "-F", "-", input=message.encode())
        git("log", "-1", "--format=Committed: %h %s")
    git("push", "-q")
    print("Pushed.")

    tag_exists = git("rev-parse", "-q", "--verify", f"refs/tags/{label}",
                     check=False, stdout=subprocess.DEVNULL).returncode == 0
    if tag_exists:
        print(f"Tag {label} already exists; skipping.")
    elif ask(f"Also add the version label (git tag {label}) and push it?"):
        git("tag", "-a", label, "-F", "-", input=message.encode())
        git("push", "-q", "origin", label)
        print(f"Tagged and pushed {label}.")


def ensure_tkinter_environment() -> None:
    """Re-run through env.sh, which makes Tkinter importable, when it is not."""
    try:
        import tkinter  # noqa: F401
    except ModuleNotFoundError:
        if os.environ.get("SURPLS_DIST_REEXEC"):
            return  # env.sh could not help; ensure_build_python reports it.
        os.environ["SURPLS_DIST_REEXEC"] = "1"
        os.execv(ROOT / "env.sh", [str(ROOT / "env.sh"), *sys.argv])


def main() -> int:
    ensure_tkinter_environment()
    release = latest_release()
    if release is None:
        print("No valid release found in manifest.json", file=sys.stderr)
        return 1

    print(f"Building {APP_NAME} {release.dir_name}")
    try:
        build(ROOT / "dist" / release.dir_name)
        if sys.stdin.isatty():
            publish(release.label, render_commit_message(release))
        else:
            print("Not a terminal; skipping the commit/push/tag prompts.")
    except subprocess.CalledProcessError as exc:
        print(f"Command failed ({exc.returncode}): {' '.join(map(str, exc.cmd))}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
