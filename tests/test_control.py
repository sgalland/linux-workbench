from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

from adapters.kde_workspace import plan
from test_kde_workspace import Fixture
from workbenchlib.backup import BackupStore
from workbenchlib.control import FixtureAuthorization, authorize_fixture, dry_run, run_fixture
from workbenchlib.transaction import Status


class ControlTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        repo = Path(self.temp.name)
        (repo / ".gitignore").write_text(".workbench/\n")
        self.store = BackupStore(repo)
        self.backend = Fixture()
        self.state = self.backend.inspect()
        self.tx = plan(self.state, "control-v1").transition(Status.AUTHORIZATION_REQUIRED)
        self.auth = authorize_fixture(self.tx, self.state)

    def test_dry_run_does_not_mutate_or_create_backup(self):
        result = dry_run(self.backend, "control-v1")
        self.assertEqual(result["fingerprint"], self.tx.plan_fingerprint())
        self.assertEqual(self.backend.inspect(), self.state)
        self.assertFalse(self.store.root.exists())

    def test_no_wrong_stale_cross_or_changed_plan_authorization(self):
        for auth in (None, replace(self.auth, fingerprint="0" * 64),
                     replace(self.auth, prestate_digest="0" * 64),
                     replace(self.auth, transaction_id="other")):
            with self.assertRaises(ValueError):
                run_fixture(self.backend, self.tx, auth, self.store)
        with self.assertRaises(ValueError):
            run_fixture(self.backend, replace(self.tx, verification=(("changed", "yes"),)), self.auth, self.store)
        self.backend.set_name("fixture-id", "drift")
        with self.assertRaises(ValueError):
            run_fixture(self.backend, self.tx, self.auth, self.store)
        self.assertFalse(self.store.root.exists())

    def test_live_and_duplicate_apply_rejected(self):
        self.backend.fixture_only = False
        with self.assertRaises(ValueError):
            run_fixture(self.backend, self.tx, self.auth, self.store)
        self.backend.fixture_only = True
        with self.assertRaises(ValueError):
            run_fixture(self.backend, self.tx.transition(Status.AUTHORIZED), self.auth, self.store)

    def test_fixture_authorized_apply(self):
        result = run_fixture(self.backend, self.tx, self.auth, self.store)
        self.assertEqual(result["status"], "verified")
        with self.assertRaises(ValueError):
            run_fixture(self.backend, self.tx, self.auth, self.store)

    def test_full_fixture_lifecycle_with_restore(self):
        result = run_fixture(self.backend, self.tx, self.auth, self.store, rollback_after_verify=True)
        self.assertEqual(result["status"], "rolled-back")
        self.assertEqual(result["rollback"]["failed_keys"], [])
        self.assertEqual(self.backend.inspect(), self.state)

    def test_partial_apply_failure_restores_fixture(self):
        self.backend.fail_at = 2
        result = run_fixture(self.backend, self.tx, self.auth, self.store)
        self.assertEqual(result["status"], "rolled-back")
        self.assertEqual(result["rollback"]["failed_keys"], [])
        self.assertEqual(self.backend.inspect(), self.state)


if __name__ == "__main__":
    unittest.main()
