"""Validation only for candidate desktop intent and KDE mappings."""

SUPPORT = {"supported", "supported-with-limitations", "workaround-required", "unsupported", "unknown"}
IDS = {
    "workspace.named_contexts", "window.overlapping", "window.snap",
    "shortcuts.application_conventions", "shortcuts.workstation_meta",
    "control_area.persistent_side", "launcher.grouped", "monitor.useful",
    "desktop_menu.application_system",
}


def validate(intent: dict, adapter: dict) -> None:
    if intent.get("schema_version") != 1 or intent.get("status") != "candidate":
        raise ValueError("invalid desktop intent header")
    if adapter.get("schema_version") != 1 or adapter.get("status") != "candidate" or adapter.get("target") != "kde-plasma":
        raise ValueError("invalid KDE adapter header")
    outcomes = intent.get("outcomes")
    mappings = adapter.get("mappings")
    if not isinstance(outcomes, list) or not isinstance(mappings, list):
        raise ValueError("outcomes and mappings must be lists")
    if {r.get("id") for r in outcomes} != IDS or len(outcomes) != len(IDS):
        raise ValueError("desktop outcomes must match reviewed IDs exactly")
    if {r.get("id") for r in mappings} != IDS or len(mappings) != len(IDS):
        raise ValueError("KDE mappings must match desktop outcomes exactly")
    if next(r for r in outcomes if r["id"] == "workspace.named_contexts").get("names") != ["Development", "General", "Office", "Creative"]:
        raise ValueError("workspace names differ from candidate requirement")
    for row in mappings:
        if row.get("support") not in SUPPORT or not all(isinstance(row.get(key), str) and row[key] for key in ("mechanism", "future_surface", "verify")):
            raise ValueError("incomplete KDE mapping")
