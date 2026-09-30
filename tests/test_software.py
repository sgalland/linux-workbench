import json
import tempfile
import unittest
from pathlib import Path

from adapters.software import discover
from workbenchlib.plan import plan
from workbenchlib.compare import compare


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

    def test_multiple_ide_markers_and_missing_toolbox(self):
        from adapters.software import CATALOG
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "jetbrains-pycharm.desktop").touch()
            (root / "jetbrains-rider.desktop").touch()
            rows = discover(root, path_env="/no-tools-here", catalog=CATALOG,
                            application_roots=(root,))
        states = {row["id"]: row["state"] for row in rows}
        self.assertEqual([states["software.pycharm"], states["software.rider"], states["software.clion"], states["software.webstorm"], states["software.jetbrains-toolbox"]], ["present", "present", "absent", "absent", "absent"])

    def test_targeted_plan_and_compare_keep_unknown(self):
        desired = {"schema_version": 1, "software": [{"id": "software.pycharm", "intent": "optional", "review_category": "development"}], "settings_surfaces": []}
        mapping = {"schema_version": 1, "software": [{"logical_id": "software.pycharm", "source": "targeted", "identifier": "launcher.pycharm"}]}
        def snap(state):
            return {"schema_version": 1, "probes": [{"id": "software_targeted", "status": "ok", "observation": "unknown" if state == "unknown" else "present", "facts": {"evidence": [{"id": "software.pycharm", "evidence_id": "launcher.pycharm", "source": "launcher", "state": state}]}}]}
        self.assertEqual(plan(desired, snap("present"), mapping)["entries"][0]["classification"], "satisfied")
        self.assertEqual(plan(desired, snap("absent"), mapping)["entries"][0]["classification"], "missing")
        self.assertEqual(plan(desired, snap("unknown"), mapping)["entries"][0]["classification"], "observation-unknown")
        self.assertEqual(compare(snap("present"), snap("unknown"))["changes"][0]["classification"], "unknown")
