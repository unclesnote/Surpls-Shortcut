from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from version import latest_release, load_releases, manifest_path, render_commit_message, render_markdown


class VersionTests(unittest.TestCase):
    def _write(self, directory: str, data: object) -> Path:
        path = Path(directory) / "manifest.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_latest_is_newest_date_regardless_of_order(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self._write(
                directory,
                [
                    {"version": "1.0.0", "date": "2026-01-01", "note": ["a"]},
                    {"version": "1.1.0", "date": "2026-02-01", "note": ["b", "c"]},
                    {"version": "0.9.0", "date": "2025-12-01", "note": []},
                ],
            )
            release = latest_release(path)
        self.assertEqual(release.version, "1.1.0")
        self.assertEqual(release.notes, ("b", "c"))
        self.assertEqual(release.dir_name, "1.1.0_2026-02-01")

    def test_same_date_prefers_higher_version(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self._write(
                directory,
                [
                    {"version": "1.2.0", "date": "2026-02-01", "note": []},
                    {"version": "1.10.0", "date": "2026-02-01", "note": []},
                ],
            )
            self.assertEqual(latest_release(path).version, "1.10.0")

    def test_invalid_manifest_has_no_release(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assertIsNone(latest_release(Path(directory) / "missing.json"))
            self.assertIsNone(latest_release(self._write(directory, {"version": "1"})))

    def test_markdown_lists_all_releases_newest_first(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self._write(
                directory,
                [
                    {"version": "1.0.0", "date": "2026-01-01", "note": ["first"]},
                    {"version": "1.1.0", "date": "2026-02-01", "note": ["b", "c"]},
                    {"version": "1.1.1", "date": "2026-03-01", "note": []},
                ],
            )
            text = render_markdown(load_releases(path))
        self.assertEqual(
            text,
            "# Release Notes\n\n"
            "## v1.1.1 (2026-03-01)\n\n"
            "## v1.1.0 (2026-02-01)\n\n- b\n- c\n\n"
            "## v1.0.0 (2026-01-01)\n\n- first\n",
        )

    def test_commit_message_has_subject_and_note_bullets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            release = latest_release(
                self._write(directory, [{"version": "1.2.0", "date": "20260101", "note": ["a", "b"]}])
            )
        self.assertEqual(render_commit_message(release), "release: v1.2.0 (20260101)\n\n- a\n- b")

    def test_label_has_a_single_v_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            plain = latest_release(self._write(directory, [{"version": "1.0.0", "date": "1"}]))
            prefixed = latest_release(self._write(directory, [{"version": "v1.0.0", "date": "1"}]))
        self.assertEqual(plain.label, "v1.0.0")
        self.assertEqual(prefixed.label, "v1.0.0")

    def test_project_manifest_is_valid(self) -> None:
        self.assertIsNotNone(latest_release(manifest_path()))


if __name__ == "__main__":
    unittest.main()
