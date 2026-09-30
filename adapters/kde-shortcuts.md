# KDE shortcut and window interaction candidate (Batch 003, Job 3)

KDE [separates global from standard application shortcuts](https://docs.kde.org/stable_kf6/en/plasma-desktop/kcontrol/keys/index.html).
KWin owns window and desktop actions; Plasma owns launcher and shell actions;
KDE standard shortcuts cover common document/edit actions. The same KDE manual
states that applications define additional shortcuts themselves. Workbench
therefore cannot guarantee Windows-like bindings across non-KDE applications.
The current local bindings are **unknown**: this batch does not read the full
`kglobalshortcutsrc`, and no exact action-key parser was reviewed for it.

| Intent | Candidate binding | KDE owner | Default or collision note |
| --- | --- | --- | --- |
| Application menu | bare Meta | Plasma launcher | KDE [documents Meta as the default](https://docs.kde.org/stable_kf6/en/plasma-desktop/kcontrol/keys/index.html); current binding unknown |
| Search/run | Meta+Space candidate | Plasma/KRunner | Check existing global binding before any assignment; launcher overlap possible |
| Switch windows | Alt+Tab | KWin task switcher | Documented common invocation; preserves familiar convention |
| Maximize | Meta+Up candidate | KWin | Supported KWin action; binding is a candidate, not a verified default |
| Minimize/restore | Meta+Down candidate | KWin | Direction can conflict with quick tile or restore behavior; exact action semantics require review |
| Tile left/right | Meta+Left / Meta+Right candidate | KWin quick tile | KWin [documents quick tiling](https://docs.kde.org/stable_kf6/en/kwin/kcontrol/windowbehaviour/index.html); local binding unknown |
| Show desktop | Meta+D candidate | KWin/Plasma | May collide with desktop action or application binding; confirm owner in local shortcut UI |
| Workspace 1–4 | Meta+1…4 candidate | KWin | Common collision with task manager's Meta+number launch/activate behavior; **do not allocate until checked** |
| Next/previous workspace | Meta+Ctrl+Right / Left candidate | KWin | Ctrl is used only with Meta here; check existing bindings and keyboard layout |
| Activities | Meta+Tab documented | Plasma Activities | [Plasma manual lists Meta+Tab](https://docs.kde.org/stable_kf6/en/plasma-desktop/plasma-desktop/shortcuts.html); conflicts with a proposed Meta+Tab window overview |
| Copy/paste/undo/save/find | Ctrl+C/V/Z/S/F | KDE standard applications | [KDE Fundamentals lists these conventions](https://docs.kde.org/stable_kf6/en/khelpcenter/fundamentals/kbd.html); application-owned overrides remain possible |

This candidate map deliberately reserves bare Ctrl combinations for
applications. Meta+number and Meta+Tab are unresolved collisions, so they
must not be treated as approved assignments. `Alt+Tab` is retained for window
switching. KWin [task-switcher settings](https://docs.kde.org/stable_kf6/en/kwin/kcontrol/kwintabbox/)
can filter by desktop or Activity, so its future scope needs a decision.
KWin [window rules](https://docs.kde.org/stable_kf6/en/kwin/kcontrol/windowspecific/attributes.html)
can target desktops/Activities, and [window behavior](https://docs.kde.org/stable_kf6/en/kwin/kcontrol/windowbehaviour/index.html)
can choose what happens when an already-open window on another desktop is
activated. These settings and quick tile behavior support conventional
overlapping windows with optional snap, rather than forcing a tiling layout.

Future verification should inspect only exact actions in System Settings or
through individually reviewed key reads, compare all candidates for duplicate
bindings and reserved Meta-only behavior, then test application exceptions.
No shortcut or KWin state was changed here.
