# KWin 6.7.5 workspace mutation mechanism

Selected mechanism: the local `org.kde.KWin.VirtualDesktopManager` D-Bus
interface at `/VirtualDesktopManager`, using `createDesktop(uint,string)`,
`setDesktopName(string,string)`, and `removeDesktop(string)`. The interface
provides `count`, `rows`, `current`, and ordered `desktops` properties. A
read-only introspection on this workstation confirmed these signatures on
2026-09-29. This D-Bus surface is **source-exposed implementation detail**,
not a KDE documented stability promise. The [official KWin scripting API](https://develop.kde.org/docs/plasma/kwin/api/)
documents equivalent create/remove/name operations, and the
[Virtual Desktops manual](https://docs.kde.org/stable_kf6/en/kwin/kcontrol/desktop/index.html)
documents the user-facing behavior. The script installation route documented
in the [KWin scripting tutorial](https://develop.kde.org/docs/plasma/kwin/)
requires plugin configuration and reconfigure; it would expand this pilot's
scope, so it is not selected.

The exact [KWin v6.7.5 D-Bus source](https://github.com/KDE/kwin/blob/v6.7.5/src/dbusinterface.h#L166-L225)
and [implementation](https://github.com/KDE/kwin/blob/v6.7.5/src/dbusinterface.cpp#L273-L419)
show the methods and property mapping. The
[v6.7.5 virtual desktop implementation](https://github.com/KDE/kwin/blob/v6.7.5/src/virtualdesktops.cpp#L416-L486)
inserts new desktops at requested positions, generates IDs, retains the
original desktop, and removes by ID. Its [load/save code](https://github.com/KDE/kwin/blob/v6.7.5/src/virtualdesktops.cpp#L641-L708)
shows the exact `Desktops` keys this operation can write: `Number`, `Rows`,
and `Id_1`–`Id_4` and `Name_1`–`Name_4`. It also shows that adding/removing
desktops can turn absent keys into present keys. Backup and rollback must
preserve presence separately from value for precisely those ten keys.

For this one-desktop pilot, keep the original desktop ID at position zero;
rename it, then append three desktops in order. The original is the active
desktop, so no switch is requested. Check each creation against an independent
D-Bus property read. On failure, remove only the appended IDs in reverse,
restore the original name, then restore the exact key presence/values through
KConfig key operations. Verify runtime count/order/name/ID/current/rows and
the exact backed-up config keys. No KWin/Plasma restart or reconfigure is
needed by the selected D-Bus path. The final authorized plan must reject a
different KWin version, a changed pre-state, a different count/row layout, or
an inaccessible property/config key.

This source-backed path has **not** been exercised on the live session.
Private desktop names and IDs belong only in ignored local backup material.
Rollback of windows moved onto newly created desktops during the pilot is
outside the exact configuration restore guarantee; the source shows removal
changes the active desktop, but window placement after removal needs a
separate controlled check. Live apply remains prohibited in Batch 004.
