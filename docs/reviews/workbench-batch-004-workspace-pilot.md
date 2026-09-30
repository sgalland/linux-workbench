# Human review sheet: four KWin virtual desktops

**Status:** prepared dry-run only; live apply is not authorized or available
in Batch 004.

**Transaction:** `kde-four-workspaces-v1`  
**Reviewed plan fingerprint:**
`67b55bbe399a0eee08843d5b2ae86b83c95da3651c0a1c9f4bc0232e5b9d7963`  
**Runtime pre-state digest:**
`684b42ec9a05d16974b72cbb87771bc0a9dd3cc9dd061e6652ece7f70917d865`

Observed KWin 6.7.5 has one current desktop in one row. Its name and ID are
private and held only in ignored local material. The proposed change keeps
that desktop and its ID, renames it **Development**, and appends three
desktops in order: **General**, **Office**, **Creative**. The current desktop
remains the original. Activities, panels, widgets, shortcuts, KScreen,
window rules, and unrelated settings are outside scope.

The proposed mechanism uses KWin's source-exposed virtual desktop D-Bus
interface. It requires no KWin/Plasma restart or reconfigure. Before any
future apply, make a mode 0600 local backup under `.workbench/backups/` of
the original runtime desktop ID/name/current/rows and exact presence/value
of `Desktops/Number`, `Rows`, `Id_1`–`Id_4`, `Name_1`–`Name_4`. Require
`Id_5` absent. Then rename the original and append one desktop at a time,
checking order, names, IDs, current desktop, and rows after each action.
Verify the final four names and allowlisted config state. On any failure,
remove only newly created IDs in reverse, restore the original name and
backed-up key presence/values, and verify exact restoration. Report partial
rollback honestly.

A later live run requires a new human authorization bound to this exact
transaction and fingerprint, plus a fresh runtime/config pre-state match.
Any drift requires a new plan and review. The current batch request and this
sheet are not authorization. No live apply was run.
