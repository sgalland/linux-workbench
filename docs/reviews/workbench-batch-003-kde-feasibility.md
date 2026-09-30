# Batch 003 KDE feasibility matrix

Audit date: 2026-09-29. Local read-only observations: KWin reported 6.7.5;
the exact `kwinrc` `Desktops/Number` read parsed as **1**. `kreadconfig6`,
`plasmashell`, and `kwin_wayland` were available in PATH. The direct
`plasmashell --version` probe returned nonzero and its version is unknown by
that route; package metadata reports `plasma-workspace`, `plasma-desktop`, and
`kwin` **6.7.5-1.1**. A package version is not a runtime shell version.
No names, Activity IDs, panel/widget state, shortcuts, or monitor data were
collected.

| Portable requirement | KDE mechanism | Evidence type | Classification | Safe local state / limitation |
| --- | --- | --- | --- | --- |
| Conventional overlapping windows | KWin window behavior | [Official documentation](https://docs.kde.org/stable_kf6/en/kwin/kcontrol/windowbehaviour/index.html) | Supported | KWin version observed; current window behavior unknown |
| Familiar application shortcuts | KDE standard shortcuts | [Official documentation](https://docs.kde.org/stable_kf6/en/plasma-desktop/kcontrol/keys/index.html) | Supported with limitations | Application-owned actions cannot be guaranteed centrally; current bindings unknown |
| Ctrl primarily in applications | KDE standard vs global shortcut split | Official documentation above + project inference | Supported with limitations | Requires collision review; no current bindings read |
| Meta for window/workstation actions | KWin and Plasma global shortcuts | Official documentation above | Supported with limitations | Meta+number and Meta+Tab candidate collisions remain unresolved |
| Named Development, General, Office, Creative contexts | Named KWin virtual desktops candidate; Activities alternative | [Official documentation](https://docs.kde.org/stable_kf6/en/kwin/kcontrol/desktop/index.html), [local count](../../adapters/kde-evidence.md), project inference | Supported with limitations | Current count is 1, names unknown; four-context configuration untested |
| Persistent side control area | Plasma left/right panel, non-hiding mode | [Official KDE API](https://develop.kde.org/docs/plasma/scripting/api/) | Supported with limitations | Current panels uninspected; persistence and display behavior untested |
| Grouped application drawers | Application Launcher or Menu categories | [Official documentation](https://docs.kde.org/trunk_kf6/en/plasma-desktop/plasma-desktop/panel.html) | Supported with limitations | Custom group/ordering requirements and current launcher unknown |
| Useful system monitors | System Monitor and sensor widgets | [Official KDE developer documentation](https://develop.kde.org/docs/apps/sensor-faces/) | Supported | Desired metrics and current widgets unknown |
| Application/system menu from desktop right-click | Desktop Mouse Actions and launcher | [Official Plasma handbook](https://docs.kde.org/stable_kf6/en/plasma-desktop/plasma-desktop/plasma-desktop.pdf) + unknown combined behavior | Unknown | One action retaining standard system menu and full application tree unverified |
| Windows-like maximize/minimize/snap and workspace switching | KWin actions, quick tile, task switcher | [Official window behavior](https://docs.kde.org/stable_kf6/en/kwin/kcontrol/windowbehaviour/index.html) and [shortcut settings](https://docs.kde.org/stable_kf6/en/plasma-desktop/kcontrol/keys/index.html) | Supported with limitations | Exact bindings and restore semantics unknown |

The cited KDE pages are current stable KF6 or development documentation,
though several manuals retain older Plasma 5 revision labels. Documented
features are not assertions that this particular 6.7.5 session is configured
that way. The workspace choice is an adapter recommendation, not observed
intent. No KScreen state, arbitrary D-Bus payload, private KDE config, widget
data, history, or raw snapshot was collected or committed.
