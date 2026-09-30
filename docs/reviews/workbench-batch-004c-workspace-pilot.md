# Batch 004C workspace pilot: fresh read-only preflight

Date: 2026-09-30. Status: review only; production authorization is required before any mutation.

- Transaction ID: `kde-four-workspaces-v1`
- Fresh fingerprint: `67b55bbe399a0eee08843d5b2ae86b83c95da3651c0a1c9f4bc0232e5b9d7963`
- Batch 004 fingerprint: identical. No fingerprint difference requires classification. The current runtime/config pre-state still binds the reviewed plan.
- KWin: exactly 6.7.5. `org.kde.KWin.VirtualDesktopManager` validation passed: declared `desktops` signature `a(iss)`, runtime reply `a(uss)`, and the other reviewed members/signatures matched. The source-backed distinction is in [the adapter evidence record](../../adapters/kde-kwin-675-dbus-signatures.md).
- Observed scope: one desktop, one row. The `Id_5` exclusion and allowlisted config reads passed.

The exact logical target keeps the original desktop, ID, and current selection; renames it **Development**; then appends **General**, **Office**, and **Creative** in that order. It keeps one row. No activities, panels, widgets, shortcuts, display settings, window rules, or unrelated settings are part of this transaction.

Backup scope names only: runtime desktop ID, name, current ID, and rows; `Desktops/Number`, `Desktops/Rows`, `Desktops/Id_1`–`Id_4`, and `Desktops/Name_1`–`Name_4`, including key presence. `Id_5` must remain absent.

After separate explicit human approval, the executor's sequence is: recheck the exact version/interface and pre-state; consume one-time authorization under a lock; take the narrow backup; recheck pre-state; rename and verify by read-back; append each desktop and verify by read-back; independently verify final runtime order, IDs, current desktop, rows, and allowlisted config. If any step after mutation fails, remove only appended desktops in reverse, restore the original name and backed-up config key presence/values, and verify restoration. Retain the backup and report any incomplete rollback.

Operator commands after that approval and a fresh matching preflight:

```text
./workbench workspace-pilot preflight
./workbench workspace-pilot authorize 67b55bbe399a0eee08843d5b2ae86b83c95da3651c0a1c9f4bc0232e5b9d7963
./workbench workspace-pilot apply 67b55bbe399a0eee08843d5b2ae86b83c95da3651c0a1c9f4bc0232e5b9d7963
./workbench workspace-pilot verify
./workbench workspace-pilot rollback kde-four-workspaces-v1
```

The rollback command is for an authorized recovery decision or failed verification, using the matching pilot backup. Remaining live risks: the D-Bus surface is an implementation detail; KWin or pre-state drift will block execution; interruption or a failed restore may require manual recovery from the retained backup; window placement after removing newly created desktops is outside the config restore guarantee. This preflight issued no authorization and made no live change.
