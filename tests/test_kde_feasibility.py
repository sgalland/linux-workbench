import json
import unittest

from adapters import kde_feasibility as kde


class KDEEvidenceTests(unittest.TestCase):
    def test_fixed_probe_and_privacy(self):
        calls = []

        def runner(argv):
            calls.append(argv)
            return "4\n", 0

        rows = kde.collect(runner, lambda name: "/fixture/tool")
        self.assertEqual(calls, [list(kde.PROBES["virtual_desktop_count"])])
        self.assertEqual(rows[-1]["value"], 4)
        self.assertNotIn("kwinrc", json.dumps(rows))

    def test_private_or_malformed_output_is_unknown(self):
        for raw in ("/home/private\n", "4\nSecret=token", "0", "21", "", "4 5"):
            rows = kde.collect(lambda argv: (raw, 0), lambda name: "/fixture/tool")
            self.assertEqual(rows[-1]["evidence_type"], "unknown")
            self.assertIsNone(rows[-1]["value"])
            if raw:
                self.assertNotIn(raw, json.dumps(rows))

    def test_missing_tool_and_failure_are_unknown(self):
        self.assertEqual(kde.collect(which=lambda name: None)[-1]["status"], "missing_tool")
        self.assertEqual(kde.collect(lambda argv: ("private", 1), lambda name: "tool")[-1]["status"], "command_error")


if __name__ == "__main__":
    unittest.main()
