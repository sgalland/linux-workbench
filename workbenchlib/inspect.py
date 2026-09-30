"""Read-only, deterministic discovery for the current user session.

Probe output is parsed in memory and discarded. Only normalized, allowlisted
facts are written to a snapshot under .workbench/inspections/.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from adapters.surfaces import discover as discover_surfaces

SCHEMA_VERSION = 1
COLLECTOR_VERSION = "0.3.0"
TIMEOUT_SECONDS = 8
REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / ".workbench" / "inspections"

# These are the only session variables made available to child processes.
# Their values are never included in the snapshot.
CHILD_ENV_KEYS = (
    "PATH", "HOME", "XDG_RUNTIME_DIR", "DBUS_SESSION_BUS_ADDRESS",
    "WAYLAND_DISPLAY", "DISPLAY", "XDG_SESSION_TYPE", "XDG_CURRENT_DESKTOP",
    "XDG_SESSION_DESKTOP", "KDE_SESSION_VERSION", "LANG", "LC_ALL",
)

Runner = Callable[[list[str], int], tuple[str, str, int]]


def _run(argv: list[str], timeout: int = TIMEOUT_SECONDS) -> tuple[str, str, int]:
    """Run one allowlisted command without a shell; never persist its output."""
    env = {key: os.environ[key] for key in CHILD_ENV_KEYS if key in os.environ}
    try:
        result = subprocess.run(
            argv, shell=False, capture_output=True, text=True, timeout=timeout,
            check=False, env=env,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return stdout, stderr, -1
    except FileNotFoundError:
        return "", "", -2
    except PermissionError:
        return "", "", -3
    return result.stdout, result.stderr, result.returncode


def _status_for_command(argv: list[str], code: int) -> str:
    if code == -2 or shutil.which(argv[0]) is None:
        return "missing_tool"
    if code == -3:
        return "access_denied"
    if code == -1:
        return "timeout"
    if code != 0:
        return "command_error"
    return "ok"


def _text_facts(text: str) -> dict[str, Any]:
    """Extract only reviewed, low-risk stable facts from os-release text."""
    allowed = {"NAME", "ID", "ID_LIKE", "VERSION_ID", "PRETTY_NAME"}
    found: dict[str, Any] = {}
    for line in text.splitlines():
        match = re.fullmatch(r'([A-Z_]+)=(?:"(.*)"|([^"\s]+))?', line)
        if match and match.group(1) in allowed:
            value = match.group(2) if match.group(2) is not None else match.group(3)
            if value:
                found[match.group(1).lower()] = value[:120]
    return found


def _parse_os_release(text: str) -> tuple[str, dict[str, Any]]:
    facts = _text_facts(text)
    return ("present" if facts else "unknown"), {"distribution": facts} if facts else {}


def _parse_uname(text: str) -> tuple[str, dict[str, Any]]:
    parts = text.strip().split()
    if len(parts) < 3:
        return "unknown", {}
    # uname -srm => kernel name, release, machine. Do not preserve the
    # hostname or other user-controlled nodename.
    return "present", {"kernel": parts[0][:40], "kernel_release": parts[1][:80], "architecture": parts[2][:40]}


def _parse_version(text: str) -> tuple[str, dict[str, Any]]:
    match = re.search(r"\b(\d+(?:\.\d+)+(?:[-+][A-Za-z0-9._-]+)?)\b", text)
    return ("present", {"version": match.group(1)}) if match else ("unknown", {})


def _parse_package_ids(text: str) -> tuple[str, dict[str, Any]]:
    """Accept only pacman package names, never descriptions or raw output."""
    rows = text.splitlines()
    if any(not re.fullmatch(r"[a-z0-9][a-z0-9@._+-]*", row) for row in rows):
        return "unknown", {}
    ids = sorted(set(rows))
    return ("present" if ids else "not_present"), {"ids": ids}


def _parse_flatpak_ids(text: str) -> tuple[str, dict[str, Any]]:
    rows = text.splitlines()
    # Application IDs are reverse-DNS style. Reject diagnostic or column text.
    if any(not re.fullmatch(r"[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+){2,}", row) for row in rows):
        return "unknown", {}
    ids = sorted(set(rows))
    return ("present" if ids else "not_present"), {"ids": ids}


def _parse_lscpu(text: str) -> tuple[str, dict[str, Any]]:
    facts: dict[str, Any] = {}
    keys = {"Architecture": "architecture", "CPU(s)": "logical_cpus", "Model name": "model", "Vendor ID": "vendor"}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = (part.strip() for part in line.split(":", 1))
        target = keys.get(key)
        if target and value:
            if target == "logical_cpus" and value.isdigit():
                facts[target] = int(value)
            else:
                facts[target] = value[:100]
    return ("present", facts) if facts else ("unknown", {})


def _parse_meminfo(text: str) -> tuple[str, dict[str, Any]]:
    for line in text.splitlines():
        match = re.fullmatch(r"MemTotal:\s+(\d+)\s+kB", line)
        if match:
            return "present", {"memory_total_kib": int(match.group(1))}
    return "unknown", {}


def _parse_lsblk(text: str) -> tuple[str, dict[str, Any]]:
    try:
        document = json.loads(text)
        devices = document.get("blockdevices", [])
        out = []

        def visit(items: list[Any], parent: int | None = None) -> None:
            for sibling_index, item in enumerate(items):
                if not isinstance(item, dict):
                    continue
                row: dict[str, Any] = {"index": sibling_index}
                if parent is not None:
                    row["parent_index"] = parent
                row.update({key: item[key] for key in ("type", "size", "fstype", "rota", "tran") if item.get(key) is not None})
                row_index = len(out)
                out.append(row)
                children = item.get("children")
                if isinstance(children, list):
                    visit(children, row_index)

        visit(devices)
        return ("present", {"devices": out}) if out else ("not_present", {"devices": []})
    except (json.JSONDecodeError, AttributeError, TypeError):
        return "unknown", {}


def _parse_pci(text: str) -> tuple[str, dict[str, Any]]:
    devices = []
    # Keep class and description only; omit bus addresses, vendor/device IDs,
    # subsystem IDs, and all driver symlink details that could identify a unit.
    for line in text.splitlines():
        match = re.match(r"\s*[0-9a-fA-F:.]+\s+([^:]+):\s+(.+)$", line)
        if match:
            cls, description = match.groups()
            description = re.sub(r"\s+\[[0-9a-fA-F]{4}:[0-9a-fA-F]{4}\]", "", description)
            row = {"class": re.sub(r"\s+\[[0-9a-fA-F]{4}\]", "", cls).strip()[:80], "description": description.strip()[:120]}
            devices.append(row)
        elif line.lstrip().startswith("Kernel driver in use:") and devices:
            devices[-1]["driver"] = line.split(":", 1)[1].strip()[:60]
    return ("present", {"devices": devices}) if devices else ("unknown", {})


def _parse_lsusb(text: str) -> tuple[str, dict[str, Any]]:
    devices = []
    for line in text.splitlines():
        # Exclude bus/device numbers and the hexadecimal VID:PID, retaining a
        # normalized class-like description only when it is present.
        match = re.search(r"ID\s+[0-9a-fA-F]{4}:[0-9a-fA-F]{4}\s+(.+)$", line)
        if match:
            description = re.sub(r"\b(?:serial|s/n)\s*[:#]?\s*\S+", "", match.group(1), flags=re.I).strip()
            description = re.sub(r"\s+", " ", description)
            if description:
                devices.append(description[:120])
    return ("present", {"devices": devices}) if devices else ("not_present", {"devices": []})


def _parse_usb_tree(text: str) -> tuple[str, dict[str, Any]]:
    # Keep topology depth and speed, omit bus/device addresses and port IDs.
    rows = []
    for line in text.splitlines():
        if re.search(r"\b(?:Class=|Driver=)", line):
            depth = len(line) - len(line.lstrip(" `|+-"))
            cls = re.search(r"Class=([^ ,]+)", line)
            driver = re.search(r"Driver=([^ ,]+)", line)
            speed = re.search(r"(\d+(?:\.\d+)?M)", line)
            rows.append({"depth": depth, **({"class": cls.group(1)} if cls else {}), **({"driver": driver.group(1)} if driver and driver.group(1) != "(none)" else {}), **({"speed": speed.group(1)} if speed else {})})
    return ("present", {"topology": rows}) if rows else ("unknown", {})


def _parse_alsa_cards(text: str) -> tuple[str, dict[str, Any]]:
    cards = []
    for line in text.splitlines():
        match = re.match(r"\s*(\d+)\s+\[([^]]+)\]:\s*(\S+)\s+-\s*(.+)$", line)
        if match:
            # ALSA card labels may contain hardware-derived identifiers. Keep
            # only card index and driver family.
            cards.append({"index": int(match.group(1)), "name": _safe_label(match.group(2)), "driver": _safe_label(match.group(3))})
        playback = re.match(r"\s*card\s+(\d+):\s+[^,]+,\s+device\s+\d+:\s+[^,]+,\s+subdevices:\s+(\d+)/(\d+)", line, re.I)
        if playback:
            card = int(playback.group(1))
            if not any(row.get("index") == card for row in cards):
                cards.append({"index": card})
    return ("present", {"cards": cards}) if cards else ("not_present", {"cards": []})


def _parse_alsa_listing(text: str, direction: str) -> tuple[str, dict[str, Any]]:
    _, card_facts = _parse_alsa_cards(text)
    devices = []
    for line in text.splitlines():
        match = re.match(r"\s*card\s+(\d+):\s*([^,]+),\s*device\s+(\d+):\s*([^,]+),\s*subdevices:\s*(\d+)/(\d+)", line, re.I)
        if match:
            card, _card_label, device, name, available, total = match.groups()
            devices.append({"card_index": int(card), "device_index": int(device), "name": _safe_label(name), "role": _audio_role(name), "direction": direction, "available_subdevices": int(available), "subdevices": int(total)})
    present = bool(card_facts["cards"] or devices)
    return ("present", {"cards": card_facts["cards"], "devices": devices}) if present else ("not_present", {"cards": [], "devices": []})


def _parse_alsa_pcm(text: str) -> tuple[str, dict[str, Any]]:
    rows = []
    for line in text.splitlines():
        match = re.match(r"\s*(\d+)-(\d+):\s*([^:]+):\s*(.*)$", line)
        if match:
            card, device, name, caps = match.groups()
            for direction, count, available in re.findall(r"\b(playback|capture)\s+(\d+)(?:\s*:\s*(?:subdevices?\s+)?(\d+))?", caps, re.I):
                row = {"card_index": int(card), "device_index": int(device), "name": _safe_label(name), "role": _audio_role(name), "direction": direction.lower(), "subdevices": int(count)}
                if available: row["available_subdevices"] = int(available)
                rows.append(row)
    return ("present", {"devices": rows}) if rows else ("not_present", {"devices": []})


def _parse_wpctl(text: str) -> tuple[str, dict[str, Any]]:
    sinks = sources = 0
    active_default: dict[str, str] = {}
    section = None
    for line in text.splitlines():
        stripped = line.strip()
        if re.search(r"\bAudio\s*$", stripped):
            section = "audio"
        elif stripped.startswith("Video") or stripped.startswith("Settings"):
            section = None
        if section == "audio" and re.search(r"\bSinks:\s*$", stripped):
            section = "sinks"
        elif re.search(r"\bSources:\s*$", stripped):
            section = "sources"
        elif re.search(r"\bSinks:\s*$", stripped):
            section = "sinks"
        elif section == "sinks" and re.search(r"\b\d+\.\s+.*\[vol:.*\]", stripped):
            sinks += 1
        elif section == "sources" and re.search(r"\b\d+\.\s+.*\[vol:.*\]", stripped):
            sources += 1
    if section is None and "audio" not in text.lower():
        return "unknown", {}
    defaults = {}
    active_section = None
    for line in text.splitlines():
        stripped = line.strip()
        if re.search(r"\bSinks:\s*$", stripped): active_section = "sink"
        elif re.search(r"\bSources:\s*$", stripped): active_section = "source"
        elif stripped.startswith(("Filters", "Streams", "Video", "Settings")): active_section = None
        if active_section and "*" in stripped:
            match = re.search(r"\b(\d+)\.\s+", stripped)
            if match: defaults[active_section] = int(match.group(1))
    return "present", {"sink_count": sinks, "source_count": sources, "default_markers": defaults}


def _parse_pw_dump(text: str) -> tuple[str, dict[str, Any]]:
    try:
        objects = json.loads(text)
        counts: dict[str, int] = {}
        endpoints = []
        for obj in objects:
            if not isinstance(obj, dict):
                continue
            info = obj.get("info") or {}
            props = info.get("props") or {}
            media_class = props.get("media.class")
            if isinstance(media_class, str) and media_class in {"Audio/Sink", "Audio/Source", "Audio/Device"}:
                counts[media_class] = counts.get(media_class, 0) + 1
                oid = obj.get("id")
                endpoint = {"snapshot_id": oid if isinstance(oid, int) else len(endpoints), "kind": media_class.split("/")[-1].lower()}
                for key in ("device.id", "node.device", "device.profile"):
                    val = props.get(key)
                    if key == "device.id" and isinstance(val, int): endpoint["device_ref"] = val
                    elif isinstance(val, str): endpoint[key.replace(".", "_")] = _safe_label(val)
                category = props.get("device.category") or props.get("media.role")
                if isinstance(category, str): endpoint["category"] = _safe_label(category)
                endpoints.append(endpoint)
            # Allowlist normalized mute/volume only on device/endpoint objects.
            # Do not retain node names, descriptions, client or stream identity.
            params = info.get("params") or []
            if isinstance(params, dict):
                prop_sets = params.get("Props", [])
            elif isinstance(params, list):
                prop_sets = [item.get("param", {}) for item in params if isinstance(item, dict) and item.get("id") == "Props"]
            else:
                prop_sets = []
            for param in prop_sets:
                if not isinstance(param, dict):
                    continue
                item = {}
                if isinstance(param.get("mute"), bool):
                    item["muted"] = param["mute"]
                volume = param.get("volume")
                if isinstance(volume, (int, float)):
                    item["volume"] = round(float(volume), 3)
                channels = param.get("channelVolumes")
                if isinstance(channels, list) and all(isinstance(v, (int, float)) for v in channels):
                    item["channel_volumes"] = [round(float(v), 3) for v in channels[:8]]
                if item:
                    target = next((x for x in endpoints if x["snapshot_id"] == obj.get("id")), None)
                    if target is not None: target["controls"] = item
        return "present", {"audio_class_counts": counts, "endpoints": endpoints}
    except (json.JSONDecodeError, TypeError, AttributeError):
        return "unknown", {}


def _safe_label(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9 _./+-]", "", value)
    return re.sub(r"\s+", " ", value).strip()[:80]


def _audio_role(value: str) -> str:
    label = value.lower()
    for term, role in (("hdmi", "hdmi"), ("deep buffer", "deep_buffer"), ("dmic", "microphone"), ("mic", "microphone"), ("analog", "analog"), ("headphone", "headphone")):
        if term in label: return role
    return "other"


def _parse_pactl(text: str) -> tuple[str, dict[str, Any]]:
    # pactl is only used with short listings. Parse counts; device/client names
    # and properties are discarded.
    return "present", {"item_count": sum(1 for line in text.splitlines() if line.strip() and not line.lower().startswith("card #"))}


def _parse_unit_states(text: str) -> tuple[str, dict[str, Any]]:
    allowed = {"pipewire.service", "wireplumber.service"}
    result: dict[str, dict[str, str]] = {}
    current: dict[str, str] = {}
    for line in text.splitlines() + [""]:
        if not line.strip():
            unit = current.get("Id")
            if unit in allowed:
                result[unit.removesuffix(".service")] = {key.lower(): value for key, value in current.items() if key in {"LoadState", "ActiveState", "SubState"}}
            current = {}
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            if key in {"Id", "LoadState", "ActiveState", "SubState"}:
                current[key] = value[:40]
    expected = {"pipewire", "wireplumber"}
    return ("present", {"units": result}) if set(result) == expected else ("unknown", {"units": result} if result else {})


def _probe_command(name: str, argv: list[str], parser: Callable[[str], tuple[str, dict[str, Any]]], runner: Runner) -> dict[str, Any]:
    try:
        stdout, _stderr, returncode = runner(argv, TIMEOUT_SECONDS)
    except Exception:
        return {"id": name, "status": "probe_error", "observation": "unknown", "facts": {}, "provenance": {"kind": "command", "argv": argv, "parser": "workbenchlib.inspect:v1"}}
    status = _status_for_command(argv, returncode)
    observation, facts = ("unknown", {})
    if status == "ok":
        try:
            observation, facts = parser(stdout)
            if observation == "unknown" and stdout.strip():
                status = "parse_error"
        except Exception:
            status = "parse_error"
    return {
        "id": name,
        "status": status,
        "observation": observation if status == "ok" else "unknown",
        "facts": facts if status == "ok" else {},
        "provenance": {"kind": "command", "argv": argv, "parser": "workbenchlib.inspect:v1"},
        **({"exit_code": returncode} if returncode >= 0 else {}),
    }


def _probe_file(name: str, path: Path, parser: Callable[[str], tuple[str, dict[str, Any]]]) -> dict[str, Any]:
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return {"id": name, "status": "unavailable", "observation": "unknown", "facts": {}, "provenance": {"kind": "file", "path": str(path), "parser": "workbenchlib.inspect:v1"}}
    except PermissionError:
        return {"id": name, "status": "access_denied", "observation": "unknown", "facts": {}, "provenance": {"kind": "file", "path": str(path), "parser": "workbenchlib.inspect:v1"}}
    except OSError:
        return {"id": name, "status": "read_error", "observation": "unknown", "facts": {}, "provenance": {"kind": "file", "path": str(path), "parser": "workbenchlib.inspect:v1"}}
    try:
        observation, facts = parser(content)
        return {"id": name, "status": "ok", "observation": observation, "facts": facts, "provenance": {"kind": "file", "path": str(path), "parser": "workbenchlib.inspect:v1"}}
    except Exception:
        return {"id": name, "status": "parse_error", "observation": "unknown", "facts": {}, "provenance": {"kind": "file", "path": str(path), "parser": "workbenchlib.inspect:v1"}}


def _probe_directory_count(name: str, path: Path) -> dict[str, Any]:
    try:
        count = sum(1 for _ in path.iterdir())
        return {"id": name, "status": "ok", "observation": "present" if count else "not_present", "facts": {"entry_count": count}, "provenance": {"kind": "directory_count", "path": str(path)}}
    except FileNotFoundError:
        return {"id": name, "status": "unavailable", "observation": "unknown", "facts": {}, "provenance": {"kind": "directory_count", "path": str(path)}}
    except PermissionError:
        return {"id": name, "status": "access_denied", "observation": "unknown", "facts": {}, "provenance": {"kind": "directory_count", "path": str(path)}}
    except OSError:
        return {"id": name, "status": "read_error", "observation": "unknown", "facts": {}, "provenance": {"kind": "directory_count", "path": str(path)}}


def _probe_audio_sysfs(name: str, path: Path, *, filter_audio: bool = False) -> dict[str, Any]:
    """Collect bounded direct-child names and driver links, never recurse."""
    try:
        rows = []
        for entry in sorted(path.iterdir(), key=lambda p: p.name)[:128]:
            row = {"name": _safe_label(entry.name)}
            try:
                driver = (entry / "driver").resolve().name
            except OSError:
                driver = ""
            if driver: row["driver"] = _safe_label(driver)
            if filter_audio and not re.search(r"audio|sound|codec|amp|speaker|hda", entry.name + " " + driver, re.I):
                continue
            rows.append(row)
        return {"id": name, "status": "ok", "observation": "present" if rows else "not_present", "facts": {"devices": rows}, "provenance": {"kind": "sysfs_direct_children", "path": str(path)}}
    except FileNotFoundError:
        return {"id": name, "status": "unavailable", "observation": "unknown", "facts": {}, "provenance": {"kind": "sysfs_direct_children", "path": str(path)}}
    except OSError:
        return {"id": name, "status": "read_error", "observation": "unknown", "facts": {}, "provenance": {"kind": "sysfs_direct_children", "path": str(path)}}


def collect(runner: Runner = _run, *, proc: Path = Path("/proc"), sysfs: Path = Path("/sys"), etc: Path = Path("/etc"), home: Path | None = None) -> dict[str, Any]:
    """Collect one snapshot. Paths are injectable for fixture-only tests."""
    probes: list[dict[str, Any]] = []
    # Stable basic facts, useful to supersede the manually assembled baseline.
    probes.append(_probe_file("os_release", etc / "os-release", _parse_os_release))
    probes.append(_probe_command("kernel", ["uname", "-srm"], _parse_uname, runner))
    probes.append(_probe_command("cpu", ["lscpu"], _parse_lscpu, runner))
    probes.append(_probe_file("memory", proc / "meminfo", _parse_meminfo))
    dmi_files = [sysfs / "class/dmi/id" / field for field in ("sys_vendor", "product_name", "product_version", "board_vendor", "board_name", "bios_vendor", "bios_version", "bios_date")]
    # DMI strings can contain serial/asset identifiers. Exclude those fields;
    # keep only model/vendor/date fields from the explicit list above.
    dmi_fields = {}
    for path in dmi_files:
        try:
            value = path.read_text(encoding="utf-8", errors="replace").strip()
            if value and value not in {"None", "To be filled by O.E.M."}:
                dmi_fields[path.name] = value[:100]
        except OSError:
            continue
    probes.append({"id": "firmware_and_system", "status": "ok" if dmi_fields else "unavailable", "observation": "present" if dmi_fields else "unknown", "facts": dmi_fields, "provenance": {"kind": "files", "paths": [str(p) for p in dmi_files], "parser": "workbenchlib.inspect:v1"}})
    probes.append(_probe_command("storage", ["lsblk", "--json", "--output", "NAME,TYPE,SIZE,FSTYPE,ROTA,TRAN"], _parse_lsblk, runner))
    probes.append(_probe_command("pci", ["lspci", "-nnk"], _parse_pci, runner))
    probes.append(_probe_command("usb", ["lsusb"], _parse_lsusb, runner))
    probes.append(_probe_command("usb_topology", ["lsusb", "-t"], _parse_usb_tree, runner))
    probes.extend([
        _probe_command("software_repo_explicit", ["pacman", "-Qqen"], _parse_package_ids, runner),
        _probe_command("software_foreign_explicit", ["pacman", "-Qqem"], _parse_package_ids, runner),
        _probe_command("software_flatpak_apps", ["flatpak", "list", "--app", "--columns=application"], _parse_flatpak_ids, runner),
    ])
    surfaces = discover_surfaces(home if home is not None else Path.home(), etc)
    probes.append({"id": "settings_surfaces", "status": "ok", "observation": "present" if all(s["state"] != "unknown" for s in surfaces) else "unknown", "facts": {"surfaces": surfaces}, "provenance": {"kind": "reviewed_surface_catalog", "catalog": "adapters.surfaces:v1"}})

    # Session facts contain only coarse, normalized values; raw environment is
    # never copied. Probe facility readiness with fixed display clients.
    session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    session_facts = {"session_type": session_type if session_type in {"wayland", "x11", "tty"} else "unknown", "desktop": "kde" if "kde" in desktop or "plasma" in desktop else "other" if desktop else "unknown"}
    probes.append({"id": "desktop_session", "status": "ok", "observation": "present" if session_facts["session_type"] != "unknown" else "unknown", "facts": session_facts, "provenance": {"kind": "allowlisted_environment", "keys": ["XDG_SESSION_TYPE", "XDG_CURRENT_DESKTOP"]}})
    probes.append(_probe_command("plasma_version", ["plasmashell", "--version"], _parse_version, runner))
    probes.append(_probe_command("kwin_version", ["kwin_wayland", "--version"], _parse_version, runner))
    probes.append({"id": "kscreen", "status": "not_collected", "observation": "unknown", "facts": {}, "provenance": {"kind": "deferred_probe", "reason": "kscreen-doctor excluded pending separately approved normal-session experiment"}})

    probes.extend([
        _probe_command("pipewire_snapshot", ["pw-dump"], _parse_pw_dump, runner),
        _probe_command("wireplumber_status", ["wpctl", "status"], _parse_wpctl, runner),
        _probe_command("pipewire_user_units", ["systemctl", "--user", "show", "--no-pager", "--property=Id,LoadState,ActiveState,SubState", "pipewire.service", "wireplumber.service"], _parse_unit_states, runner),
        _probe_command("alsa_playback", ["aplay", "-l"], lambda text: _parse_alsa_listing(text, "playback"), runner),
        _probe_command("alsa_capture", ["arecord", "-l"], lambda text: _parse_alsa_listing(text, "capture"), runner),
        _probe_file("alsa_proc_cards", proc / "asound/cards", _parse_alsa_cards),
        _probe_file("alsa_proc_pcm", proc / "asound/pcm", _parse_alsa_pcm),
        _probe_directory_count("alsa_proc_entries", proc / "asound"),
        _probe_audio_sysfs("hdaudio_devices", sysfs / "bus/hdaudio/devices"),
        _probe_audio_sysfs("i2c_audio_devices", sysfs / "bus/i2c/devices", filter_audio=True),
        _probe_audio_sysfs("soundwire_devices", sysfs / "bus/soundwire/devices"),
    ])

    # Only top-level names are collected. No recursive sysfs/proc dumps.
    sound_path = sysfs / "class/sound"
    try:
        sound_names = sorted(p.name for p in sound_path.iterdir())
        probes.append({"id": "sound_sysfs", "status": "ok", "observation": "present" if sound_names else "not_present", "facts": {"devices": [{"name": _safe_label(name)} for name in sound_names[:128]]}, "provenance": {"kind": "directory_names", "path": str(sound_path)}})
    except FileNotFoundError:
        probes.append({"id": "sound_sysfs", "status": "unavailable", "observation": "unknown", "facts": {}, "provenance": {"kind": "directory_names", "path": str(sound_path)}})
    except OSError:
        probes.append({"id": "sound_sysfs", "status": "read_error", "observation": "unknown", "facts": {}, "provenance": {"kind": "directory_names", "path": str(sound_path)}})

    return {
        "schema_version": SCHEMA_VERSION,
        "collector_version": COLLECTOR_VERSION,
        "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "completeness": {"probe_count": len(probes), "ok_count": sum(p["status"] == "ok" for p in probes), "incomplete_probe_ids": [p["id"] for p in probes if p["status"] != "ok" or p["observation"] == "unknown"], "complete": all(p["status"] == "ok" and p["observation"] != "unknown" for p in probes)},
        "probes": probes,
    }


def write_snapshot(snapshot: dict[str, Any], output_dir: Path = OUTPUT_DIR) -> Path:
    repo_root = REPO_ROOT.resolve()
    allowed_root = OUTPUT_DIR.resolve()
    resolved_output = output_dir.resolve()
    try:
        allowed_root.relative_to(repo_root)
        resolved_output.relative_to(allowed_root)
    except ValueError as exc:
        raise ValueError("snapshot output must stay under .workbench/inspections") from exc
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = output_dir / f"{stamp}.json"
    suffix = 1
    payload = json.dumps(snapshot, indent=2, sort_keys=True) + "\n"
    while True:
        try:
            # Exclusive creation refuses existing files and symlinks, including
            # broken symlinks, instead of following an attacker/user-created path.
            with path.open("x", encoding="utf-8") as output:
                output.write(payload)
            return path
        except FileExistsError:
            path = output_dir / f"{stamp}-{suffix}.json"
            suffix += 1


def main(args: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if args is None else args)
    if args != ["inspect"]:
        print("Usage: ./workbench inspect", file=sys.stderr)
        return 2
    snapshot = collect()
    path = write_snapshot(snapshot)
    print(f"Wrote sanitized inspection snapshot: {path.relative_to(REPO_ROOT)}")
    return 0
