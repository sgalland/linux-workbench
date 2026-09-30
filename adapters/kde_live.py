"""Narrow KWin 6.7.5 session backend for the four-desktop pilot.

All commands are fixed argv through an injectable runner. Construction and
inspection never invoke a mutator. This is an implementation-detail interface,
so the exact version and introspection surface are required before writes.
"""

import json
from pathlib import Path
import re
import secrets
import subprocess

from adapters.kde_workspace import CONFIG_KEYS, Desktop, State, TARGET
from workbenchlib.backup import Value

SERVICE = "org.kde.KWin"
OBJECT = "/VirtualDesktopManager"
INTERFACE = "org.kde.KWin.VirtualDesktopManager"
EXPECTED = {
    "createDesktop": ("method", "us", ""),
    "setDesktopName": ("method", "ss", ""),
    "removeDesktop": ("method", "s", ""),
    "count": ("property", "u", ""),
    "rows": ("property", "u", ""),
    "current": ("property", "s", ""),
    "desktops": ("property", "a(iss)", ""),
}


def subprocess_runner(argv):
    return subprocess.run(argv, capture_output=True, text=True, timeout=8, check=True).stdout


class KWinBackend:
    def __init__(self, runner=subprocess_runner, config_path=None):
        self.runner = runner
        self.config_path = str(config_path if config_path is not None else Path.home() / ".config/kwinrc")

    def _run(self, argv):
        try:
            return self.runner(argv)
        except (OSError, subprocess.SubprocessError) as exc:
            step = "introspection" if "introspect" in argv else (
                "property read" if "get-property" in argv else (
                    "version" if argv[0] == "kwin_wayland" else "config read" if argv[0] == "kreadconfig6" else "mutation"))
            raise ValueError(f"KWin {step} command failed") from exc

    def validate_surface(self):
        if self._run(["kwin_wayland", "--version"]).strip() != "kwin 6.7.5":
            raise ValueError("unsupported KWin version")
        output = self._run(["busctl", "--user", "introspect", SERVICE, OBJECT, INTERFACE])
        found = {}
        for line in output.splitlines():
            fields = line.split()
            if fields:
                fields[0] = fields[0].removeprefix(INTERFACE + ".").removeprefix(".")
            if len(fields) >= 2 and fields[0] in EXPECTED:
                if fields[0] in found:
                    raise ValueError("duplicate KWin interface member")
                found[fields[0]] = fields
        for name, (kind, input_sig, output_sig) in EXPECTED.items():
            fields = found.get(name)
            if fields is None or fields[1] != kind:
                raise ValueError(f"unsupported KWin interface member: {name}")
            if kind == "method":
                if len(fields) < 4 or fields[2:4] != [input_sig or "-", output_sig or "-"]:
                    raise ValueError(f"unsupported KWin method signature: {name} ({','.join(fields[2:4])})")
            elif len(fields) < 3 or fields[2] != input_sig:
                raise ValueError(f"unsupported KWin property signature: {name} ({fields[2] if len(fields) > 2 else '-'})")

    def _property(self, name, signature):
        if name not in {"count", "rows", "current", "desktops"}:
            raise ValueError("property outside pilot")
        try:
            reply = json.loads(self._run(["busctl", "--user", "--json=short", "get-property", SERVICE, OBJECT, INTERFACE, name]))
            if reply["type"] != signature or set(reply) != {"type", "data"}:
                raise ValueError(f"unexpected property reply: {name}, type={reply.get('type')}, keys={','.join(sorted(reply))}")
            return reply["data"]
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError("malformed property reply") from exc

    def inspect(self):
        rows = self._property("desktops", "a(iss)")
        count = self._property("count", "u")
        current = self._property("current", "s")
        row_count = self._property("rows", "u")
        if (type(rows) is not list or type(count) is not int or count != len(rows)
                or type(current) is not str or type(row_count) is not int
                or any(type(item) is not list or len(item) != 3 or type(item[0]) is not int
                       or type(item[1]) is not str or type(item[2]) is not str for item in rows)
                or [item[0] for item in rows] != list(range(count))):
            raise ValueError("inconsistent KWin desktop reply")
        return State(tuple(Desktop(item[1], item[2]) for item in rows), current, row_count)

    def read_key(self, key):
        if key not in CONFIG_KEYS + ("Id_5",):
            raise ValueError("config key outside pilot")
        sentinels = ["WORKBENCH_ABSENT_" + secrets.token_hex(16) for _ in range(2)]
        outputs = [self._run(["kreadconfig6", "--file", self.config_path, "--group", "Desktops",
                              "--key", key, "--default", sentinel]).removesuffix("\n") for sentinel in sentinels]
        if outputs == sentinels:
            return Value(False)
        if outputs[0] == outputs[1] and outputs[0] not in sentinels:
            return Value(True, outputs[0])
        raise ValueError("ambiguous config presence")

    def write_key(self, key, value):
        if key not in CONFIG_KEYS or not isinstance(value, Value):
            raise ValueError("config write outside pilot")
        argv = ["kwriteconfig6", "--file", self.config_path, "--group", "Desktops", "--key", key]
        self._run(argv + ([value.value] if value.present else ["--delete"]))

    def set_name(self, desktop_id, name):
        if not isinstance(desktop_id, str) or not desktop_id or not isinstance(name, str):
            raise ValueError("rename outside pilot")
        self._run(["busctl", "--user", "call", SERVICE, OBJECT, INTERFACE,
                   "setDesktopName", "ss", desktop_id, name])

    def create(self, position, name):
        if type(position) is not int or position not in (1, 2, 3) or name != TARGET[position]:
            raise ValueError("create outside pilot")
        self._run(["busctl", "--user", "call", SERVICE, OBJECT, INTERFACE,
                   "createDesktop", "us", str(position), name])

    def remove(self, desktop_id):
        if not isinstance(desktop_id, str) or not desktop_id:
            raise ValueError("invalid desktop ID")
        self._run(["busctl", "--user", "call", SERVICE, OBJECT, INTERFACE,
                   "removeDesktop", "s", desktop_id])
