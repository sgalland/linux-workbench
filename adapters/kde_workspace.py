"""KWin 6.7 virtual desktop transaction logic; backend is injected.

The backend contract corresponds to KWin's VirtualDesktopManager D-Bus
interface and exact Desktops configuration keys. This module never connects
to the live session on its own.
"""

from dataclasses import dataclass
import hashlib
import json
from typing import Protocol

from workbenchlib.backup import Value
from workbenchlib.transaction import Action, Transaction


TARGET = ("Development", "General", "Office", "Creative")
CONFIG_KEYS = ("Number", "Rows", *(f"Id_{n}" for n in range(1, 5)), *(f"Name_{n}" for n in range(1, 5)))
BACKUP_KEYS = ("runtime.id", "runtime.name", "runtime.current", "runtime.rows", *(f"config.{key}" for key in CONFIG_KEYS))


@dataclass(frozen=True)
class Desktop:
    id: str
    name: str


@dataclass(frozen=True)
class State:
    desktops: tuple[Desktop, ...]
    current_id: str
    rows: int

    def __post_init__(self):
        if not self.desktops or any(not d.id or not isinstance(d.name, str) for d in self.desktops):
            raise ValueError("unknown desktop state")
        if len({d.id for d in self.desktops}) != len(self.desktops) or self.current_id not in {d.id for d in self.desktops}:
            raise ValueError("inconsistent desktop state")
        if type(self.rows) is not int or not 1 <= self.rows <= len(self.desktops):
            raise ValueError("invalid desktop rows")

    def digest(self) -> str:
        data = {"desktops": [(d.id, d.name) for d in self.desktops], "current": self.current_id, "rows": self.rows}
        return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


class Backend(Protocol):
    def inspect(self) -> State: ...
    def read_key(self, key: str) -> Value: ...
    def write_key(self, key: str, value: Value) -> None: ...
    def set_name(self, desktop_id: str, name: str) -> None: ...
    def create(self, position: int, name: str) -> None: ...
    def remove(self, desktop_id: str) -> None: ...


def plan(state: State, transaction_id: str) -> Transaction:
    if len(state.desktops) != 1 or state.rows != 1 or state.current_id != state.desktops[0].id:
        raise ValueError("pilot requires one active desktop and one row")
    operations = (Action("desktop.set_name", (("slot", 0), ("name", TARGET[0]))),
                  *(Action("desktop.create", (("position", i), ("name", name))) for i, name in enumerate(TARGET[1:], 1)))
    rollback = (Action("desktop.remove_added", ()), Action("desktop.restore_name", ()), Action("config.restore_keys", ()))
    return Transaction(transaction_id=transaction_id, adapter="kde-kwin-6-7", outcomes=("workspace.named_contexts",),
                       preconditions=(("runtime_sha256", state.digest()), ("kwin_version", "6.7.5")),
                       operations=operations, backup_keys=BACKUP_KEYS,
                       verification=(("names_in_order", "|".join(TARGET)), ("original_id_first", state.desktops[0].id),
                                     ("current_id", state.current_id), ("rows", "1")), rollback=rollback)


def backup_value(backend: Backend, state: State, key: str) -> Value:
    if key not in BACKUP_KEYS:
        raise ValueError("key outside workspace backup scope")
    if key == "runtime.id":
        return Value(True, state.desktops[0].id)
    if key == "runtime.name":
        return Value(True, state.desktops[0].name)
    if key == "runtime.current":
        return Value(True, state.current_id)
    if key == "runtime.rows":
        return Value(True, str(state.rows))
    return backend.read_key(key.removeprefix("config."))


def apply(backend: Backend, state: State) -> None:
    if backend.inspect() != state:
        raise ValueError("pre-state drift")
    original = state.desktops[0]
    backend.set_name(original.id, TARGET[0])
    for position, name in enumerate(TARGET[1:], 1):
        backend.create(position, name)
        observed = backend.inspect()
        if len(observed.desktops) != position + 1 or tuple(d.name for d in observed.desktops) != TARGET[:position + 1] or observed.desktops[0].id != original.id or observed.current_id != original.id or observed.rows != 1:
            raise RuntimeError("KWin desktop creation did not match plan")


def verify(backend: Backend, state: State) -> bool:
    observed = backend.inspect()
    return (tuple(d.name for d in observed.desktops) == TARGET and observed.desktops[0].id == state.desktops[0].id
            and observed.current_id == state.current_id and observed.rows == 1)


def rollback(backend: Backend, values: dict[str, Value]) -> dict[str, object]:
    original_id = values["runtime.id"].value
    original_name = values["runtime.name"].value
    if original_id is None or original_name is None:
        raise ValueError("incomplete runtime backup")
    failed = []
    try:
        observed = backend.inspect()
        if not observed.desktops or observed.desktops[0].id != original_id:
            raise ValueError("original desktop missing")
        for desktop in reversed(observed.desktops[1:]):
            backend.remove(desktop.id)
        backend.set_name(original_id, original_name)
    except Exception:
        failed.append("runtime")
    if not failed:
        for key in CONFIG_KEYS:
            try:
                backend.write_key(key, values[f"config.{key}"])
            except Exception:
                failed.append(f"config.{key}")
    try:
        restored = backend.inspect()
        if len(restored.desktops) != 1 or restored.desktops[0] != Desktop(original_id, original_name) or restored.current_id != values["runtime.current"].value or restored.rows != int(values["runtime.rows"].value):
            failed.append("verification")
        if any(backend.read_key(key) != values[f"config.{key}"] for key in CONFIG_KEYS):
            failed.append("config.verification")
    except Exception:
        failed.append("verification")
    return {"status": "rolled-back" if not failed else "rollback-failed", "failed_keys": failed}
