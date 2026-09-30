# Batch 002 read-only workstation reconciliation

The Workbench collector ran in the normal KDE Wayland session, wrote one
ignored local snapshot under `.workbench/inspections/`, and the read-only
planner reconciled it with the 22-entry candidate manifest and operational
CachyOS mapping. All candidate intents remain undecided. These classifications
are evidence reports, not installation or removal instructions.

## Candidate evidence

- Satisfied at the reviewed marker (11): AnyDesk, Blender, Brave, Codex CLI,
  GitHub CLI, Inkscape, Insync, JetBrains Toolbox, Krita, Obsidian, and Visual
  Studio Code.
- Missing at the reviewed marker (6): CLion, Godot, PyCharm, Rider, Spotify,
  and WebStorm. A missing command or launcher does not prove that the software
  is absent through every installation source.
- Observation unknown (5): ChatGPT desktop, GOG Galaxy, ModernUO, Star Trek
  Fleet Command, and Ultima Online. Their sources are deliberately deferred.
- Mapping unavailable or ambiguous: none among the 22 candidates. Each maps
  to one catalog evidence ID, including an explicitly deferred ID where no
  safe source exists.

## Inventory coverage

The pacman explicit repository and foreign probes succeeded. The planner
observed 240 repository and 9 foreign package identifiers outside its curated
mapping. Those identifiers are intentionally omitted from this public review.
The Flatpak probe reported `missing_tool`, so Flatpak inventory is unknown;
it is not an empty installed-app set. Targeted evidence uses exact command
and launcher checks and does not inspect application contents. Game and Wine
sources remain deferred.

Only allowlisted candidate names and category counts appear here. No raw
snapshot, full installed-package list, private paths, account data, or command
output is committed. Collection and planning performed no system mutation.
