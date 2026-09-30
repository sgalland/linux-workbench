"""Private, single-use authorization for the one KWin workspace pilot."""

import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import stat
import sys
import time

TRANSACTION_ID = "kde-four-workspaces-v1"
SCOPE = "kwin-6.7.5-four-workspaces-v1"
TTL_SECONDS = 900
HEX = re.compile(r"[0-9a-f]{64}\Z")


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


class ProductionAuthorizations:
    def __init__(self, repo_root: Path, *, clock=time.time):
        self.repo_root = repo_root
        self.root = repo_root / ".workbench" / "authorizations"
        self.clock = clock
        if ".workbench/" not in (repo_root / ".gitignore").read_text():
            raise ValueError("authorization root must be ignored")

    def _directory(self, create=True):
        for path in (self.repo_root, self.repo_root / ".workbench", self.root):
            if path.is_symlink():
                raise ValueError("authorization path symlink")
            if create and not path.exists():
                path.mkdir(mode=0o700)
            if not path.is_dir():
                raise ValueError("unsafe authorization path")
        if create:
            os.chmod(self.repo_root / ".workbench", 0o700)
            os.chmod(self.root, 0o700)

    def _path(self, fingerprint):
        if not isinstance(fingerprint, str) or not HEX.fullmatch(fingerprint):
            raise ValueError("invalid fingerprint")
        return self.root / f"{fingerprint}.json"

    def _key(self, create):
        path = self.root / "integrity.key"
        if create and not path.exists():
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
            with os.fdopen(fd, "wb") as output:
                output.write(secrets.token_bytes(32))
                output.flush()
                os.fsync(output.fileno())
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(fd, "rb") as source:
            if not stat.S_ISREG(os.fstat(source.fileno()).st_mode) or os.fstat(source.fileno()).st_mode & 0o077:
                raise ValueError("unsafe authorization key")
            key = source.read()
        if len(key) != 32:
            raise ValueError("invalid authorization key")
        return key

    def issue(self, *, fingerprint, runtime_digest, config_digest, terminal=None):
        """Only an attached human terminal can issue. `terminal` is test injection."""
        terminal = terminal or sys.stdin
        if not terminal.isatty() or not sys.stdout.isatty() and terminal is sys.stdin:
            raise ValueError("interactive TTY required")
        for digest in (fingerprint, runtime_digest, config_digest):
            if not isinstance(digest, str) or not HEX.fullmatch(digest):
                raise ValueError("invalid authorization digest")
        print(f"Authorize {TRANSACTION_ID} fingerprint {fingerprint}; expires in 15 minutes.\n"
              "Enter the transaction ID, then the fingerprint on separate lines:", file=sys.stderr)
        if terminal.readline().strip() != TRANSACTION_ID:
            raise ValueError("transaction confirmation mismatch")
        if terminal.readline().strip() != fingerprint:
            raise ValueError("fingerprint confirmation mismatch")
        self._directory()
        path = self._path(fingerprint)
        if path.exists() or path.with_suffix(".consumed").exists():
            raise ValueError("authorization already exists or was consumed")
        payload = {"schema": 1, "transaction_id": TRANSACTION_ID, "scope": SCOPE,
                   "fingerprint": fingerprint, "runtime_digest": runtime_digest,
                   "config_digest": config_digest, "expires_at": int(self.clock()) + TTL_SECONDS,
                   "nonce": secrets.token_hex(16)}
        mac = hmac.new(self._key(True), _canonical(payload), hashlib.sha256).hexdigest()
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
        with os.fdopen(fd, "w") as output:
            json.dump({"payload": payload, "hmac": mac}, output, sort_keys=True)
            output.flush()
            os.fsync(output.fileno())

    def validate(self, fingerprint, runtime_digest, config_digest):
        self._directory(False)
        path = self._path(fingerprint)
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(fd) as source:
            if not stat.S_ISREG(os.fstat(source.fileno()).st_mode) or os.fstat(source.fileno()).st_mode & 0o077:
                raise ValueError("unsafe authorization file")
            envelope = json.load(source)
        payload = envelope["payload"]
        if not hmac.compare_digest(hmac.new(self._key(False), _canonical(payload), hashlib.sha256).hexdigest(), envelope["hmac"]):
            raise ValueError("authorization integrity failure")
        if (payload["schema"] != 1 or payload["transaction_id"] != TRANSACTION_ID or payload["scope"] != SCOPE
                or payload["fingerprint"] != fingerprint or payload["runtime_digest"] != runtime_digest
                or payload["config_digest"] != config_digest or self.clock() > payload["expires_at"]):
            raise ValueError("authorization stale or mismatched")
        return payload

    def consume(self, fingerprint, runtime_digest, config_digest):
        self.validate(fingerprint, runtime_digest, config_digest)
        path = self._path(fingerprint)
        consumed = path.with_suffix(".consumed")
        if consumed.exists():
            raise ValueError("authorization consumed")
        os.link(path, consumed, follow_symlinks=False)
        path.unlink()
