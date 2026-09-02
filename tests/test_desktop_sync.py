from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from models import DesktopEntry
from services.gnome_service import GnomeShortcutService


class GnomeShortcutServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.apps = self.root / "applications"
        self.desktop = self.root / "Desktop"
        self.service = GnomeShortcutService(self.apps, self.desktop)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_save_create_and_remove_desktop_copy(self) -> None:
        entry = DesktopEntry(
            name="My Tool",
            comment="Tool",
            executable_path="/opt/my tool/run.sh",
            icon="utilities-terminal",
            terminal=True,
            categories=["Utility"],
            desktop_copy_exists=True,
        )
        with (
            patch.object(self.service, "apply_file_trust", return_value=[]),
            patch.object(self.service, "refresh", return_value=[]),
        ):
            result = self.service.save_entry(entry)
            self.assertTrue(result.application_file.is_file())
            self.assertTrue((self.desktop / "my-tool.desktop").is_file())

            loaded = self.service.list_entries()[0][0]
            loaded.desktop_copy_exists = False
            self.service.save_entry(loaded)
            self.assertFalse((self.desktop / "my-tool.desktop").exists())

    def test_delete_does_not_remove_executable(self) -> None:
        executable = self.root / "real-app"
        executable.write_text("app", encoding="utf-8")
        entry = DesktopEntry(
            name="Real App",
            executable_path=str(executable),
            desktop_copy_exists=True,
        )
        with (
            patch.object(self.service, "apply_file_trust", return_value=[]),
            patch.object(self.service, "refresh", return_value=[]),
        ):
            self.service.save_entry(entry)
            self.service.delete_entry(entry)
        self.assertTrue(executable.exists())

    def test_trust_uses_exact_true_string(self) -> None:
        target = self.root / "trusted.desktop"
        target.write_text("[Desktop Entry]\n", encoding="utf-8")
        completed = Mock(returncode=0)
        with (
            patch("services.gnome_service.shutil.which", return_value="/usr/bin/gio"),
            patch("services.gnome_service.subprocess.run", return_value=completed) as run,
        ):
            warnings = self.service.apply_file_trust(target)
        self.assertEqual(warnings, [])
        self.assertTrue(target.stat().st_mode & 0o100)
        run.assert_called_once_with(
            [
                "/usr/bin/gio",
                "set",
                "--type=string",
                str(target),
                "metadata::trusted",
                "true",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )


if __name__ == "__main__":
    unittest.main()
