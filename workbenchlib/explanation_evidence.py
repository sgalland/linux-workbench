"""Deterministic, read-only evidence packaging for future A1 explanations.

Inputs are already-normalized Workbench documents. This module performs no
collection, inference, planning, or provider calls.
"""

import json

from workbenchlib.compare import validate_snapshot


def _copy_json(value):
    """Copy input and reject values outside the JSON data model."""
    try:
        return json.loads(json.dumps(value, allow_nan=False, sort_keys=True))
    except (TypeError, ValueError) as exc:
        raise ValueError("evidence must be JSON-serializable") from exc


def build_bundle(*, snapshot=None, comparison=None, proposal=None):
    """Package supplied Workbench evidence without interpreting its meaning.

    Omitted sections remain None. Incomplete probes retain their ID and source,
    but cannot supply an observed fact. No input document is modified.
    """
    if snapshot is None and comparison is None and proposal is None:
        raise ValueError("at least one evidence document is required")

    observations = None
    if snapshot is not None:
        validate_snapshot(snapshot)
        observations = []
        for probe in sorted(snapshot["probes"], key=lambda row: row["id"]):
            status = probe.get("status", "unknown")
            observation = probe.get("observation", "unknown")
            facts = probe.get("facts")
            provenance = probe.get("provenance")
            if not isinstance(status, str) or observation not in {"present", "not_present", "unknown"}:
                raise ValueError("invalid probe status or observation")
            if facts is not None and not isinstance(facts, dict):
                raise ValueError("invalid probe facts")
            if provenance is not None and not isinstance(provenance, dict):
                raise ValueError("invalid probe provenance")
            if status != "ok" or facts is None:
                observation, facts = "unknown", {}
            elif probe["id"] in {"software_repo_explicit", "software_foreign_explicit", "software_flatpak_apps"}:
                ids = facts.get("ids")
                if not isinstance(ids, list) or any(not isinstance(row, str) for row in ids):
                    observation, facts = "unknown", {}
                else:
                    facts = {**facts, "ids": sorted(ids)}
            elif probe["id"] in {"settings_surfaces", "software_targeted"}:
                field, key = (("surfaces", "id") if probe["id"] == "settings_surfaces" else ("evidence", "evidence_id"))
                rows = facts.get(field)
                if not isinstance(rows, list) or any(not isinstance(row, dict) or not isinstance(row.get(key), str) for row in rows):
                    observation, facts = "unknown", {}
                else:
                    allowed = {"present", "absent", "unknown"}
                    if any(row.get("state", "unknown") not in allowed for row in rows):
                        raise ValueError("invalid evidence state")
                    normalized = [{**row, "state": row.get("state", "unknown")} for row in rows]
                    facts = {**facts, field: sorted(normalized, key=lambda row: row[key])}
            observations.append({"id": probe["id"], "status": status, "observation": observation,
                                 "facts": facts, "provenance": provenance})

    changes = None
    if comparison is not None:
        if not isinstance(comparison, dict) or comparison.get("schema_version") != 1 or not isinstance(comparison.get("changes"), list):
            raise ValueError("invalid comparison document")
        changes = comparison["changes"]
        if any(not isinstance(row, dict) or not isinstance(row.get("key"), str) or row.get("classification") not in {"added", "removed", "changed", "unchanged", "unknown"} for row in changes):
            raise ValueError("invalid comparison change")
        if len({row["key"] for row in changes}) != len(changes):
            raise ValueError("duplicate comparison key")
        changes = sorted(({"key": row["key"], "classification": row["classification"]} for row in changes), key=lambda row: row["key"])

    planned = None
    if proposal is not None:
        if not isinstance(proposal, dict) or proposal.get("schema_version") != 1 or proposal.get("proposal_only") is not True or not isinstance(proposal.get("entries"), list):
            raise ValueError("invalid proposal document")
        entries = proposal["entries"]
        if any(not isinstance(row, dict) or not isinstance(row.get("classification"), str) for row in entries):
            raise ValueError("invalid proposal entry")
        planned = {"proposal_only": True, "entries": sorted(_copy_json(entries), key=lambda row: json.dumps(row, sort_keys=True))}

    return _copy_json({"schema_version": 1, "observations": observations,
                       "changes": changes, "proposal": planned})
