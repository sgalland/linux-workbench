import unittest

from workbenchlib.transaction import Action, Status, Transaction


def sample(**changes):
    data = dict(transaction_id="pilot-v1", adapter="fixture", outcomes=("workspace.named_contexts",),
                preconditions=(("count", "1"),), operations=(Action("desktop.create", (("position", 1), ("name", "General"))),),
                backup_keys=("desktop.name.0",), verification=(("count", "4"),),
                rollback=(Action("desktop.remove", (("position", 1),)),))
    data.update(changes)
    return Transaction(**data)


class TransactionTests(unittest.TestCase):
    def test_lifecycle_and_fingerprint(self):
        tx = sample()
        fingerprint = tx.plan_fingerprint()
        for status in (Status.AUTHORIZATION_REQUIRED, Status.AUTHORIZED, Status.BACKUP_CREATED,
                       Status.APPLIED, Status.VERIFICATION_FAILED, Status.ROLLED_BACK):
            tx = tx.transition(status)
            self.assertEqual(tx.plan_fingerprint(), fingerprint)

    def test_invalid_transitions(self):
        with self.assertRaises(ValueError):
            sample().transition(Status.APPLIED)
        with self.assertRaises(ValueError):
            sample().transition(Status.PLANNED)
        with self.assertRaises(ValueError):
            sample().transition(Status.AUTHORIZATION_REQUIRED).transition(Status.AUTHORIZATION_REQUIRED)

    def test_unknown_and_incomplete_block(self):
        with self.assertRaises(ValueError):
            sample(preconditions=(("name", "unknown"),))
        with self.assertRaises(ValueError):
            sample(backup_keys=())

    def test_typed_actions_and_plan_changes(self):
        with self.assertRaises(ValueError):
            Action("; shell", ())
        with self.assertRaises(ValueError):
            Action("desktop.create", (("position", True),))
        self.assertNotEqual(sample().plan_fingerprint(), sample(transaction_id="other-v1").plan_fingerprint())
        self.assertNotEqual(sample().plan_fingerprint(), sample(backup_keys=("other",)).plan_fingerprint())


if __name__ == "__main__":
    unittest.main()
