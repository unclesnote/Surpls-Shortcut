from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from services.desktop_entry_service import (
    DesktopEntryConflictError,
    parse_desktop_entry,
    serialize_desktop_entry,
    write_desktop_entry,
)


class DesktopEntryRoundTripTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.desktop = self.root / "Desktop"
        self.desktop.mkdir()
        self.path = self.root / "sample.desktop"
        self.path.write_text(
            """[Desktop Entry]
Version=1.0
Type=Application
Name=Sample App
Comment=Before
Exec=\"/opt/Sample App/app\" --no-sandbox --verbose %u
Icon=sample
Terminal=false
Categories=Development;
NoDisplay=true

[Desktop Action Debug]
Name=Debug
Exec=\"/opt/Sample App/app\" --debug
""",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_parse_and_serialize_preserve_unknown_fields_and_sections(self) -> None:
        entry = parse_desktop_entry(self.path, self.desktop)
        self.assertTrue(entry.no_sandbox)
        self.assertEqual(entry.execution_options, "--verbose")
        self.assertFalse(entry.manager_created)

        entry.comment = "After"
        output = serialize_desktop_entry(entry)
        self.assertIn("NoDisplay=true", output)
        self.assertIn("[Desktop Action Debug]", output)
        self.assertIn('Exec="/opt/Sample App/app" --no-sandbox --verbose %u', output)

        entry.terminal = True
        self.assertIn("Terminal=true", serialize_desktop_entry(entry))

    def test_detects_external_file_change(self) -> None:
        entry = parse_desktop_entry(self.path, self.desktop)
        self.path.write_text(self.path.read_text(encoding="utf-8") + "# changed\n", encoding="utf-8")
        with self.assertRaises(DesktopEntryConflictError):
            write_desktop_entry(entry, self.path, overwrite=True)


if __name__ == "__main__":
    unittest.main()
