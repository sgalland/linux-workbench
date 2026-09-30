"""Validate portable intent and data-only CachyOS software mappings."""

import json
import re
from pathlib import Path

LOGICAL = re.compile(r"[a-z][a-z0-9]*(?:[.-][a-z0-9]+)+\Z")
PACKAGE = re.compile(r"[a-z0-9][a-z0-9@._+-]*\Z")
FLATPAK = re.compile(r"[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+){2,}\Z")
SOURCES = {"repo", "foreign", "flatpak", "targeted"}


def _object_keys(value, required):
    return isinstance(value, dict) and set(value) == set(required)


def validate_desired(document: dict) -> dict:
    if not _object_keys(document, {"schema_version", "software", "settings_surfaces"}) or type(document["schema_version"]) is not int or document["schema_version"] != 1:
        raise ValueError("invalid desired-state document or schema")
    seen = set()
    for kind in ("software", "settings_surfaces"):
        rows = document[kind]
        if not isinstance(rows, list):
            raise ValueError("invalid desired-state rows")
        for row in rows:
            if not _object_keys(row, {"id", "intent", "review_category"}) or not isinstance(row["id"], str) or not LOGICAL.fullmatch(row["id"]) or not isinstance(row["intent"], str) or row["intent"] not in {"required", "optional"} or not isinstance(row["review_category"], str) or not LOGICAL.fullmatch("category." + row["review_category"]):
                raise ValueError("invalid desired-state entry")
            if not row["id"].startswith("software." if kind == "software" else "settings.") or row["id"] in seen:
                raise ValueError("invalid or duplicate logical ID")
            seen.add(row["id"])
    return document


def validate_mapping(document: dict) -> dict:
    if not _object_keys(document, {"schema_version", "software"}) or type(document["schema_version"]) is not int or document["schema_version"] != 1 or not isinstance(document["software"], list):
        raise ValueError("invalid mapping document or schema")
    for row in document["software"]:
        if not _object_keys(row, {"logical_id", "source", "identifier"}) or not isinstance(row["logical_id"], str) or not LOGICAL.fullmatch(row["logical_id"]) or not row["logical_id"].startswith("software.") or not isinstance(row["source"], str) or row["source"] not in SOURCES or not isinstance(row["identifier"], str):
            raise ValueError("invalid software mapping")
        pattern = FLATPAK if row["source"] == "flatpak" else LOGICAL if row["source"] == "targeted" else PACKAGE
        if not pattern.fullmatch(row["identifier"]):
            raise ValueError("invalid mapped identifier")
    return document


def load_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
