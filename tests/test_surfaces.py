import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from adapters.surfaces import discover


class SurfaceTests(unittest.TestCase):
    def test_presence_only_never_reads_contents_or_serializes_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home, etc = root / "private-home", root / "etc"
            (home / ".config/fish").mkdir(parents=True)
            etc.mkdir()
            (home / ".config/fish/config.fish").write_text("PRIVATE_TOKEN")
            with patch.object(Path, "read_text", side_effect=AssertionError("content read")):
                rows = discover(home, etc)
            self.assertEqual(next(x for x in rows if x["id"] == "shell.fish")["state"], "present")
            self.assertEqual(next(x for x in rows if x["id"] == "vcs.git-user")["state"], "absent")
            encoded = json.dumps(rows)
            self.assertNotIn("PRIVATE_TOKEN", encoded)
            self.assertNotIn("private-home", encoded)
            self.assertNotIn("config.fish", encoded)

    def test_permission_failure_is_unknown(self):
        with patch.object(Path, "stat", side_effect=PermissionError("private path")):
            rows = discover(Path("/fixture/home"), Path("/fixture/etc"))
        self.assertTrue(all(row["state"] == "unknown" for row in rows))
        self.assertNotIn("private path", json.dumps(rows))
