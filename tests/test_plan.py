import copy
import unittest

from workbenchlib.plan import plan


def desired(*names):
    return {"schema_version": 1, "software": [{"id": name, "intent": "required", "review_category": "development"} for name in names], "settings_surfaces": []}


def snapshot(repo=None, foreign=None, flatpak=None):
    probes = []
    for name, ids in (("software_repo_explicit", repo), ("software_foreign_explicit", foreign), ("software_flatpak_apps", flatpak)):
        probes.append({"id": name, "status": "ok" if ids is not None else "missing_tool", "observation": "present" if ids else "not_present" if ids == [] else "unknown", "facts": {"ids": ids} if ids is not None else {}})
    return {"schema_version": 1, "probes": probes}


def mapping(*rows):
    return {"schema_version": 1, "software": [{"logical_id": logical, "source": source, "identifier": identifier} for logical, source, identifier in rows]}


class PlanTests(unittest.TestCase):
    def test_satisfied_missing_unmanaged_and_deterministic_without_mutation(self):
        want = desired("software.shell", "software.editor")
        seen = snapshot(repo=["zsh", "fish"])
        maps = mapping(("software.shell", "repo", "fish"), ("software.editor", "repo", "vim"))
        original = copy.deepcopy((want, seen, maps))
        entries = plan(want, seen, maps)["entries"]
        self.assertEqual([e["classification"] for e in entries], ["missing", "satisfied", "observed-but-unmanaged"])
        self.assertEqual(entries, plan(want, seen, maps)["entries"])
        self.assertEqual((want, seen, maps), original)
        self.assertNotIn("remove", str(entries))

    def test_unknown_suppresses_missing(self):
        want = desired("software.shell", "software.editor")
        want["software"][0]["intent"] = "optional"
        maps = mapping(("software.shell", "foreign", "fish"), ("software.editor", "repo", "vim"))
        result = plan(want, snapshot(repo=[]), maps)
        by_id = {e["id"]: e for e in result["entries"]}
        self.assertEqual(by_id["software.shell"]["classification"], "observation-unknown")
        self.assertEqual(by_id["software.editor"]["classification"], "missing")
        self.assertTrue(result["proposal_only"])

    def test_mapping_unavailable_conflicts_and_settings(self):
        want = desired("software.shell", "software.editor", "software.extra")
        want["settings_surfaces"] = [{"id": "settings.shell", "intent": "optional", "review_category": "development"}]
        maps = mapping(("software.shell", "repo", "fish"), ("software.editor", "repo", "fish"))
        entries = plan(want, snapshot(repo=["fish"]), maps)["entries"]
        by_id = {e["id"]: e["classification"] for e in entries if "id" in e}
        self.assertEqual(by_id["software.shell"], "ambiguous/conflicting-mapping")
        self.assertEqual(by_id["software.editor"], "ambiguous/conflicting-mapping")
        self.assertEqual(by_id["software.extra"], "mapping-unavailable")
        self.assertEqual(by_id["settings.shell"], "mapping-unavailable")

    def test_multiple_candidates_are_ambiguous(self):
        result = plan(desired("software.shell"), snapshot(repo=["fish"], flatpak=[]), mapping(("software.shell", "repo", "fish"), ("software.shell", "flatpak", "org.example.Fish")))
        self.assertEqual(result["entries"][0]["classification"], "ambiguous/conflicting-mapping")
