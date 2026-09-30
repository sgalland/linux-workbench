"""Read-only reconciliation classifications; no execution path."""

from collections import Counter

from workbenchlib.compare import validate_snapshot
from workbenchlib.desired import validate_desired, validate_mapping

SOURCE_PROBES = {"repo": "software_repo_explicit", "foreign": "software_foreign_explicit", "flatpak": "software_flatpak_apps"}


def plan(desired: dict, snapshot: dict, mapping: dict) -> dict:
    validate_desired(desired)
    validate_snapshot(snapshot)
    validate_mapping(mapping)
    probes = {p["id"]: p for p in snapshot["probes"]}
    available = {}
    for source, name in SOURCE_PROBES.items():
        probe = probes.get(name)
        if probe is None or probe.get("status") != "ok" or probe.get("observation") not in {"present", "not_present"}:
            available[source] = None
            continue
        ids = probe.get("facts", {}).get("ids")
        if not isinstance(ids, list) or not all(isinstance(x, str) for x in ids):
            available[source] = None
        else:
            available[source] = set(ids)
    targeted = probes.get("software_targeted")
    targeted_states = None
    if targeted and targeted.get("status") == "ok" and isinstance(targeted.get("facts", {}).get("evidence"), list):
        targeted_states = {}
        for row in targeted["facts"]["evidence"]:
            if isinstance(row, dict) and isinstance(row.get("evidence_id"), str) and row.get("state") in {"present", "absent", "unknown"}:
                targeted_states[row["evidence_id"]] = row["state"]
    mappings = mapping["software"]
    target_counts = Counter((row["source"], row["identifier"]) for row in mappings)
    entries = []
    mapped_targets = set()
    for item in sorted(desired["software"], key=lambda x: x["id"]):
        candidates = [row for row in mappings if row["logical_id"] == item["id"]]
        mapped_targets.update((row["source"], row["identifier"]) for row in candidates)
        if not candidates:
            state = "mapping-unavailable"
        elif len(candidates) != 1 or any(target_counts[(row["source"], row["identifier"])] != 1 for row in candidates):
            state = "ambiguous/conflicting-mapping"
        else:
            row = candidates[0]
            if row["source"] == "targeted":
                observed_state = targeted_states.get(row["identifier"], "unknown") if targeted_states is not None else "unknown"
                state = {"present": "satisfied", "absent": "missing", "unknown": "observation-unknown"}[observed_state]
            else:
                observed = available[row["source"]]
                state = "observation-unknown" if observed is None else "satisfied" if row["identifier"] in observed else "missing"
        entries.append({"kind": "software", "id": item["id"], "intent": item["intent"], "review_category": item["review_category"], "classification": state})
    # Settings intent is portable; no settings implementation mapping exists yet.
    for item in sorted(desired["settings_surfaces"], key=lambda x: x["id"]):
        entries.append({"kind": "settings_surface", "id": item["id"], "intent": item["intent"], "review_category": item["review_category"], "classification": "mapping-unavailable"})
    for source in sorted(SOURCE_PROBES):
        observed = available[source]
        if observed is None:
            continue
        for identifier in sorted(observed):
            if (source, identifier) not in mapped_targets:
                entries.append({"kind": "software", "source": source, "identifier": identifier, "classification": "observed-but-unmanaged"})
    if targeted_states is not None:
        for identifier in sorted(targeted_states):
            if targeted_states[identifier] == "present" and ("targeted", identifier) not in mapped_targets:
                entries.append({"kind": "software", "source": "targeted", "identifier": identifier, "classification": "observed-but-unmanaged"})
    return {"schema_version": 1, "proposal_only": True, "entries": entries}
