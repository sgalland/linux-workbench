import io
from pathlib import Path
import tempfile
import unittest

from workbenchlib.production_auth import ProductionAuthorizations, TRANSACTION_ID


class Terminal(io.StringIO):
    def isatty(self):
        return True


class AuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / ".gitignore").write_text(".workbench/\n")
        self.store = ProductionAuthorizations(self.root, clock=lambda: 100)
        self.fp, self.runtime, self.config = "a" * 64, "b" * 64, "c" * 64

    def issue(self):
        self.store.issue(fingerprint=self.fp, runtime_digest=self.runtime, config_digest=self.config,
                         terminal=Terminal(TRANSACTION_ID + "\n" + self.fp + "\n"))

    def test_issue_validate_consume(self):
        self.issue()
        self.assertEqual(self.store.validate(self.fp, self.runtime, self.config)["scope"], "kwin-6.7.5-four-workspaces-v1")
        self.assertEqual((self.store.root.stat().st_mode & 0o777), 0o700)
        self.assertEqual(((self.store.root / (self.fp + ".json")).stat().st_mode & 0o777), 0o600)
        self.store.consume(self.fp, self.runtime, self.config)
        with self.assertRaises((ValueError, OSError)):
            self.store.validate(self.fp, self.runtime, self.config)
        with self.assertRaises(ValueError):
            self.issue()

    def test_confirmation_and_drift(self):
        with self.assertRaises(ValueError):
            self.store.issue(fingerprint=self.fp, runtime_digest=self.runtime, config_digest=self.config,
                             terminal=io.StringIO(TRANSACTION_ID + "\n" + self.fp + "\n"))
        for answer in ("wrong\n" + self.fp + "\n", TRANSACTION_ID + "\nwrong\n"):
            with self.assertRaises(ValueError):
                self.store.issue(fingerprint=self.fp, runtime_digest=self.runtime, config_digest=self.config,
                                 terminal=Terminal(answer))
        self.issue()
        for args in (("d" * 64, self.runtime, self.config), (self.fp, "d" * 64, self.config),
                     (self.fp, self.runtime, "d" * 64)):
            with self.assertRaises((ValueError, OSError)):
                self.store.validate(*args)
        self.store.clock = lambda: 100 + 901
        with self.assertRaises(ValueError):
            self.store.validate(self.fp, self.runtime, self.config)

    def test_integrity(self):
        self.issue()
        path = self.store.root / (self.fp + ".json")
        content = path.read_text().replace(self.runtime, "d" * 64)
        path.write_text(content)
        with self.assertRaises(ValueError):
            self.store.validate(self.fp, self.runtime, self.config)
