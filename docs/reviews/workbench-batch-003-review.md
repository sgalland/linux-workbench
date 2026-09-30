# Batch 003 read-only KDE review gate

## Checkpoints

1. `af40029` — narrow KDE evidence model and fixture/privacy/failure probes.
2. `ef65420` — virtual desktop, Activity, and hybrid decision record.
3. `89ee0a6` — shortcut and window interaction candidate map.
4. `e48be5c` — Plasma shell/control-area feasibility.
5. `a3f080e` — portable candidate desktop intent and KDE adapter data.
6. This review-gate commit; its hash is reported at the gate.

## Verification and local versions

The complete `python3 -m unittest discover -s tests -v` suite passed:
**44 tests, zero failures or errors**. `git diff --check` passed. Jobs 1–4
passed 42 tests at each checkpoint; Job 5 passed 44. KWin `--version` returned
6.7.5. Exact pacman metadata returned 6.7.5-1.1 for `kwin`,
`plasma-desktop`, and `plasma-workspace`. The direct `plasmashell --version`
probe failed nonzero; no runtime Plasma shell version is claimed from it.
The allowlisted numeric desktop-count probe returned 1. Tool availability
alone does not establish configured behavior.

## Decisions and limits

Four named KWin virtual desktops are the recommended **candidate** for
Development, General, Office, and Creative because the requirement centers
on window grouping. Activities remain an alternative for separate desktop
widgets, and a hybrid is reserved for a demonstrated two-axis need. KDE
documents remembering the current virtual desktop per Activity, with a
restart required. Panels are shared across Activities. Persistence of the
chosen arrangement across login/reboot is untested.

The shortcut candidate preserves Ctrl for common application actions and
uses KWin/Plasma global actions for workstation behavior. Alt+Tab remains the
window switcher candidate. Meta+number may overlap task-manager launching;
Meta+Tab is documented for Activities; exact current assignments were not
read. Application-owned shortcuts remain outside a central guarantee.

Plasma supports a side panel, built-in categorized launcher/menu, and System
Monitor widgets. Current layouts and chosen metrics are unknown. A desktop
right-click that simultaneously supplies a full application menu and retains
the standard desktop/system context menu is unverified. Ordinary overlapping
windows and optional KWin quick tiling are documented capabilities. The
[capability matrix](workbench-batch-003-kde-feasibility.md) separates
documentation, local observation, inference, and unknown status.

The candidate [portable desktop intent](../../spec/desktop-intent.candidate.json)
and [KDE adapter](../../adapters/kde-desktop.candidate.json) validate but are
not authoritative or executable. Future surfaces and verification strategies
are design notes only. No backup/apply/rollback implementation was added.

Deferred decisions: approve or revise four virtual desktops versus
Activities; specify whether context-specific widgets are wanted; choose
shortcut assignments after exact collision review; define launcher groups
and monitor metrics; determine whether right-click must preserve the
standard context menu; verify persistence, multi-display panel behavior,
window placement, and session restoration in a separately authorized change.

Only fixed tool checks, exact `kwinrc` desktop count, KWin version, and exact
package-version queries were used. No complete KDE files, arbitrary D-Bus
payloads, KScreen data, Activity UUIDs, widget-private data, recent-document
data, histories, or raw inspection snapshots were collected or committed.
No desktop or system mutation occurred. The untracked experimental-kernel
directory was not touched. This is the v0.4 review gate; v0.5 is not
authorized.
