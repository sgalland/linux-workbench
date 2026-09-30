"""Narrow read-only KWin 6.7 probe; private result stays in ignored backups.

This module contains no D-Bus Set or method call and no KConfig write.
"""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import secrets
import subprocess

from adapters.kde_workspace import CONFIG_KEYS, Desktop, State
from workbenchlib.backup import BackupStore, Value
from workbenchlib.control import dry_run
from workbenchlib.inspect import REPO_ROOT


SERVICE = "org.kde.KWin"
OBJECT = "/VirtualDesktopManager"
INTERFACE = "org.kde.KWin.VirtualDesktopManager"


def _run(argv):
    result = subprocess.run(argv, capture_output=True, text=True, timeout=8, check=True)
    return result.stdout


def _property(name):
    if name not in {"desktops", "current", "rows", "count"}:
        raise ValueError("property outside probe allowlist")
    return json.loads(_run(["busctl", "--user", "--json=short", "get-property", SERVICE, OBJECT, INTERFACE, name]))["data"]


def _config_value(key):
    if key not in CONFIG_KEYS:
        raise ValueError("key outside probe allowlist")
    sentinels = ["WORKBENCH_ABSENT_" + secrets.token_hex(16) for _ in range(2)]
    outputs = []
    for sentinel in sentinels:
        outputs.append(_run(["kreadconfig6", "--file", str(Path.home() / ".config/kwinrc"),
                             "--group", "Desktops", "--key", key, "--default", sentinel]).removesuffix("\n"))
    if outputs == sentinels:
        return Value(False)
    if outputs[0] == outputs[1] and outputs[0] not in sentinels:
        return Value(True, outputs[0])
    raise ValueError("ambiguous config presence")


def collect():
    desktop_rows = _property("desktops")
    count = _property("count")
    current = _property("current")
    rows = _property("rows")
    if not isinstance(desktop_rows, list) or any(not isinstance(row, list) or len(row) != 3 or type(row[0]) is not int or type(row[1]) is not str or type(row[2]) is not str for row in desktop_rows):
        raise ValueError("unexpected KWin desktop property")
    if [row[0] for row in desktop_rows] != list(range(len(desktop_rows))) or count != len(desktop_rows):
        raise ValueError("inconsistent KWin desktop property")
    state = State(tuple(Desktop(row[1], row[2]) for row in desktop_rows), current, rows)
    config = {key: _config_value(key) for key in CONFIG_KEYS}
    version = _run(["kwin_wayland", "--version"]).strip()
    if version != "kwin 6.7.5":
        raise ValueError("unsupported KWin version")
    return state, config, version


def save_private(state, config, version):
    store = BackupStore(REPO_ROOT)
    store._safe_root(create=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = store.root / f"live-pilot-prestate-{stamp}.json"
    content = {"schema": 1, "version": version, "desktops": [vars(d) for d in state.desktops],
               "current": state.current_id, "rows": state.rows,
               "config": {key: vars(value) for key, value in config.items()}}
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as output:
        json.dump(content, output, ensure_ascii=False)
        output.flush()
        os.fsync(output.fileno())
    return path


class ReadOnlyBackend:
    def __init__(self, state, config):
        self.state = state
        self.config = config

    def inspect(self):
        return self.state

    def read_key(self, key):
        return self.config[key]


def main():
    state, config, version = collect()
    save_private(state, config, version)
    report = dry_run(ReadOnlyBackend(state, config), "kde-four-workspaces-v1")
    print(json.dumps({"version": version, "desktop_count": len(state.desktops),
                      "rows": state.rows, "prestate_digest": state.digest(),
                      "private_state_saved": True, "dry_run_status": report["status"],
                      "transaction_id": report["transaction_id"], "fingerprint": report["fingerprint"],
                      "backup_key_count": len(report["backup_keys"])}, sort_keys=True))


if __name__ == "__main__":
    main()
