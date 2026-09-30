"""Read-only comparison of sanitized local inspection snapshots."""

import json
from pathlib import Path

from workbenchlib.inspect import OUTPUT_DIR, SCHEMA_VERSION

SOFTWARE = {"software_repo_explicit", "software_foreign_explicit", "software_flatpak_apps"}


def load_snapshot(path: str, root: Path = OUTPUT_DIR) -> dict:
    allowed = root.resolve()
    candidate = Path(path).resolve()
    if candidate.suffix != ".json" or not candidate.is_relative_to(allowed):
        raise ValueError("snapshot path must be a JSON file under .workbench/inspections")
    document = json.loads(candidate.read_text(encoding="utf-8"))
    validate_snapshot(document)
    return document


def validate_snapshot(document: dict) -> None:
    if not isinstance(document, dict) or document.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported snapshot schema version")
    probes = document.get("probes")
    if not isinstance(probes, list) or any(not isinstance(p, dict) or not isinstance(p.get("id"), str) for p in probes):
        raise ValueError("invalid snapshot probes")
    if len({p["id"] for p in probes}) != len(probes):
        raise ValueError("duplicate probe ID")


def _known(probe: dict | None) -> bool:
    return bool(probe and probe.get("status") == "ok" and (probe.get("observation") in {"present", "not_present"} or probe.get("id") in {"settings_surfaces", "software_targeted"} and probe.get("observation") == "unknown"))


def _items(probe: dict | None) -> dict[str, object]:
    if not _known(probe):
        return {}
    name = probe["id"]
    facts = probe.get("facts", {})
    if name in SOFTWARE:
        ids = facts.get("ids", [])
        if not isinstance(ids, list) or not all(isinstance(x, str) for x in ids):
            raise ValueError("invalid software facts")
        return {f"{name}/{value}": True for value in ids}
    if name == "settings_surfaces":
        rows = facts.get("surfaces", [])
        if not isinstance(rows, list):
            raise ValueError("invalid settings facts")
        return {f"{name}/{row['id']}": (row.get("category"), row.get("state")) for row in rows if isinstance(row, dict) and isinstance(row.get("id"), str)}
    if name == "software_targeted":
        rows = facts.get("evidence", [])
        if not isinstance(rows, list):
            raise ValueError("invalid targeted software facts")
        return {f"{name}/{row['evidence_id']}": row.get("state") for row in rows if isinstance(row, dict) and isinstance(row.get("evidence_id"), str)}
    return {name: (probe["observation"], facts)}


def compare(older: dict, newer: dict) -> dict:
    validate_snapshot(older)
    validate_snapshot(newer)
    old_probes = {p["id"]: p for p in older["probes"]}
    new_probes = {p["id"]: p for p in newer["probes"]}
    changes = []
    for name in sorted(old_probes.keys() | new_probes.keys()):
        old, new = old_probes.get(name), new_probes.get(name)
        left, right = _items(old), _items(new)
        keys = left.keys() | right.keys()
        if not keys:
            keys = {name}
        for key in sorted(keys):
            a, b = left.get(key), right.get(key)
            if not _known(old) or not _known(new) or (name == "settings_surfaces" and (isinstance(a, tuple) and a[1] == "unknown" or isinstance(b, tuple) and b[1] == "unknown")) or (name == "software_targeted" and (a == "unknown" or b == "unknown")):
                classification = "unknown"
            elif key not in left:
                classification = "added"
            elif key not in right:
                classification = "removed"
            elif a == b:
                classification = "unchanged"
            else:
                classification = "changed"
            changes.append({"key": key, "classification": classification})
    return {"schema_version": SCHEMA_VERSION, "changes": changes}
