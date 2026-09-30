import json
import unittest
from pathlib import Path

from workbenchlib.desktop_intent import validate

ROOT = Path(__file__).resolve().parent.parent


class DesktopIntentTests(unittest.TestCase):
    def test_candidate_is_complete_and_portable(self):
        intent = json.loads((ROOT / "spec/desktop-intent.candidate.json").read_text())
        adapter = json.loads((ROOT / "adapters/kde-desktop.candidate.json").read_text())
        validate(intent, adapter)
        self.assertNotIn("kde", json.dumps(intent).lower())
        self.assertNotIn("kwin", json.dumps(intent).lower())
        self.assertNotIn("plasma", json.dumps(intent).lower())

    def test_missing_or_bad_mapping_rejected(self):
        intent = json.loads((ROOT / "spec/desktop-intent.candidate.json").read_text())
        adapter = json.loads((ROOT / "adapters/kde-desktop.candidate.json").read_text())
        adapter["mappings"][0]["support"] = "proved"
        with self.assertRaises(ValueError):
            validate(intent, adapter)
        adapter["mappings"].pop()
        with self.assertRaises(ValueError):
            validate(intent, adapter)
