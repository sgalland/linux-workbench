import copy
import json
import unittest
from pathlib import Path

from workbenchlib.desired import validate_desired, validate_mapping

ROOT = Path(__file__).resolve().parent.parent


class DesiredTests(unittest.TestCase):
    def test_examples_validate_and_boundaries_hold(self):
        desired_text = (ROOT / "spec/desired-state.example.json").read_text()
        desired = validate_desired(json.loads(desired_text))
        mapping = validate_mapping(json.loads((ROOT / "adapters/cachyos-software.example.json").read_text()))
        self.assertEqual(desired["software"][0]["id"], mapping["software"][0]["logical_id"])
        for implementation in ("fish", "pacman", "flatpak", "kde", "kwinrc", "org.example"):
            self.assertNotIn(implementation, desired_text.lower())

    def test_rejects_duplicate_and_implementation_fields(self):
        base = {"schema_version": 1, "software": [{"id": "software.shell", "intent": "required", "review_category": "development"}], "settings_surfaces": []}
        validate_desired(base)
        duplicate = copy.deepcopy(base)
        duplicate["software"].append(copy.deepcopy(duplicate["software"][0]))
        with self.assertRaises(ValueError):
            validate_desired(duplicate)
        command = copy.deepcopy(base)
        command["software"][0]["install_command"] = "private"
        with self.assertRaises(ValueError):
            validate_desired(command)
        bad_map = {"schema_version": 1, "software": [{"logical_id": "software.shell", "source": "repo", "identifier": "fish; command"}]}
        with self.assertRaises(ValueError):
            validate_mapping(bad_map)
