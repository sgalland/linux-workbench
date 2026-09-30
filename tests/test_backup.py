import os
from pathlib import Path
import tempfile
import unittest

from workbenchlib.backup import BackupStore, Value


class BackupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        (self.repo / ".gitignore").write_text(".workbench/\n")
        self.store = BackupStore(self.repo)
        self.fp = "a" * 64
        self.keys = ("desktop.0", "desktop.1")
        self.values = {"desktop.0": Value(True, "private name"), "desktop.1": Value(False)}

    def create(self):
        return self.store.create("pilot-v1", self.fp, self.keys, self.values.__getitem__)

    def test_private_permissions_and_missing_value(self):
        self.create()
        self.assertEqual(self.store.load("pilot-v1", self.fp, self.keys), self.values)
        self.assertEqual((self.store.root.stat().st_mode & 0o777), 0o700)
        self.assertEqual(((self.store.root / "pilot-v1.json").stat().st_mode & 0o777), 0o600)

    def test_double_restore_is_idempotent(self):
        self.create()
        restored = {}
        for _ in range(2):
            self.assertEqual(self.store.restore("pilot-v1", self.fp, self.keys, restored.__setitem__)["status"], "rolled-back")
        self.assertEqual(restored, self.values)

    def test_partial_failure_and_read_failure(self):
        with self.assertRaises(KeyError):
            self.store.create("pilot-v1", self.fp, self.keys, lambda key: self.values[key] if key == "desktop.0" else self.values["missing"])
        self.create()
        result = self.store.restore("pilot-v1", self.fp, self.keys,
                                    lambda key, value: (_ for _ in ()).throw(OSError()) if key == "desktop.1" else None)
        self.assertEqual(result, {"status": "rollback-failed", "failed_keys": ["desktop.1"]})

    def test_corruption_and_identity(self):
        self.create()
        with self.assertRaises(ValueError):
            self.store.load("pilot-v1", "b" * 64, self.keys)
        (self.store.root / "pilot-v1.json").write_text("broken")
        with self.assertRaises(ValueError):
            self.store.load("pilot-v1", self.fp, self.keys)

    def test_path_escape_and_symlinks(self):
        with self.assertRaises(ValueError):
            self.store.create("../escape", self.fp, self.keys, self.values.__getitem__)
        (self.repo / ".workbench").symlink_to(self.repo / "elsewhere")
        with self.assertRaises(ValueError):
            self.create()

    def test_load_rejects_backup_file_symlink(self):
        self.create()
        path = self.store.root / "pilot-v1.json"
        target = self.store.root / "target.json"
        path.rename(target)
        path.symlink_to(target)
        with self.assertRaises(ValueError):
            self.store.load("pilot-v1", self.fp, self.keys)


if __name__ == "__main__":
    unittest.main()
