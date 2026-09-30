"""Small, read-only KDE evidence catalog. Raw probe output never escapes parsers."""

from __future__ import annotations

import re
import shutil
import subprocess
from typing import Callable


PROBES = {
    "virtual_desktop_count": ("kreadconfig6", "--file", "kwinrc", "--group", "Desktops", "--key", "Number"),
}
TOOLS = ("kreadconfig6", "plasmashell", "kwin_wayland")
STATUSES = {"ok", "missing_tool", "access_denied", "timeout", "command_error", "parse_error"}
EVIDENCE_TYPES = {"official_documentation", "local_observation", "project_inference", "unknown"}


def parse_desktop_count(raw: str) -> int | None:
    """Accept only a small positive count; never preserve other config text."""
    if not re.fullmatch(r"[1-9][0-9]?\n?", raw) or int(raw.strip()) > 20:
        return None
    return int(raw.strip())


def collect(
    runner: Callable[[list[str]], tuple[str, int]] | None = None,
    which: Callable[[str], str | None] = shutil.which,
) -> list[dict]:
    """Run fixed argv only. No D-Bus call or config file enumeration."""
    if runner is None:
        runner = _run
    rows = [
        {"id": f"tool.{name}", "evidence_type": "local_observation", "status": "ok",
         "value": "available" if which(name) else "unknown"}
        for name in TOOLS
    ]
    for probe_id, argv in PROBES.items():
        if not which(argv[0]):
            rows.append(_unknown(probe_id, "missing_tool"))
            continue
        try:
            raw, code = runner(list(argv))
        except subprocess.TimeoutExpired:
            rows.append(_unknown(probe_id, "timeout"))
            continue
        except PermissionError:
            rows.append(_unknown(probe_id, "access_denied"))
            continue
        except Exception:
            rows.append(_unknown(probe_id, "command_error"))
            continue
        count = parse_desktop_count(raw) if code == 0 else None
        rows.append({"id": probe_id, "evidence_type": "local_observation", "status": "ok", "value": count}
                    if count is not None else _unknown(probe_id, "parse_error" if code == 0 else "command_error"))
    return rows


def _unknown(probe_id: str, status: str) -> dict:
    return {"id": probe_id, "evidence_type": "unknown", "status": status, "value": None}


def _run(argv: list[str]) -> tuple[str, int]:
    result = subprocess.run(argv, shell=False, capture_output=True, text=True, timeout=5, check=False)
    return result.stdout, result.returncode
