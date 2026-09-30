import json
import subprocess
import unittest

from adapters.kde_live import KWinBackend, EXPECTED
from workbenchlib.backup import Value


SURFACE = "\n".join(f"{name} {kind} {ins or '-'} {outs or '-'}" for name, (kind, ins, outs) in EXPECTED.items())


class Runner:
    def __init__(self):
        self.calls = []
        self.version = "kwin 6.7.5\n"
        self.surface = SURFACE
        self.properties = {"desktops": ("a(uss)", [[0, "original", "private"]]),
                           "count": ("u", 1), "current": ("s", "original"), "rows": ("u", 1)}
        self.config = {}
        self.fail = False

    def __call__(self, argv):
        self.calls.append(argv)
        if self.fail:
            raise subprocess.CalledProcessError(1, argv)
        if argv[:2] == ["kwin_wayland", "--version"]:
            return self.version
        if "introspect" in argv:
            return self.surface
        if "get-property" in argv:
            signature, data = self.properties[argv[-1]]
            return json.dumps({"type": signature, "data": data})
        if argv[0] == "kreadconfig6":
            return self.config.get(argv[argv.index("--key") + 1], argv[-1]) + "\n"
        if argv[0] == "kwriteconfig6":
            key = argv[argv.index("--key") + 1]
            if argv[-1] == "--delete":
                self.config.pop(key, None)
            else:
                self.config[key] = argv[-1]
            return ""
        return ""


class LiveBackendTests(unittest.TestCase):
    def setUp(self):
        self.runner = Runner()
        self.backend = KWinBackend(self.runner, "/fake/kwinrc")

    def test_inspect_surface_and_typed_mutators(self):
        self.backend.validate_surface()
        self.assertEqual(self.backend.inspect().desktops[0].id, "original")
        self.backend.set_name("original", "Development")
        self.backend.create(1, "General")
        self.backend.remove("new-id")
        self.assertEqual([call[6:] for call in self.runner.calls[-3:]],
                         [["setDesktopName", "ss", "original", "Development"],
                          ["createDesktop", "us", "1", "General"], ["removeDesktop", "s", "new-id"]])
        self.assertTrue(all(call[1] == "--user" for call in self.runner.calls if call[0] == "busctl"))

    def test_malformed_and_failed(self):
        self.runner.properties["count"] = ("u", 2)
        with self.assertRaises(ValueError):
            self.backend.inspect()
        self.runner.properties["count"] = ("s", 1)
        with self.assertRaises(ValueError):
            self.backend.inspect()
        self.runner.fail = True
        with self.assertRaises(ValueError):
            self.backend.validate_surface()

    def test_desktops_wire_signature_is_exact(self):
        self.backend.validate_surface()
        self.assertEqual(self.backend.inspect().desktops[0].id, "original")
        for signature in ("a(iss)", "a(sss)", "a(uss)s"):
            with self.subTest(signature=signature):
                self.runner.properties["desktops"] = (signature, [[0, "original", "private"]])
                with self.assertRaises(ValueError):
                    self.backend.inspect()

    def test_desktops_position_validation(self):
        for positions in ((-1,), (True,), (1,), (0, 2)):
            with self.subTest(positions=positions):
                self.runner.properties["desktops"] = ("a(uss)",
                    [[position, f"id-{i}", f"name-{i}"] for i, position in enumerate(positions)])
                self.runner.properties["count"] = ("u", len(positions))
                self.runner.properties["current"] = ("s", "id-0")
                with self.assertRaises(ValueError):
                    self.backend.inspect()

    def test_other_payload_validation(self):
        for rows, count, current in (([[0, "id", 4]], 1, "id"),
                                     ([[0, "id", "name"]], 2, "id"),
                                     ([[0, "id", "name"]], 1, "unknown")):
            with self.subTest(rows=rows, count=count, current=current):
                self.runner.properties["desktops"] = ("a(uss)", rows)
                self.runner.properties["count"] = ("u", count)
                self.runner.properties["current"] = ("s", current)
                with self.assertRaises(ValueError):
                    self.backend.inspect()

    def test_drifted_surface(self):
        self.runner.version = "kwin 6.7.6"
        with self.assertRaises(ValueError):
            self.backend.validate_surface()
        self.runner.version = "kwin 6.7.5"
        for member in EXPECTED:
            self.runner.surface = SURFACE.replace(member + " ", "missing ")
            with self.assertRaises(ValueError):
                self.backend.validate_surface()
        for member, (kind, ins, outs) in EXPECTED.items():
            original = f"{member} {kind} {ins or '-'} {outs or '-'}"
            changed = f"{member} {kind} changed {outs or '-'}"
            self.runner.surface = SURFACE.replace(original, changed)
            with self.subTest(member=member), self.assertRaises(ValueError):
                self.backend.validate_surface()
            self.runner.surface = SURFACE.replace(original, f"{member} method {ins or '-'} s")
            with self.subTest(member=member, field="kind-or-return"), self.assertRaises(ValueError):
                self.backend.validate_surface()

    def test_config_present_absent_and_allowlist(self):
        self.assertEqual(self.backend.read_key("Rows"), Value(False))
        self.backend.write_key("Rows", Value(True, "1"))
        self.assertEqual(self.backend.read_key("Rows"), Value(True, "1"))
        self.backend.write_key("Rows", Value(False))
        self.assertEqual(self.backend.read_key("Rows"), Value(False))
        with self.assertRaises(ValueError):
            self.backend.write_key("Plugins", Value(True, "x"))
        with self.assertRaises(ValueError):
            self.backend.create(0, "General")
