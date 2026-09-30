"""Reviewed implementation-specific settings surfaces; metadata checks only."""

from pathlib import Path

# (logical ID, category, root, relative path). No discovered names are emitted.
CATALOG = (
    ("shell.fish", "shell", "home", ".config/fish/config.fish"),
    ("vcs.git-user", "development", "home", ".gitconfig"),
    ("packages.pacman", "package-management", "etc", "pacman.conf"),
    ("packages.makepkg", "package-management", "etc", "makepkg.conf"),
    ("desktop.plasma-workspace", "desktop", "home", ".config/plasmarc"),
    ("desktop.plasma-keybindings", "desktop", "home", ".config/kglobalshortcutsrc"),
    ("desktop.plasma-window-manager", "desktop", "home", ".config/kwinrc"),
)


def discover(home: Path, etc: Path) -> list[dict[str, str]]:
    """Stat fixed paths. Never open files or serialize paths or stat values."""
    result = []
    roots = {"home": home, "etc": etc}
    for logical_id, category, root, relative in CATALOG:
        path = roots[root] / relative
        try:
            path.stat()
            state = "present"
        except FileNotFoundError:
            state = "absent"
        except OSError:
            state = "unknown"
        result.append({"id": logical_id, "category": category, "state": state})
    return result
