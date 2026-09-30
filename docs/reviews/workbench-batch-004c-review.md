# Batch 004C review and human authorization stop gate

Date: 2026-09-30. Batch complete through read-only preflight. The pilot remains at the human authorization gate.

## Checkpoints and verification

1. `e1314bf` — KWin v6.7.5 source evidence and exact compatibility rule.
2. `09ae187` — backend reconciliation and regression tests.
3. `0724822` — full safety suite and targeted preflight guard test.
4. `e842872` — fresh live read-only preflight and sanitized review sheet.
5. This review checkpoint — final handoff and stop gate.

`python3 -m unittest discover -s tests -q` passed **82 tests**. This includes Batch 004/004B transaction lifecycle, fingerprint and stale-state binding, one-time authorization, backup scope and integrity, fixture/live separation, failure injection, concurrency, interruption, drift, verification, and rollback tests. The new regressions passed for the exact declared/runtime signature pair; wrong runtime signatures; changed introspection, version, method, or property; negative, non-integer, or non-contiguous positions; malformed rows/count/current; and preflight interface drift. `git diff --check` passed.

## Exact KWin 6.7.5 evidence and rule

The [v6.7.5 interface XML](https://github.com/KDE/kwin/blob/v6.7.5/src/org.kde.KWin.VirtualDesktopManager.xml) declares `desktops` as `a(iss)`. The [v6.7.5 C++ struct](https://github.com/KDE/kwin/blob/v6.7.5/src/virtualdesktopsdbustypes.h) declares `uint position`, `QString id`, and `QString name`; the [v6.7.5 marshaller](https://github.com/KDE/kwin/blob/v6.7.5/src/virtualdesktopsdbustypes.cpp) writes them in that order. This establishes an `a(uss)` runtime wire structure. The live property reply was observed as `a(uss)` in Batch 004B and accepted by the fresh read-only preflight.

For exactly KWin 6.7.5 and `org.kde.KWin.VirtualDesktopManager.desktops`, introspection must advertise `a(iss)` and the live reply must be `a(uss)`. `count` and `rows` must be `u`, `current` must be `s`, and `createDesktop(us)`, `setDesktopName(ss)`, and `removeDesktop(s)` must have no return values. Desktop positions must be non-negative integers in exact order `0..count-1`; IDs/names must be strings, count must match, and current must identify an observed desktop. Wrong version, changed reviewed surface, wrong reply signature, or malformed payload fails closed. This exception does not apply to other versions or interfaces. The [adapter evidence record](../../adapters/kde-kwin-675-dbus-signatures.md) has the source links and applicability.

## Fresh preflight and reviewed plan

`./workbench workspace-pilot preflight` passed in the normal KDE user session. It confirmed KWin 6.7.5, the reviewed interface, the `a(uss)` property reply, one desktop in one row, and the narrow runtime/config pre-state. Transaction ID: `kde-four-workspaces-v1`. Fresh fingerprint: `67b55bbe399a0eee08843d5b2ae86b83c95da3651c0a1c9f4bc0232e5b9d7963`. It **matches** the Batch 004 reviewed fingerprint, so the reviewed plan has not changed materially. See the [sanitized pilot sheet](workbench-batch-004c-workspace-pilot.md) for target names, backup scope, verification, rollback, and remaining live risks.

After separate explicit human approval bound to this transaction, fingerprint, and fresh pre-state, the operator sequence is:

```text
./workbench workspace-pilot preflight
./workbench workspace-pilot authorize 67b55bbe399a0eee08843d5b2ae86b83c95da3651c0a1c9f4bc0232e5b9d7963
./workbench workspace-pilot apply 67b55bbe399a0eee08843d5b2ae86b83c95da3651c0a1c9f4bc0232e5b9d7963
./workbench workspace-pilot verify
./workbench workspace-pilot rollback kde-four-workspaces-v1
```

Rollback is only for a failed verification or a separately authorized recovery decision. Recheck the preflight and review again if state or fingerprint changes. Remaining risks are KWin's implementation-detail D-Bus surface, pre-state drift, interruption or failed restoration requiring manual recovery, and window placement after newly created desktops are removed.

**Stop here.** This batch issued no production authorization and performed no live desktop mutation. The Batch 004B preflight stop remains historically correct; its source-resolved status is recorded in the [blocker record](workbench-batch-004b-interface-blocker.md).
