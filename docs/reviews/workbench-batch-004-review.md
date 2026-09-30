# Batch 004 review and authorization gate

Date: 2026-09-29. This batch prepared a four-workspace KWin pilot and ended
before any live apply.

## Checkpoints and verification

1. `f5ac963` — validated mutation transaction model.
2. `8f89582` — narrow private backup and rollback substrate.
3. `05d2561` — source-backed KWin desktop adapter and fixture tests.
4. `76d5a74` — exact fixture authorization and dry-run gate.
5. `9674b5d` — fixture lifecycle proof and sanitized live dry-run.
6. This review-gate commit; its hash is available in the final batch report.

The complete `python3 -m unittest discover -s tests -q` suite passed:
**64 tests, zero failures or errors**. `git diff --check` passed. Coverage
includes transaction validation and invalid transitions; unknown pre-state;
backup permissions, symlink/path escape, absent values, corruption, repeated
restore, read/write failure; KWin fixture ordering and restoration; missing,
wrong, stale, cross-transaction, and changed-plan authorization; runtime and
config drift; dry-run, duplicate apply, and live-backend rejection. Failure
injected on the second desktop creation left partial fixture state and then
restored the exact fixture runtime/config state. No fixture test connected to
the live user bus.

## Transaction and authorization model

A transaction records a stable ID, adapter, logical outcome, exact
preconditions, typed operations, backup allowlist, verification checks,
rollback actions, authorization fingerprint, and explicit lifecycle status.
The statuses cover planned, authorization-required, authorized,
backup-created, applied, verified, verification-failed, rolled-back,
rollback-failed, and aborted. Invalid transitions and unknown required state
block mutation. The SHA-256 plan fingerprint includes the transaction ID,
runtime pre-state digest, exact allowlisted config pre-state digest, operations,
backup scope, verification, and rollback. Any change invalidates a previous
authorization. A fresh pre-state check occurs before fixture apply. The
Batch 004 runner accepts only a fixture backend and a fixture-only
authorization object. There is no live apply command, live backend, or
production authorization issuer; a generic batch request cannot cross the
live gate.

## Backup privacy and rollback

Only ignored `.workbench/backups/` is accepted for local backup material.
Directories use mode 0700 and files mode 0600. IDs and paths are validated;
existing files and symlinks are rejected. Backups store present/absent state
separately from values and bind transaction ID to fingerprint. Integrity and
identity failures block restoration. The pilot would back up the original
desktop runtime ID, name, current ID, rows, and presence/value of only ten
`Desktops` keys: `Number`, `Rows`, `Id_1`–`Id_4`, `Name_1`–`Name_4`.
An `Id_5` absence guard blocks a KWin save-loop side effect outside this
scope. Rollback removes newly created IDs in reverse, restores the original
name and exact key presence/values, and verifies both runtime and config.
Partial restoration reports `rollback-failed` with affected key IDs, never
private values. The live pre-state probe files remained ignored and were
confirmed mode 0600 under a mode 0700 directory.

## KDE mechanism and evidence

The selected mechanism for local KWin **6.7.5** is its
`org.kde.KWin.VirtualDesktopManager` session D-Bus interface. Read-only local
introspection confirmed the source-defined create, rename, remove methods
and count, ordered desktops, current, and rows properties. The
[official KWin scripting API](https://develop.kde.org/docs/plasma/kwin/api/)
documents equivalent virtual desktop operations. The precise D-Bus methods
are source-exposed implementation detail in [KWin v6.7.5](https://github.com/KDE/kwin/blob/v6.7.5/src/dbusinterface.cpp#L273-L419),
and [KWin's save/load implementation](https://github.com/KDE/kwin/blob/v6.7.5/src/virtualdesktops.cpp#L641-L708)
establishes the exact config keys and absent-key issue. The
[mechanism record](../../adapters/kde-workspace-mutation.md) separates these
sources. Direct D-Bus operations do not require KWin/Plasma restart or
reconfigure. The documented script installation route would change plugin
configuration and is outside this pilot.

## Pilot and live dry-run

The [fixture and dry-run proof](workbench-batch-004-pilot-proof.md) specifies
one transaction: retain the existing original desktop and make ordered
**Development**, **General**, **Office**, **Creative**. The real read-only
probe found KWin 6.7.5, one desktop, one row, and the sole desktop current.
Its private name and ID are held only in ignored local material. The dry-run
status was `authorization-required` for transaction
`kde-four-workspaces-v1`, fingerprint
`67b55bbe399a0eee08843d5b2ae86b83c95da3651c0a1c9f4bc0232e5b9d7963`.
The runtime digest is
`684b42ec9a05d16974b72cbb87771bc0a9dd3cc9dd061e6652ece7f70917d865`.
The fingerprint is an observation-bound review identifier, not approval.
The separate [pilot authorization sheet](workbench-batch-004-workspace-pilot.md)
summarizes the exact proposed change and stop gate.

## Remaining risks and gate

The D-Bus surface is not promised stable across KWin releases. A future
executor must confirm version and introspection again, use an independently
human-issued exact transaction authorization, and recheck runtime and config
pre-state immediately before backup/apply. No live apply/rollback has been
tested. Existing windows should remain on the retained active desktop during
creation; placement of windows moved to new desktops before a rollback is
unverified. Persistence across logout/reboot remains untested. The pilot
does not change Activities, panels, widgets, shortcuts, KScreen, window
rules, or unrelated settings.

**No live virtual desktop or other desktop/system mutation occurred.** The
batch stops at the human authorization gate. The pre-existing untracked HP
Envy experimental-kernel directory was not touched.
