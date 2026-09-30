import unittest

from adapters.kde_workspace import BACKUP_KEYS, CONFIG_KEYS, Desktop, State, TARGET, apply, backup_value, plan, rollback, verify
from workbenchlib.backup import Value


class Fixture:
    fixture_only = True
    def __init__(self):
        self.desktops = [Desktop("fixture-id", "private fixture name")]
        self.current = "fixture-id"
        self.rows = 1
        self.config = {key: Value(False) for key in CONFIG_KEYS}
        self.fail_at = None

    def inspect(self):
        return State(tuple(self.desktops), self.current, self.rows)

    def read_key(self, key):
        return self.config[key]

    def write_key(self, key, value):
        self.config[key] = value

    def set_name(self, desktop_id, name):
        self.desktops = [Desktop(d.id, name if d.id == desktop_id else d.name) for d in self.desktops]
        self.config["Name_1"] = Value(True, name)

    def create(self, position, name):
        if self.fail_at == position:
            raise OSError("injected failure")
        self.desktops.insert(position, Desktop(f"fixture-new-{position}", name))
        self.config["Number"] = Value(True, str(len(self.desktops)))
        self.config[f"Name_{position+1}"] = Value(True, name)
        self.config[f"Id_{position+1}"] = Value(True, f"fixture-new-{position}")

    def remove(self, desktop_id):
        self.desktops = [d for d in self.desktops if d.id != desktop_id]
        self.config["Number"] = Value(True, str(len(self.desktops)))


class WorkspaceTests(unittest.TestCase):
    def test_apply_verify_rollback(self):
        backend = Fixture()
        before = backend.inspect()
        tx = plan(before, "fixture-v1")
        self.assertEqual(tx.adapter, "kde-kwin-6-7")
        values = {key: backup_value(backend, before, key) for key in BACKUP_KEYS}
        apply(backend, before)
        self.assertTrue(verify(backend, before))
        self.assertEqual(tuple(d.name for d in backend.inspect().desktops), TARGET)
        self.assertEqual(rollback(backend, values)["status"], "rolled-back")
        self.assertEqual(backend.inspect(), before)
        self.assertEqual(backend.config, {key: Value(False) for key in CONFIG_KEYS})
        self.assertEqual(rollback(backend, values)["status"], "rolled-back")

    def test_partial_failure_rolls_back(self):
        backend = Fixture()
        before = backend.inspect()
        values = {key: backup_value(backend, before, key) for key in BACKUP_KEYS}
        backend.fail_at = 2
        with self.assertRaises(OSError):
            apply(backend, before)
        self.assertEqual(rollback(backend, values)["status"], "rolled-back")
        self.assertEqual(backend.inspect(), before)

    def test_drift_and_unknown_block(self):
        backend = Fixture()
        before = backend.inspect()
        backend.set_name("fixture-id", "drift")
        with self.assertRaises(ValueError):
            apply(backend, before)
        with self.assertRaises(ValueError):
            plan(State((Desktop("a", "a"), Desktop("b", "b")), "a", 1), "wrong")


if __name__ == "__main__":
    unittest.main()
