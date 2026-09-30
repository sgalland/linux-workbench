import json
import tempfile
import unittest
from pathlib import Path

from adapters.software import discover


class SoftwareEvidenceTests(unittest.TestCase):
    def test_exact_markers_and_no_paths_or_private_contents(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            apps = home / "applications"
            apps.mkdir()
            (apps / "known.desktop").write_text("Exec=/home/private/token\n")
            (apps / "other.desktop").write_text("Secret=private\n")
            catalog = (("software.known", "launcher.known", "launcher", "desktop", "known.desktop"),)
            rows = discover(home, path_env="/missing", catalog=catalog, application_roots=(apps,))
            self.assertEqual(rows, [{"id": "software.known", "evidence_id": "launcher.known", "source": "launcher", "state": "present"}])
            self.assertNotIn(directory, json.dumps(rows))
            self.assertNotIn("private", json.dumps(rows))

    def test_symlink_is_unknown_and_missing_marker_absent(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            (home / "link").symlink_to("/private/secret")
            catalog = (("software.link", "manual.link", "manual", "marker", "link"), ("software.missing", "manual.missing", "manual", "marker", "missing"))
            self.assertEqual([r["state"] for r in discover(home, path_env="", catalog=catalog)], ["unknown", "absent"])

    def test_missing_path_is_unknown(self):
        catalog = (("software.tool", "command.tool", "command", "command", "tool"),)
        self.assertEqual(discover(Path("/unused"), path_env="", catalog=catalog)[0]["state"], "unknown")
