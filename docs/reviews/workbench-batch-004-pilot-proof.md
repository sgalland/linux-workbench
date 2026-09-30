# Batch 004 Job 5: four-workspace pilot proof

## Exact logical pilot

On the locally observed single KWin desktop, retain its ID and position,
rename it **Development**, then append **General**, **Office**, and
**Creative** at positions 1, 2, and 3. No Activity, panel, widget, shortcut,
KScreen, window rule, or other KWin setting is in scope. The current desktop
must remain the retained original ID. Rows must remain one.

## Fixture proof

The test backend exercises inspect → plan → backup → test-only authorize →
apply → verify → rollback → restoration verify. The fixture starts with one
desktop, a private fixture name, one row, and absent `Desktops` keys. The
result is four names in order, then the exact original ID, name, current
desktop, row count, and key presence/values after rollback. A second rollback
also succeeds. A failure injected on the second creation leaves a partial
rename and first created desktop; automatic rollback restores the fixture.
Authorization rejection tests cover missing, wrong, stale, cross-transaction,
and changed-plan material. No fixture test talks to the live session.

## Sanitized live dry-run

Read-only probe date: 2026-09-29. KWin reports **6.7.5**. Its local D-Bus
virtual-desktop interface matches the source-backed signatures; the ordered
desktop property reports **one desktop**, **one row**, and a current desktop
matching that one desktop. The probe read only the four KWin desktop
properties, ten exact `kwinrc` `Desktops` backup keys, and an `Id_5` absence
guard. Private name, ID, and key
values were saved only under ignored `.workbench/backups/` with user-only
permissions and are not reproduced here.

Dry-run status: **authorization-required**. Transaction ID:
`kde-four-workspaces-v1`. Fingerprint:
`67b55bbe399a0eee08843d5b2ae86b83c95da3651c0a1c9f4bc0232e5b9d7963`.
The runtime pre-state digest is
`684b42ec9a05d16974b72cbb87771bc0a9dd3cc9dd061e6652ece7f70917d865`.
These identify this observation; a change in the exact plan or pre-state
invalidates them. They are **not authorization**.

The future backup scope is the runtime original ID, name, current ID, rows,
plus presence and value for `Desktops/Number`, `Rows`, `Id_1`–`Id_4`, and
`Name_1`–`Name_4`. The D-Bus mechanism needs no KWin/Plasma restart or
reconfigure. Verification reads ordered desktops, IDs, names, current ID,
and rows independently from D-Bus and checks the exact allowlisted config
keys. On failed application or verification, remove only created IDs in
reverse, restore the original name, then restore allowlisted key
presence/values and verify both runtime and config state. Partial rollback
must be reported as failure.

The original desktop remains active, so existing windows on it are expected
to stay there during creation. Window placement if the user moves windows to
new desktops before rollback remains unverified. D-Bus is source-exposed
implementation detail rather than a KDE stability promise; version and
introspection must be checked again immediately before any separately
authorized future apply. No live apply or other desktop/system mutation was
performed in this batch.
