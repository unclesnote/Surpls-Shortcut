from __future__ import annotations

import unittest

from services.desktop_entry_service import (
    build_exec_value,
    make_file_id,
    split_exec_value,
)


class ExecValueTests(unittest.TestCase):
    def test_builds_quoted_path_and_automatic_uri_field(self) -> None:
        value = build_exec_value("/opt/My App/app", "--verbose", False)
        self.assertEqual(value, '"/opt/My App/app" --verbose %u')

    def test_no_sandbox_is_separate_and_not_duplicated(self) -> None:
        value = build_exec_value(
            "/opt/app/app", "--no-sandbox --profile 'Work Space' %F", True
        )
        self.assertEqual(
            value,
            '"/opt/app/app" --no-sandbox --profile "Work Space" %F',
        )
        path, options, no_sandbox = split_exec_value(value)
        self.assertEqual(path, "/opt/app/app")
        self.assertEqual(options, '--profile "Work Space" %F')
        self.assertTrue(no_sandbox)

    def test_generated_id_matches_bash_policy(self) -> None:
        self.assertEqual(make_file_id("Antigravity IDE"), "antigravity-ide")
        self.assertRegex(make_file_id("한글 앱"), r"^app-[0-9a-f]{8}$")


if __name__ == "__main__":
    unittest.main()
