"""Fixed, reviewed software evidence. Never enumerate user directories."""

from pathlib import Path
import os

# (logical ID, evidence ID, source class, kind, exact marker).
# A marker is relative to one of the fixed XDG application directories.
CATALOG = (
    ("software.blender", "command.blender", "command", "command", "blender"),
    ("software.krita", "command.krita", "command", "command", "krita"),
    ("software.inkscape", "command.inkscape", "command", "command", "inkscape"),
    ("software.godot", "command.godot", "command", "command", "godot"),
    ("software.vscode", "command.code", "command", "command", "code"),
    ("software.obsidian", "launcher.obsidian", "launcher", "desktop", "obsidian.desktop"),
    ("software.spotify", "launcher.spotify", "launcher", "desktop", "spotify.desktop"),
    ("software.brave", "launcher.brave", "launcher", "desktop", "brave-browser.desktop"),
)


def _marker(path: Path) -> str:
    """Inspect the exact directory entry; never follow a symlink."""
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return "absent"
    except OSError:
        return "unknown"
    import stat
    return "present" if stat.S_ISREG(mode) or stat.S_ISDIR(mode) else "unknown"


def discover(home: Path, *, path_env: str | None = None, catalog=CATALOG,
             application_roots: tuple[Path, ...] | None = None) -> list[dict[str, str]]:
    roots = application_roots if application_roots is not None else (
        home / ".local/share/applications", Path("/usr/local/share/applications"),
        Path("/usr/share/applications"),
    )
    search_path = os.environ.get("PATH") if path_env is None else path_env
    rows = []
    for logical_id, evidence_id, source, kind, marker in catalog:
        if kind == "command":
            # An empty or unavailable PATH cannot establish absence.
            if not search_path:
                state = "unknown"
            else:
                import shutil
                try:
                    state = "present" if shutil.which(marker, path=search_path) else "absent"
                except OSError:
                    state = "unknown"
        elif kind == "desktop":
            states = [_marker(root / marker) for root in roots]
            state = "present" if "present" in states else "unknown" if "unknown" in states else "absent"
        elif kind == "marker":
            state = _marker(home / marker)
        else:
            state = "unknown"
        rows.append({"id": logical_id, "evidence_id": evidence_id, "source": source, "state": state})
    return rows
