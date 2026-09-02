from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from models import DesktopEntry
from services.sandbox_service import diagnose_sandbox


class SandboxDiagnosticTests(unittest.TestCase):
    def test_detects_existing_no_sandbox_without_running_executable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "app"
            executable.write_text("binary", encoding="utf-8")
            existing = DesktopEntry(
                name="Existing",
                executable_path=str(executable),
                no_sandbox=True,
            )
            result = diagnose_sandbox(executable, [existing])
        self.assertTrue(result.existing_no_sandbox)
        self.assertEqual(result.level, "warning")


if __name__ == "__main__":
    unittest.main()
