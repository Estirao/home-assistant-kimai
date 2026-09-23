"""Offline regression tests for the version/publication decisions."""
import json
from pathlib import Path
import struct
import tempfile
import unittest

from kimai_release import (
    compute_plan, contains_mentions, current_version, normalized_version, png_size,
    release_notes, replace_version, sanitize_mentions, stable_version, verify_manifest, version_key,
)


class VersionTests(unittest.TestCase):
    def test_versions_are_not_limited_to_major_two(self):
        for version in ("2.67.0", "3.0.0", "4.12.5", "12.0.0"):
            self.assertEqual(normalized_version(version), version)

    def test_optional_v_prefix(self):
        self.assertEqual(normalized_version("v3.0.0"), "3.0.0")

    def test_numeric_comparison(self):
        self.assertGreater(version_key("2.100.0"), version_key("2.99.0"))
        self.assertGreater(version_key("3.0.0"), version_key("2.999.0"))

    def test_prerelease_tags_and_moving_tags_are_rejected(self):
        for value in ("stable", "latest", "2", "3.0.0-beta1", "3.0.0-rc.1", "v3.0.0\n", "03.0.0"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalized_version(value)

    def test_draft_and_prerelease_flags_are_rejected(self):
        for field in ("draft", "prerelease"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                stable_version({"tag_name": "3.0.0", field: True})

    def test_stable_tag(self):
        self.assertEqual(stable_version({"tag_name": "v3.0.0", "draft": False, "prerelease": False}), "3.0.0")

    def test_major_upgrade_requires_build_but_is_not_blocked(self):
        self.assertEqual(compute_plan("2.67.0", "3.0.0", False, False, False),
                         {"build": True, "publish": True})

    def test_first_release_builds_even_when_config_version_matches(self):
        self.assertEqual(compute_plan("2.67.0", "2.67.0", False, False, True),
                         {"build": True, "publish": True})

    def test_no_daily_duplicate_build_or_release(self):
        self.assertEqual(compute_plan("2.67.0", "2.67.0", True, True, False),
                         {"build": False, "publish": False})

    def test_partial_failure_retries_release_without_rebuilding(self):
        self.assertEqual(compute_plan("2.67.0", "2.67.0", False, True, False),
                         {"build": False, "publish": True})

    def test_branding_can_be_added_without_rebuilding(self):
        self.assertEqual(compute_plan("2.67.0", "2.67.0", True, True, True),
                         {"build": False, "publish": True})

    def test_never_downgrade(self):
        with self.assertRaises(ValueError):
            compute_plan("3.0.0", "2.99.0", False, False, True)

    def test_only_top_level_version_is_changed(self):
        before = ('name: Kimai\nversion: "2.67.0"\noptions:\n'
                  '  database_password: "UNCHANGED"\n  database_version: "11.4.10-MariaDB"\n')
        expected = before.replace('version: "2.67.0"', 'version: "3.0.0"', 1)
        self.assertEqual(replace_version(before, "3.0.0"), expected)

    def test_supported_yaml_quotes(self):
        for text in ('version: "2.67.0"\n', "version: '2.67.0'\n", "version: 2.67.0\n"):
            self.assertEqual(current_version(text), "2.67.0")

    def test_duplicate_version_is_rejected(self):
        with self.assertRaises(ValueError):
            current_version('version: "2.67.0"\nversion: "3.0.0"\n')

    def test_major_warning_in_release_notes(self):
        release = {"tag_name": "3.0.0", "html_url": "https://github.com/kimai/kimai/releases/tag/3.0.0", "body": "Example upstream note"}
        notes = release_notes(release, "2.67.0")
        self.assertIn("Major-version change", notes)
        self.assertIn("Example upstream note", notes)
        self.assertIn("not a test of migration", notes)

    def test_upstream_mentions_are_neutralized(self):
        release = {
            "tag_name": "2.68.0",
            "html_url": "https://github.com/kimai/kimai/releases/tag/2.68.0",
            "body": "Thanks @kevinpapst, @org/team and [@helper](https://github.com/helper).",
        }
        notes = release_notes(release, "2.67.0")
        self.assertNotIn("@kevinpapst", notes)
        self.assertNotIn("@org/team", notes)
        self.assertNotIn("@helper", notes)
        self.assertIn("kevinpapst", notes)
        self.assertIn("org/team", notes)
        self.assertIn("[helper]", notes)
        self.assertFalse(contains_mentions(notes))

    def test_sanitizer_does_not_break_emails_or_url_paths(self):
        text = "Contact maintainer@example.com and see https://example.com/@asset; thanks @person."
        cleaned = sanitize_mentions(text)
        self.assertIn("maintainer@example.com", cleaned)
        self.assertIn("https://example.com/@asset", cleaned)
        self.assertIn("thanks person.", cleaned)

    def test_non_png_is_rejected(self):
        with self.assertRaises(ValueError):
            png_size(b"<html>Not found</html>")

    def test_png_dimensions(self):
        data = b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", 192, 192) + b"\x00" * 9
        self.assertEqual(png_size(data), (192, 192))

    def test_multi_arch_manifest(self):
        document = {"manifests": [{"platform": {"os": "linux", "architecture": arch}} for arch in ("amd64", "arm64")]}
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "manifest.json"
            file.write_text(json.dumps(document))
            verify_manifest(file)
            document["manifests"].pop()
            file.write_text(json.dumps(document))
            with self.assertRaises(ValueError):
                verify_manifest(file)


if __name__ == "__main__":
    unittest.main()
