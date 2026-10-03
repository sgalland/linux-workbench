import copy
import json
import unittest

from workbenchlib.explanation_evidence import build_bundle


class ExplanationEvidenceTests(unittest.TestCase):
    def test_deterministic_order_and_no_input_mutation(self):
        snapshot = {"schema_version": 1, "probes": [
            {"id": "software_repo_explicit", "status": "ok", "observation": "present", "facts": {"ids": ["zsh", "fish"]}, "provenance": {"kind": "command"}},
            {"id": "settings_surfaces", "status": "ok", "observation": "present", "facts": {"surfaces": [{"id": "b", "state": "absent"}, {"id": "a", "state": "present"}]}, "provenance": {"kind": "catalog"}},
        ]}
        comparison = {"schema_version": 1, "changes": [{"key": "z", "classification": "changed"}, {"key": "a", "classification": "unchanged"}]}
        proposal = {"schema_version": 1, "proposal_only": True, "entries": [{"kind": "software", "id": "software.fish", "classification": "missing"}]}
        original = copy.deepcopy((snapshot, comparison, proposal))
        bundle = build_bundle(snapshot=snapshot, comparison=comparison, proposal=proposal)
        reordered = copy.deepcopy(snapshot)
        reordered["probes"].reverse()
        reordered["probes"][0]["facts"]["surfaces"].reverse()
        reordered["probes"][1]["facts"]["ids"].reverse()
        self.assertEqual(json.dumps(bundle, sort_keys=True), json.dumps(build_bundle(snapshot=reordered, comparison={**comparison, "changes": list(reversed(comparison["changes"]))}, proposal=proposal), sort_keys=True))
        self.assertEqual((snapshot, comparison, proposal), original)
        self.assertTrue(bundle["proposal"]["proposal_only"])

    def test_unknown_and_provenance_are_retained(self):
        snapshot = {"schema_version": 1, "probes": [
            {"id": "blocked", "status": "access_denied", "observation": "not_present", "facts": {"ids": []}, "provenance": {"kind": "file", "parser": "fixture:v1"}},
            {"id": "partial", "status": "ok", "observation": "unknown", "facts": {"surfaces": [{"id": "a", "state": "unknown"}]}, "provenance": {"kind": "catalog"}},
        ]}
        rows = build_bundle(snapshot=snapshot)["observations"]
        self.assertEqual(rows[0]["observation"], "unknown")
        self.assertEqual(rows[0]["facts"], {})
        self.assertEqual(rows[0]["provenance"], {"kind": "file", "parser": "fixture:v1"})
        self.assertEqual(rows[1]["facts"]["surfaces"][0]["state"], "unknown")
        missing_state = {"schema_version": 1, "probes": [{"id": "software_targeted", "status": "ok", "observation": "unknown", "facts": {"evidence": [{"evidence_id": "app.example"}]}}]}
        self.assertEqual(build_bundle(snapshot=missing_state)["observations"][0]["facts"]["evidence"][0]["state"], "unknown")

    def test_incomplete_and_malformed_input(self):
        row = build_bundle(snapshot={"schema_version": 1, "probes": [{"id": "incomplete"}]})["observations"][0]
        self.assertEqual((row["status"], row["observation"], row["facts"], row["provenance"]), ("unknown", "unknown", {}, None))
        for kwargs in ({}, {"snapshot": {"schema_version": 2, "probes": []}},
                       {"snapshot": {"schema_version": 1, "probes": [{"id": "x", "facts": []}]}},
                       {"snapshot": {"schema_version": 1, "probes": [{"id": "settings_surfaces", "status": "ok", "facts": {"surfaces": [{"id": "a", "state": "abscent"}]}}]}},
                       {"comparison": {"schema_version": 1, "changes": [{"key": "x"}]}},
                       {"proposal": {"schema_version": 1, "proposal_only": False, "entries": []}}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                build_bundle(**kwargs)


if __name__ == "__main__":
    unittest.main()
