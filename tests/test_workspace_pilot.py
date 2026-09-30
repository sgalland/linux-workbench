import io
from pathlib import Path
import tempfile
import unittest

from adapters.kde_workspace import CONFIG_KEYS, Desktop, State
from test_kde_workspace import Fixture
from workbenchlib.backup import Value
from workbenchlib.production_auth import ProductionAuthorizations, TRANSACTION_ID
from workbenchlib.workspace_pilot import current_plan, run, verify_live
from workbenchlib.workspace_pilot import _lock


class Terminal(io.StringIO):
    def isatty(self):
        return True


class FakeLive(Fixture):
    fixture_only = False
    def __init__(self):
        super().__init__()
        self.stage = None
        self.mutations = 0
        self.name4_reads = 0
        self.rollback_failure = False

    def validate_surface(self):
        if self.stage == "surface":
            raise ValueError("unsupported surface")

    def read_key(self, key):
        if key == "Id_5":
            return Value(False)
        if self.stage == "final-verify" and len(self.desktops) == 4 and key == "Number":
            return Value(True, "99")
        if self.stage == "backup" and key == "Name_4":
            self.name4_reads += 1
            if self.name4_reads == 2:
                raise OSError("backup failure")
        return super().read_key(key)

    def set_name(self, desktop_id, name):
        if self.stage == "rename" and name == "Development":
            raise OSError("rename failed")
        super().set_name(desktop_id, name)
        self.mutations += 1
        if self.stage == "after-rename" and name == "Development":
            raise OSError("partial rename")

    def create(self, position, name):
        super().create(position, name)
        self.mutations += 1
        if self.stage == f"after-create-{position}":
            raise OSError("partial create")
        if self.stage == "interruption" and position == 2:
            raise KeyboardInterrupt("injected interrupt")
        if position == 3:
            self.config["Rows"] = Value(True, "1")
            self.config["Id_1"] = Value(True, self.desktops[0].id)
            self.config["Name_1"] = Value(True, self.desktops[0].name)

    def remove(self, desktop_id):
        if self.rollback_failure:
            raise OSError("rollback failed")
        super().remove(desktop_id)


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / ".gitignore").write_text(".workbench/\n")
        self.backend = FakeLive()
        self.before = self.backend.inspect()
        self.fp = current_plan(self.backend)[1].plan_fingerprint()

    def authorize(self):
        _, tx = current_plan(self.backend)
        digests = dict(tx.preconditions)
        ProductionAuthorizations(self.root).issue(fingerprint=self.fp,
            runtime_digest=digests["runtime_sha256"], config_digest=digests["config_sha256"],
            terminal=Terminal(TRANSACTION_ID + "\n" + self.fp + "\n"))

    def test_success_consumed_and_verify(self):
        self.authorize()
        result = run(self.backend, self.root, self.fp)
        self.assertEqual(result["status"], "verified")
        self.assertEqual(verify_live(self.backend)["status"], "verified")
        with self.assertRaises(ValueError):
            run(self.backend, self.root, self.fp)

    def test_no_auth_drift_and_surface(self):
        with self.assertRaises(ValueError):
            run(self.backend, self.root, self.fp)
        self.assertEqual(self.backend.mutations, 0)
        self.authorize()
        self.backend.config["Rows"] = Value(True, "1")
        with self.assertRaises(ValueError):
            run(self.backend, self.root, self.fp)
        self.assertEqual(self.backend.mutations, 0)
        self.backend.config["Rows"] = Value(False)
        self.backend.stage = "surface"
        with self.assertRaises(ValueError):
            run(self.backend, self.root, self.fp)

    def test_failure_injections(self):
        for stage, status in (("backup", "aborted"), ("rename", "rolled-back"),
                              ("after-rename", "rolled-back"),
                              ("after-create-1", "rolled-back"),
                              ("after-create-2", "rolled-back"),
                              ("after-create-3", "rolled-back"),
                              ("final-verify", "rolled-back"),
                              ("interruption", "rolled-back")):
            with self.subTest(stage=stage):
                self.setUp()
                self.authorize()
                self.backend.stage = stage
                result = run(self.backend, self.root, self.fp)
                self.assertEqual(result["status"], status)
                if status == "rolled-back":
                    self.assertEqual(self.backend.inspect(), self.before)

    def test_rollback_failure_and_concurrency(self):
        self.authorize()
        with _lock(self.root):
            with self.assertRaises(BlockingIOError):
                run(self.backend, self.root, self.fp)
        self.backend.stage = "after-create-1"
        self.backend.rollback_failure = True
        result = run(self.backend, self.root, self.fp)
        self.assertEqual(result["status"], "rollback-failed")
        self.assertEqual(result["failure_category"], "OSError")


if __name__ == "__main__":
    unittest.main()
