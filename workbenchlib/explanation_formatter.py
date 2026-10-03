"""Deterministic terminal text for supplied A1 explanation evidence bundles."""

import json


def _json(value):
    return json.dumps(value, allow_nan=False, sort_keys=True, separators=(", ", ": "))


def _validate(bundle):
    if not isinstance(bundle, dict) or type(bundle.get("schema_version")) is not int or bundle["schema_version"] != 1:
        raise ValueError("invalid explanation bundle schema")
    try:
        _json(bundle)
    except (TypeError, ValueError) as exc:
        raise ValueError("explanation bundle must be JSON-serializable") from exc

    observations = bundle.get("observations")
    if observations is not None:
        if not isinstance(observations, list) or any(
            not isinstance(row, dict)
            or not isinstance(row.get("id"), str)
            or not isinstance(row.get("status"), str)
            or not isinstance(row.get("observation"), str)
            or row["observation"] not in {"present", "not_present", "unknown"}
            or not isinstance(row.get("facts"), dict)
            or row.get("provenance") is not None and not isinstance(row["provenance"], dict)
            or row["status"] != "ok" and (row["observation"] != "unknown" or row["facts"])
            for row in observations
        ) or len({row["id"] for row in observations}) != len(observations):
            raise ValueError("invalid bundle observations")

    changes = bundle.get("changes")
    if changes is not None:
        if not isinstance(changes, list) or any(
            not isinstance(row, dict)
            or not isinstance(row.get("key"), str)
            or not isinstance(row.get("classification"), str)
            or row["classification"] not in {"added", "removed", "changed", "unchanged", "unknown"}
            for row in changes
        ) or len({row["key"] for row in changes}) != len(changes):
            raise ValueError("invalid bundle changes")

    proposal = bundle.get("proposal")
    if proposal is not None:
        if (not isinstance(proposal, dict) or proposal.get("proposal_only") is not True
                or not isinstance(proposal.get("entries"), list) or any(
                    not isinstance(row, dict) or not isinstance(row.get("classification"), str)
                    for row in proposal["entries"]
                )):
            raise ValueError("invalid bundle proposal")


def format_bundle(bundle):
    """Render a supplied bundle as stable text, without collecting evidence."""
    _validate(bundle)
    observations = bundle.get("observations")
    known = [] if observations is None else sorted(
        (row for row in observations if row["status"] == "ok" and row["observation"] != "unknown"),
        key=lambda row: row["id"],
    )
    unknown = [] if observations is None else sorted(
        (row for row in observations if row["status"] != "ok" or row["observation"] == "unknown"),
        key=lambda row: row["id"],
    )
    lines = ["Observations:"]
    _render_observations(lines, known, observations is None)
    lines.append("Unknown/incomplete evidence:")
    _render_observations(lines, unknown, observations is None)

    lines.append("Comparison changes:")
    changes = bundle.get("changes")
    if changes is None:
        lines.append("  (not supplied)")
    elif not changes:
        lines.append("  (none)")
    else:
        for row in sorted(changes, key=lambda row: row["key"]):
            lines.append(f"  - {_json(row['key'])}: {row['classification']}")

    lines.append("Proposals (proposal only):")
    proposal = bundle.get("proposal")
    if proposal is None:
        lines.append("  (not supplied)")
    elif not proposal["entries"]:
        lines.append("  (none)")
    else:
        for row in sorted(proposal["entries"], key=_json):
            lines.append(f"  - {_json(row)}")
    return "\n".join(lines) + "\n"


def _render_observations(lines, rows, missing):
    if missing:
        lines.append("  (not supplied)")
    elif not rows:
        lines.append("  (none)")
    for row in rows:
        lines.append(f"  - {_json(row['id'])}: {row['observation']} (status: {_json(row['status'])})")
        lines.append(f"    Facts: {_json(row['facts'])}")
        if row["provenance"] is not None:
            lines.append(f"    Provenance: {_json(row['provenance'])}")
