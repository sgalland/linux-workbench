"""Operator commands for the single reviewed workspace transaction."""

import json
import os
from pathlib import Path
import sys

from adapters.kde_live import KWinBackend
from adapters.kde_workspace import BACKUP_KEYS, TARGET
from workbenchlib.backup import BackupStore
from workbenchlib.inspect import REPO_ROOT
from workbenchlib.production_auth import ProductionAuthorizations, TRANSACTION_ID
from workbenchlib.workspace_pilot import current_plan, explicit_rollback, run, verify_live


HELP = ("Usage: ./workbench workspace-pilot preflight | authorize <fingerprint> | "
        "apply <fingerprint> | verify | rollback <backup-id>\n"
        "Preflight and this batch are not authorization. Authorize needs an interactive human TTY.")


def _session():
    if os.geteuid() == 0 or "KDE" not in os.environ.get("XDG_CURRENT_DESKTOP", "").upper().split(":"):
        raise ValueError("unsupported user KDE session")
    if not os.environ.get("DBUS_SESSION_BUS_ADDRESS"):
        raise ValueError("missing user session bus")


def _report(backend):
    state, tx = current_plan(backend)
    return {"status": "authorization-required", "transaction_id": TRANSACTION_ID,
            "fingerprint": tx.plan_fingerprint(), "runtime_digest": state.digest(),
            "config_digest": dict(tx.preconditions)["config_sha256"], "kwin_version": "6.7.5",
            "interface": "verified", "desktop_count": len(state.desktops), "rows": state.rows,
            "target_names": list(TARGET), "backup_keys": list(BACKUP_KEYS)}


def main(args, *, backend_factory=KWinBackend, repo_root=REPO_ROOT, check_session=_session):
    args = list(args)
    if not args or args[0] not in {"preflight", "authorize", "apply", "verify", "rollback"}:
        print(HELP, file=sys.stderr)
        return 2
    command, *tail = args
    if len(tail) != (0 if command in {"preflight", "verify"} else 1):
        print(HELP, file=sys.stderr)
        return 2
    try:
        check_session()
        backend = backend_factory()
        if command == "preflight":
            result = _report(backend)
        elif command == "authorize":
            result = _report(backend)
            if tail[0] != result["fingerprint"]:
                raise ValueError("fingerprint mismatch")
            ProductionAuthorizations(repo_root).issue(fingerprint=tail[0],
                runtime_digest=result["runtime_digest"], config_digest=result["config_digest"])
            result = {"status": "authorized", "transaction_id": TRANSACTION_ID, "fingerprint": tail[0]}
        elif command == "apply":
            result = run(backend, repo_root, tail[0])
        elif command == "verify":
            result = verify_live(backend)
        else:
            path = repo_root / ".workbench" / "runs" / (TRANSACTION_ID + ".json")
            if path.is_symlink():
                raise ValueError("unsafe result record")
            record = json.loads(path.read_text())
            if record.get("transaction_id") != TRANSACTION_ID or record.get("backup_id") != tail[0] or record.get("status") not in {"verified", "rollback-failed"}:
                raise ValueError("no matching pilot run")
            if record["status"] == "verified":
                verify_live(backend)
            result = explicit_rollback(backend, repo_root, tail[0], record["fingerprint"])
        print(json.dumps(result, sort_keys=True))
        return 0 if result["status"] in {"authorization-required", "authorized", "verified", "rolled-back"} else 1
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"workspace-pilot: {type(exc).__name__}: operation refused", file=sys.stderr)
        return 2
