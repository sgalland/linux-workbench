"""Narrow local backup material for adapter-owned restoration.

No backup contents are returned in exception messages or normal CLI output.
"""

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Callable


@dataclass(frozen=True)
class Value:
    present: bool
    value: str | None = None

    def __post_init__(self):
        if type(self.present) is not bool or (self.present and not isinstance(self.value, str)) or (not self.present and self.value is not None):
            raise ValueError("invalid backup value")


class BackupStore:
    def __init__(self, repo_root: Path):
        self.root = repo_root / ".workbench" / "backups"
        if not (repo_root / ".gitignore").is_file() or ".workbench/" not in (repo_root / ".gitignore").read_text():
            raise ValueError("backup root must be ignored")
        self.repo_root = repo_root

    @staticmethod
    def _id(value: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}", value) or value in {".", ".."}:
            raise ValueError("invalid backup identifier")
        return value

    def _safe_root(self, create: bool):
        for path in (self.repo_root, self.repo_root / ".workbench", self.root):
            if path.is_symlink():
                raise ValueError("symlink in backup path")
            if create and not path.exists():
                path.mkdir(mode=0o700)
            if not path.is_dir():
                raise ValueError("unsafe backup path")
        if create:
            os.chmod(self.repo_root / ".workbench", 0o700)
            os.chmod(self.root, 0o700)

    def create(self, transaction_id: str, fingerprint: str, allowlist: tuple[str, ...],
               reader: Callable[[str], Value]) -> str:
        backup_id = self._id(transaction_id)
        if not re.fullmatch(r"[0-9a-f]{64}", fingerprint):
            raise ValueError("invalid fingerprint")
        if not allowlist or len(set(allowlist)) != len(allowlist) or any(not re.fullmatch(r"[a-zA-Z0-9_.-]+", key) for key in allowlist):
            raise ValueError("invalid backup allowlist")
        self._safe_root(create=True)
        values = {}
        for key in allowlist:
            value = reader(key)
            if not isinstance(value, Value):
                raise ValueError("backup read failed")
            values[key] = {"present": value.present, "value": value.value}
        payload = {"schema": 1, "transaction_id": backup_id, "fingerprint": fingerprint,
                   "keys": list(allowlist), "values": values}
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        envelope = {"payload": payload, "sha256": hashlib.sha256(canonical.encode()).hexdigest()}
        path = self.root / f"{backup_id}.json"
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags, 0o600)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(envelope, stream, sort_keys=True)
                stream.flush()
                os.fsync(stream.fileno())
        except BaseException:
            path.unlink(missing_ok=True)
            raise
        return backup_id

    def load(self, backup_id: str, fingerprint: str, allowlist: tuple[str, ...]) -> dict[str, Value]:
        self._safe_root(create=False)
        path = self.root / f"{self._id(backup_id)}.json"
        if path.is_symlink() or not path.is_file() or path.stat().st_mode & 0o077:
            raise ValueError("unsafe backup file")
        try:
            envelope = json.loads(path.read_text(encoding="utf-8"))
            payload = envelope["payload"]
            canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
            if hashlib.sha256(canonical.encode()).hexdigest() != envelope["sha256"]:
                raise ValueError("backup integrity failure")
            if payload["schema"] != 1 or payload["transaction_id"] != backup_id or payload["fingerprint"] != fingerprint or payload["keys"] != list(allowlist) or set(payload["values"]) != set(allowlist):
                raise ValueError("backup identity failure")
            return {key: Value(**payload["values"][key]) for key in allowlist}
        except (KeyError, TypeError, json.JSONDecodeError, UnicodeError) as exc:
            raise ValueError("corrupt backup") from exc

    def restore(self, backup_id: str, fingerprint: str, allowlist: tuple[str, ...],
                writer: Callable[[str, Value], None]) -> dict[str, object]:
        values = self.load(backup_id, fingerprint, allowlist)
        failed = []
        for key in allowlist:
            try:
                writer(key, values[key])
            except Exception:
                failed.append(key)
        return {"status": "rolled-back" if not failed else "rollback-failed", "failed_keys": failed}
