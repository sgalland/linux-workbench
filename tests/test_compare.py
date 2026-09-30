import copy
import json
import tempfile
import unittest
from pathlib import Path

from workbenchlib.compare import compare, load_snapshot


def snapshot(*probes):
    return {"schema_version": 1, "probes": list(probes)}


def probe(name, facts, observation="present", status="ok"):
    return {"id": name, "facts": facts, "observation": observation, "status": status}


class CompareTests(unittest.TestCase):
    def test_software_changes_order_and_unchanged_without_mutation(self):
        old = snapshot(probe("software_repo_explicit", {"ids": ["zsh", "fish"]}))
        new = snapshot(probe("software_repo_explicit", {"ids": ["bash", "fish"]}))
        before = copy.deepcopy((old, new))
        self.assertEqual(compare(old, new)["changes"], [
            {"key": "software_repo_explicit/bash", "classification": "added"},
            {"key": "software_repo_explicit/fish", "classification": "unchanged"},
            {"key": "software_repo_explicit/zsh", "classification": "removed"},
        ])
        self.assertEqual((old, new), before)
        self.assertTrue(all(x["classification"] == "unchanged" for x in compare(old, old)["changes"]))

    def test_settings_changes_and_unknown_suppress_removal(self):
        old = snapshot(probe("settings_surfaces", {"surfaces": [{"id": "a", "category": "shell", "state": "present"}, {"id": "b", "category": "shell", "state": "present"}]}))
        new = snapshot(probe("settings_surfaces", {"surfaces": [{"id": "a", "category": "shell", "state": "absent"}, {"id": "b", "category": "shell", "state": "unknown"}]}, "unknown"))
        self.assertEqual([x["classification"] for x in compare(old, new)["changes"]], ["changed", "unknown"])
        failed = snapshot(probe("settings_surfaces", {}, "unknown", "read_error"))
        self.assertTrue(all(x["classification"] == "unknown" for x in compare(old, failed)["changes"]))

    def test_schema_mismatch_and_missing_probe_are_unknown(self):
        old = snapshot(probe("software_flatpak_apps", {"ids": ["org.example.App"]}))
        self.assertEqual(compare(old, snapshot())["changes"][0]["classification"], "unknown")
        with self.assertRaises(ValueError):
            compare(old, {"schema_version": 2, "probes": []})

    def test_cli_path_restriction_and_symlink_escape(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            good = root / "good.json"
            good.write_text(json.dumps(snapshot()))
            self.assertEqual(load_snapshot(str(good), root)["schema_version"], 1)
            external = Path(outside) / "external.json"
            external.write_text(json.dumps(snapshot()))
            (root / "escape.json").symlink_to(external)
            for path in (str(external), str(root / "escape.json"), str(root / "bad.txt")):
                with self.assertRaises(ValueError):
                    load_snapshot(path, root)
