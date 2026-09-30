"""Validated, adapter-neutral descriptions of a single mutation transaction.

Descriptions contain typed actions, never executable command strings. A driver
must still validate the adapter and pre-state immediately before any mutation.
"""

from dataclasses import dataclass, replace
from enum import StrEnum
import hashlib
import json
import re


class Status(StrEnum):
    PLANNED = "planned"
    AUTHORIZATION_REQUIRED = "authorization-required"
    AUTHORIZED = "authorized"
    BACKUP_CREATED = "backup-created"
    APPLIED = "applied"
    VERIFIED = "verified"
    VERIFICATION_FAILED = "verification-failed"
    ROLLED_BACK = "rolled-back"
    ROLLBACK_FAILED = "rollback-failed"
    ABORTED = "aborted"


TRANSITIONS = {
    Status.PLANNED: {Status.AUTHORIZATION_REQUIRED, Status.ABORTED},
    Status.AUTHORIZATION_REQUIRED: {Status.AUTHORIZED, Status.ABORTED},
    Status.AUTHORIZED: {Status.BACKUP_CREATED, Status.ABORTED},
    Status.BACKUP_CREATED: {Status.APPLIED, Status.ABORTED},
    Status.APPLIED: {Status.VERIFIED, Status.VERIFICATION_FAILED, Status.ROLLED_BACK, Status.ROLLBACK_FAILED},
    Status.VERIFICATION_FAILED: {Status.ROLLED_BACK, Status.ROLLBACK_FAILED},
    Status.ROLLBACK_FAILED: {Status.ROLLED_BACK},
    Status.VERIFIED: {Status.ROLLED_BACK, Status.ROLLBACK_FAILED},
}


@dataclass(frozen=True)
class Action:
    kind: str
    parameters: tuple[tuple[str, str | int], ...]

    def __post_init__(self):
        if not re.fullmatch(r"[a-z][a-z0-9_.]*", self.kind):
            raise ValueError("invalid action kind")
        if len({key for key, _ in self.parameters}) != len(self.parameters):
            raise ValueError("duplicate action parameter")
        if any(not re.fullmatch(r"[a-z][a-z0-9_]*", key) or type(value) not in (str, int)
               for key, value in self.parameters):
            raise ValueError("invalid action parameter")


@dataclass(frozen=True)
class Transaction:
    transaction_id: str
    adapter: str
    outcomes: tuple[str, ...]
    preconditions: tuple[tuple[str, str], ...]
    operations: tuple[Action, ...]
    backup_keys: tuple[str, ...]
    verification: tuple[tuple[str, str], ...]
    rollback: tuple[Action, ...]
    status: Status = Status.PLANNED
    authorization_fingerprint: str | None = None

    def __post_init__(self):
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]{0,95}", self.transaction_id):
            raise ValueError("invalid transaction ID")
        if not re.fullmatch(r"[a-z][a-z0-9-]*", self.adapter):
            raise ValueError("invalid adapter")
        if not self.outcomes or not self.preconditions or not self.operations or not self.backup_keys or not self.verification or not self.rollback:
            raise ValueError("incomplete transaction")
        if len(set(self.backup_keys)) != len(self.backup_keys):
            raise ValueError("duplicate backup key")
        if any(value == "unknown" for _, value in self.preconditions):
            raise ValueError("unknown required precondition")

    def plan_fingerprint(self) -> str:
        material = {
            "schema": 1, "transaction_id": self.transaction_id, "adapter": self.adapter,
            "outcomes": self.outcomes, "preconditions": self.preconditions,
            "operations": [(a.kind, a.parameters) for a in self.operations],
            "backup_keys": self.backup_keys, "verification": self.verification,
            "rollback": [(a.kind, a.parameters) for a in self.rollback],
        }
        return hashlib.sha256(json.dumps(material, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def transition(self, status: Status) -> "Transaction":
        if status not in TRANSITIONS.get(self.status, set()):
            raise ValueError(f"invalid transaction transition: {self.status} -> {status}")
        return replace(self, status=status)
