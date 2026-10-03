import copy
import unittest

from workbenchlib.explanation_evidence import build_bundle
from workbenchlib.explanation_formatter import format_bundle


class ExplanationFormatterTests(unittest.TestCase):
    def test_stable_order_and_provenance(self):
        bundle = build_bundle(
            snapshot={"schema_version": 1, "probes": [
                {"id": "z", "status": "ok", "observation": "present", "facts": {"b": 2, "a": 1},
                 "provenance": {"parser": "fixture:v1", "kind": "file"}},
                {"id": "a", "status": "ok", "observation": "not_present", "facts": {},
                 "provenance": {"kind": "catalog"}},
            ]},
            comparison={"schema_version": 1, "changes": [
                {"key": "z", "classification": "changed"},
                {"key": "a", "classification": "unknown"},
            ]},
            proposal={"schema_version": 1, "proposal_only": True, "entries": [
                {"id": "z", "classification": "missing"},
                {"id": "a", "classification": "observation-unknown"},
            ]},
        )
        reordered = copy.deepcopy(bundle)
        for section in (reordered["observations"], reordered["changes"], reordered["proposal"]["entries"]):
            section.reverse()
        rendered = format_bundle(bundle)
        self.assertEqual(rendered, format_bundle(reordered))
        self.assertLess(rendered.index('"a": not_present'), rendered.index('"z": present'))
        self.assertIn('Provenance: {"kind": "file", "parser": "fixture:v1"}', rendered)
        self.assertIn('"a": unknown', rendered)
        self.assertIn('Proposals (proposal only):', rendered)

    def test_unknown_is_separate_and_retains_status(self):
        bundle = build_bundle(snapshot={"schema_version": 1, "probes": [
            {"id": "blocked", "status": "access_denied", "observation": "not_present",
             "facts": {"ids": []}, "provenance": {"kind": "file"}},
            {"id": "partial", "status": "ok", "observation": "unknown",
             "facts": {"evidence": [{"state": "unknown"}]}, "provenance": None},
        ]})
        rendered = format_bundle(bundle)
        self.assertIn('"blocked": unknown (status: "access_denied")', rendered)
        self.assertIn('"partial": unknown (status: "ok")', rendered)
        self.assertIn('Facts: {"evidence": [{"state": "unknown"}]}', rendered)
        self.assertEqual(rendered.split("Unknown/incomplete evidence:")[0], "Observations:\n  (none)\n")
        self.assertNotIn('"blocked": not_present', rendered)

    def test_missing_and_empty_sections_are_distinct(self):
        self.assertEqual(format_bundle({"schema_version": 1}),
                         "Observations:\n  (not supplied)\nUnknown/incomplete evidence:\n  (not supplied)\n"
                         "Comparison changes:\n  (not supplied)\nProposals (proposal only):\n  (not supplied)\n")
        rendered = format_bundle({"schema_version": 1, "observations": [], "changes": [],
                                  "proposal": {"proposal_only": True, "entries": []}})
        self.assertEqual(rendered.count("  (none)"), 4)

    def test_malformed_bundle(self):
        valid = {"schema_version": 1, "observations": [], "changes": [],
                 "proposal": {"proposal_only": True, "entries": []}}
        bad = [None, {}, {"schema_version": 2}, {"schema_version": True},
               {**valid, "observations": [{}]},
               {**valid, "observations": [{"id": "x", "status": "ok", "observation": [],
                                            "facts": {}, "provenance": None}]},
               {**valid, "observations": [{"id": "x", "status": "access_denied",
                                            "observation": "not_present", "facts": {}, "provenance": None}]},
               {**valid, "changes": [{"key": "x", "classification": "missing"}]},
               {**valid, "changes": [{"key": "x", "classification": []}]},
               {**valid, "proposal": {"proposal_only": False, "entries": []}},
               {**valid, "proposal": {"proposal_only": True, "entries": [{}]}},
               {**valid, "extra": float("nan")}]
        for bundle in bad:
            with self.subTest(bundle=bundle), self.assertRaises(ValueError):
                format_bundle(bundle)


if __name__ == "__main__":
    unittest.main()
