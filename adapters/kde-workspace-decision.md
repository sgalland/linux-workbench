# KDE workspace model decision (Batch 003, Job 2)

**Recommendation:** represent Development, General, Office, and Creative as
four named KWin virtual desktops in the KDE adapter. This is a project
inference from the requirement's emphasis on window grouping and switching;
it is a candidate, not a request to create desktops. Keep Activities as an
alternative if distinct desktop widgets or activity-specific behavior becomes
an explicit requirement. Do not add a hybrid by default.

| Question | Virtual desktops | Activities | Hybrid |
| --- | --- | --- | --- |
| Human-readable names | Documented rename | Documented name | Both |
| Keyboard switching | KWin global shortcut category; exact local binding unknown | Per-activity and walk-through shortcuts documented | Two axes of switching |
| Window grouping/placement | Primary KWin grouping; window rules can target a desktop | Window rules can target an Activity, but Activities chiefly group desktop widgets | Both targets; placement policy must disambiguate |
| Desktop widgets | No separate widget set established | Separate desktop containments/widgets documented | Per-Activity widgets |
| Panels | Shared shell panel | KDE scripting API states all Activities share panels | Shared panels |
| Persistence | Configuration expected to persist; no safe login/reboot test in this batch | Configuration expected to persist; no safe login/reboot test | Two mechanisms to restore and verify |
| Interaction | One desktop axis | Activity axis; can remember a virtual desktop per Activity, requiring restart | Remember-current-desktop option exists; precise window behavior needs later controlled verification |
| Future configuration | KWin virtual-desktop settings and global shortcuts; window rules only if placement is desired | Activities settings, activity shortcuts, Plasma containments | Both plus interaction setting |
| Rollback/portability | Four names and bindings; portable intent maps to common workspace metaphor | Activity IDs and widget associations raise restore complexity; KDE-specific | Highest state and rollback complexity |

KDE documents virtual desktop naming and pager/navigation behavior in its
[Virtual Desktops manual](https://docs.kde.org/stable_kf6/en/kwin/kcontrol/desktop/index.html).
KDE documents Activity names, shortcuts, and the **remember Current virtual
desktop for each activity** setting, including its restart requirement, in
the [Activities settings manual](https://docs.kde.org/stable_kf6/en/plasma-desktop/kcontrol/kcmactivities/index.html).
Its [Plasma handbook](https://docs.kde.org/stable_kf6/en/plasma-desktop/plasma-desktop/activities-interface.html)
distinguishes window-oriented virtual desktops from widget-oriented
Activities. The [window-rule attributes](https://docs.kde.org/stable_kf6/en/kwin/kcontrol/windowspecific/attributes.html)
can place a window on a virtual desktop or Activity. KDE's
[Plasma scripting API](https://develop.kde.org/docs/plasma/scripting/api/)
states that Activities share panels. These are current stable KF6 pages, but
some page revision labels still refer to Plasma 5; local Plasma 6 behavior
is not thereby proven. The local audit will only collect a numeric desktop
count, not names, Activity IDs, or placement rules.

The recommendation does not promise automatic per-application placement,
independent panels, or reliable application session restoration. Future
verification must decide whether these are needed, choose shortcut bindings,
and test persistence under a separately authorized change lifecycle.
