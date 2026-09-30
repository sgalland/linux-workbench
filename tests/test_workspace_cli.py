from contextlib import redirect_stdout, redirect_stderr
import io
from pathlib import Path
import tempfile
import unittest

from test_workspace_pilot import FakeLive
from workbenchlib.backup import Value
from workbenchlib.workspace_cli import main
from workbenchlib.workspace_pilot import current_plan


class CLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / ".gitignore").write_text(".workbench/\n")
        self.backend = FakeLive()
        self.fp = current_plan(self.backend)[1].plan_fingerprint()

    def call(self, args, check=lambda: None):
        output = io.StringIO()
        with redirect_stdout(output), redirect_stderr(io.StringIO()):
            code = main(args, backend_factory=lambda: self.backend, repo_root=self.root, check_session=check)
        return code, output.getvalue()

    def test_preflight_is_read_only_and_sanitized(self):
        code, output = self.call(["preflight"])
        self.assertEqual(code, 0)
        self.assertIn(self.fp, output)
        self.assertNotIn("fixture-id", output)
        self.assertNotIn("private fixture name", output)
        self.assertFalse((self.root / ".workbench").exists())

    def test_no_auth_wrong_fingerprint_and_noninteractive(self):
        self.assertEqual(self.call(["apply", self.fp])[0], 2)
        self.assertEqual(self.call(["apply", "0" * 64])[0], 2)
        self.assertEqual(self.call(["authorize", self.fp])[0], 2)
        self.assertFalse((self.root / ".workbench" / "authorizations").exists())

    def test_context_and_drift(self):
        self.assertEqual(self.call(["apply", self.fp], check=lambda: (_ for _ in ()).throw(ValueError()))[0], 2)
        self.backend.stage = "surface"
        self.assertEqual(self.call(["preflight"])[0], 2)
        self.backend.stage = None
        self.backend.config["Rows"] = Value(True, "1")
        self.assertEqual(self.call(["apply", self.fp])[0], 2)


if __name__ == "__main__":
    unittest.main()
