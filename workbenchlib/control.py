"""Fixture-only execution gate for the Batch 004 mutation design.

No production authorization issuer or live backend is exposed here. A later
live pilot needs a separately reviewed, human-issued authorization channel.
"""

from dataclasses import dataclass

from adapters import kde_workspace as kde
from workbenchlib.backup import BackupStore
from workbenchlib.transaction import Status, Transaction


@dataclass(frozen=True)
class FixtureAuthorization:
    transaction_id: str
    fingerprint: str
    prestate_digest: str
    scope: str = "fixture-only"


def authorize_fixture(tx: Transaction, state: kde.State) -> FixtureAuthorization:
    if tx.status != Status.AUTHORIZATION_REQUIRED or tx.preconditions[0] != ("runtime_sha256", state.digest()) or not any(key == "config_sha256" for key, _ in tx.preconditions):
        raise ValueError("plan is not ready for fixture authorization")
    return FixtureAuthorization(tx.transaction_id, tx.plan_fingerprint(), state.digest())


def dry_run(backend: kde.Backend, transaction_id: str) -> dict[str, object]:
    state = backend.inspect()
    tx = kde.bind_config(kde.plan(state, transaction_id), backend).transition(Status.AUTHORIZATION_REQUIRED)
    # Check exactly the planned backup scope without returning private values.
    for key in tx.backup_keys:
        kde.backup_value(backend, state, key)
    return {"transaction_id": tx.transaction_id, "fingerprint": tx.plan_fingerprint(),
            "status": tx.status.value, "backup_keys": list(tx.backup_keys),
            "target_names": list(kde.TARGET), "prestate_digest": state.digest(),
            "operations": [action.kind for action in tx.operations],
            "verification": [name for name, _ in tx.verification]}


def run_fixture(backend: kde.Backend, tx: Transaction, auth: FixtureAuthorization,
                store: BackupStore, *, rollback_after_verify: bool = False) -> dict[str, object]:
    if getattr(backend, "fixture_only", False) is not True:
        raise ValueError("Batch 004 cannot apply to a live backend")
    if tx.status != Status.AUTHORIZATION_REQUIRED:
        raise ValueError("duplicate or unplanned apply")
    if not isinstance(auth, FixtureAuthorization) or auth.scope != "fixture-only":
        raise ValueError("fixture authorization required")
    state = backend.inspect()
    current_config = kde.bind_config(kde.plan(state, tx.transaction_id), backend).preconditions[-1]
    if (auth.transaction_id != tx.transaction_id or auth.fingerprint != tx.plan_fingerprint()
            or auth.prestate_digest != state.digest() or tx.preconditions[0] != ("runtime_sha256", state.digest())
            or current_config not in tx.preconditions):
        raise ValueError("authorization or pre-state mismatch")
    tx = tx.transition(Status.AUTHORIZED)
    fingerprint = tx.plan_fingerprint()
    backup_id = store.create(tx.transaction_id, fingerprint, tx.backup_keys,
                             lambda key: kde.backup_value(backend, state, key))
    tx = tx.transition(Status.BACKUP_CREATED)
    try:
        kde.apply(backend, state)
        tx = tx.transition(Status.APPLIED)
        if not kde.verify(backend, state):
            tx = tx.transition(Status.VERIFICATION_FAILED)
            raise RuntimeError("fixture verification failed")
        tx = tx.transition(Status.VERIFIED)
    except Exception:
        # A backend may have changed state before raising. Roll back from the
        # backup even when the apply transition itself did not complete.
        if tx.status == Status.BACKUP_CREATED:
            tx = tx.transition(Status.APPLIED).transition(Status.VERIFICATION_FAILED)
        values = store.load(backup_id, fingerprint, tx.backup_keys)
        result = kde.rollback(backend, values)
        tx = tx.transition(Status.ROLLED_BACK if result["status"] == "rolled-back" else Status.ROLLBACK_FAILED)
        return {"status": tx.status.value, "backup_id": backup_id, "rollback": result}
    if rollback_after_verify:
        values = store.load(backup_id, fingerprint, tx.backup_keys)
        result = kde.rollback(backend, values)
        tx = tx.transition(Status.ROLLED_BACK if result["status"] == "rolled-back" else Status.ROLLBACK_FAILED)
        return {"status": tx.status.value, "backup_id": backup_id, "rollback": result}
    return {"status": tx.status.value, "backup_id": backup_id}
