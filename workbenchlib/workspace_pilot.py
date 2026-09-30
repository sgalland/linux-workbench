"""Single-purpose production lifecycle for the reviewed KWin pilot."""

from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import signal

from adapters import kde_workspace as kde
from workbenchlib.backup import BackupStore, Value
from workbenchlib.production_auth import ProductionAuthorizations, TRANSACTION_ID
from workbenchlib.transaction import Status


def _digests(tx):
    return dict(tx.preconditions)["runtime_sha256"], dict(tx.preconditions)["config_sha256"]


def current_plan(backend):
    backend.validate_surface()
    state = backend.inspect()
    if backend.read_key("Id_5").present:
        raise ValueError("unsupported extra desktop config")
    tx = kde.bind_config(kde.plan(state, TRANSACTION_ID), backend).transition(Status.AUTHORIZATION_REQUIRED)
    return state, tx


def _same_prestate(backend, tx):
    state, fresh = current_plan(backend)
    if fresh.plan_fingerprint() != tx.plan_fingerprint():
        raise ValueError("pre-state drift")
    return state


def _prefix(backend, before, length):
    observed = backend.inspect()
    if (len(observed.desktops) != length or observed.desktops[0].id != before.desktops[0].id
            or observed.current_id != before.current_id or observed.rows != 1
            or tuple(d.name for d in observed.desktops) != kde.TARGET[:length]
            or len({d.id for d in observed.desktops}) != length):
        raise RuntimeError("runtime verification failed")
    return observed


def _final_config(backend, observed):
    expected = {"Number": "4", "Rows": "1"}
    for index, desktop in enumerate(observed.desktops, 1):
        expected[f"Id_{index}"] = desktop.id
        expected[f"Name_{index}"] = desktop.name
    if any(backend.read_key(key) != Value(True, value) for key, value in expected.items()):
        raise RuntimeError("config verification failed")
    if backend.read_key("Id_5").present:
        raise RuntimeError("unexpected config scope")


def verify_live(backend, before=None):
    backend.validate_surface()
    observed = backend.inspect()
    if (len(observed.desktops) != 4 or tuple(d.name for d in observed.desktops) != kde.TARGET
            or observed.rows != 1 or observed.current_id != observed.desktops[0].id
            or before is not None and (observed.desktops[0].id != before.desktops[0].id
                                       or observed.current_id != before.current_id)):
        raise RuntimeError("runtime verification failed")
    _final_config(backend, observed)
    return {"status": "verified", "transaction_id": TRANSACTION_ID}


@contextmanager
def _lock(repo_root):
    root = repo_root / ".workbench"
    if root.is_symlink():
        raise ValueError("unsafe workbench directory")
    root.mkdir(mode=0o700, exist_ok=True)
    os.chmod(root, 0o700)
    fd = os.open(root / "workspace-pilot.lock", os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    finally:
        os.close(fd)


def _record(repo_root, result):
    root = repo_root / ".workbench" / "runs"
    if root.is_symlink():
        raise ValueError("unsafe run directory")
    root.mkdir(mode=0o700, exist_ok=True)
    os.chmod(root, 0o700)
    path = root / (TRANSACTION_ID + ".json")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "w") as output:
        json.dump(result, output, sort_keys=True)
        output.flush()
        os.fsync(output.fileno())


def _rollback(backend, store, backup_id, fingerprint):
    values = store.load(backup_id, fingerprint, kde.BACKUP_KEYS)
    original = values["runtime.id"].value
    observed = backend.inspect()
    names = tuple(d.name for d in observed.desktops)
    allowed_names = names == kde.TARGET[:len(observed.desktops)] or (
        len(observed.desktops) == 1 and names == (values["runtime.name"].value,))
    if (not observed.desktops or observed.desktops[0].id != original or observed.current_id != original
            or observed.rows != 1 or len(observed.desktops) > 4
            or not allowed_names):
        raise ValueError("rollback state drift")
    result = kde.rollback(backend, values)
    if result["status"] != "rolled-back":
        raise RuntimeError("rollback verification failed")
    return result


def run(backend, repo_root: Path, fingerprint: str):
    """Consume exact auth and run. Only fake backends may invoke this in Batch 004B tests."""
    with _lock(repo_root):
        before, tx = current_plan(backend)
        if tx.plan_fingerprint() != fingerprint:
            raise ValueError("fingerprint mismatch")
        runtime_digest, config_digest = _digests(tx)
        auth = ProductionAuthorizations(repo_root)
        auth.consume(fingerprint, runtime_digest, config_digest)
        store = BackupStore(repo_root)
        backup_id = None
        mutated = False
        old_term = signal.getsignal(signal.SIGTERM)
        def interrupted(signum, frame):
            raise KeyboardInterrupt("interrupted")
        signal.signal(signal.SIGTERM, interrupted)
        try:
            backup_id = store.create(TRANSACTION_ID, fingerprint, kde.BACKUP_KEYS,
                                     lambda key: kde.backup_value(backend, before, key))
            _same_prestate(backend, tx)
            backend.validate_surface()
            mutated = True  # A mutator may change state before raising.
            backend.set_name(before.desktops[0].id, kde.TARGET[0])
            _prefix(backend, before, 1)
            for position, name in enumerate(kde.TARGET[1:], 1):
                backend.validate_surface()
                backend.create(position, name)
                _prefix(backend, before, position + 1)
            verify_live(backend, before)
            result = {"status": "verified", "transaction_id": TRANSACTION_ID,
                      "fingerprint": fingerprint, "backup_id": backup_id}
        except BaseException as exc:
            category = type(exc).__name__
            if mutated and backup_id is not None:
                try:
                    _rollback(backend, store, backup_id, fingerprint)
                    status = "rolled-back"
                except BaseException:
                    status = "rollback-failed"
            else:
                status = "aborted"
            result = {"status": status, "transaction_id": TRANSACTION_ID,
                      "fingerprint": fingerprint, "backup_id": backup_id,
                      "failure_category": category}
        finally:
            signal.signal(signal.SIGTERM, old_term)
        _record(repo_root, result)
        return result


def explicit_rollback(backend, repo_root: Path, backup_id: str, fingerprint: str):
    with _lock(repo_root):
        backend.validate_surface()
        result = _rollback(backend, BackupStore(repo_root), backup_id, fingerprint)
        public = {"status": result["status"], "transaction_id": TRANSACTION_ID,
                  "fingerprint": fingerprint, "backup_id": backup_id}
        _record(repo_root, public)
        return public
