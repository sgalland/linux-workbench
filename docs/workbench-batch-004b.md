# Workbench Batch 004B — Live Four-Workspace Pilot Executor

Purpose: bridge the reviewed Batch 004 four-workspace transaction from fixture-only execution to a production-capable, narrowly scoped live executor. Implement and test the live KWin backend, local human authorization artifact, live preflight, backup, apply/verify/rollback orchestration, and operator commands.

**This batch still does not authorize or execute the live workspace mutation.** It ends with executable capability prepared and a fresh human authorization gate.

Complete jobs in order, make one clean checkpoint commit after each job, continue automatically while tests remain green, and stop at the final gate.

## Global rules

- Read AGENTS.md, docs/safety-model.md, docs/workbench-batch-004.md, docs/reviews/workbench-batch-004-review.md, docs/reviews/workbench-batch-004-workspace-pilot.md, workbenchlib/control.py, workbenchlib/transaction.py, workbenchlib/backup.py, adapters/kde_workspace.py, and adapters/kde-workspace-mutation.md first.
- No sudo, package changes, service changes, KWin/Plasma restart, or unrelated desktop/system changes.
- Do not run the live apply command during this batch.
- Do not create a real production authorization record during this batch.
- Do not rename/create/remove live virtual desktops during this batch.
- Live D-Bus writes and live config restoration code may be implemented, but tests must inject fake runners/backends and may not connect mutating calls to the real user session.
- Read-only live preflight is allowed.
- Preserve the exact pilot scope: retain the existing desktop/ID/current desktop, rename it Development, append General, Office, Creative, keep one row, and touch nothing else.
- Any state/version/interface drift must block execution and require re-plan/review.
- Keep all authorization/backup/run material under ignored .workbench/ with restrictive permissions. Never commit or print private desktop IDs/names or config values.
- Do not touch machines/hp-envy/experimental-kernel/.

## Reviewed pilot identity

Transaction ID: kde-four-workspaces-v1

Batch 004 reviewed fingerprint:
67b55bbe399a0eee08843d5b2ae86b83c95da3651c0a1c9f4bc0232e5b9d7963

That fingerprint is historical review evidence, not a value to hard-code as permanently valid. A fresh preflight must reconstruct the plan from current live state. If the resulting fingerprint differs, do not authorize or apply it under the old review.

Target names in order:
1. Development
2. General
3. Office
4. Creative

## Job 1 — Narrow live KWin backend

Implement a production backend for adapters/kde_workspace.py that satisfies the existing Backend protocol for exactly this pilot.

Requirements:
- session D-Bus only; no system bus and no privilege escalation;
- exact KWin service/object/interface names from the source-backed Batch 004 mechanism record;
- read-only inspect obtains only ordered desktop IDs/names, current desktop, and rows;
- mutators expose only the operations needed by this pilot: rename desktop, create desktop at position, remove desktop;
- exact allowlisted Desktops config reads/writes needed by backup/rollback only;
- subprocess/D-Bus invocation uses fixed argv or a typed runner; never shell interpolation;
- validate returned types/count/order and reject malformed or extra-unexpected state;
- confirm KWin runtime version 6.7.5 and the expected VirtualDesktopManager introspection surface immediately before any live mutation;
- reject unsupported version/interface rather than guessing compatibility;
- no generic arbitrary D-Bus method facility in the public Workbench API.

If a command-line D-Bus client/config helper is used, model it behind an injected runner so all mutation paths are unit-testable without a live bus.

Add tests for inspect, rename/create/remove serialization, malformed replies, command failure, version mismatch, missing interface/method/property, and config key present/absent behavior.

Do not call live mutators.

Checkpoint commit.

## Job 2 — Production authorization artifact

Replace the fixture-only authorization limitation with a separate production authorization type and issuer while retaining fixture authorization unchanged.

The production authorization must:
- be specific to transaction ID, exact plan fingerprint, runtime/config pre-state digests, and pilot scope;
- be one-time/consumable;
- live only under ignored .workbench/authorizations/ with directory mode 0700 and file mode 0600 where supported;
- contain no private desktop names/IDs/config values beyond non-reversible digests and safe transaction metadata;
- have integrity validation;
- expire or become invalid on pre-state/plan drift;
- never be reusable across transaction IDs or fingerprints.

Human issuance must require an interactive TTY and explicit entry of both the transaction ID and current fingerprint, or an equivalently strong transaction-specific confirmation. Refuse piped stdin/non-TTY issuance. A generic --yes, environment variable, batch flag, config setting, or API that an unattended batch can trivially use must not authorize production mutation.

The batch itself must not issue a production authorization.

Add tests using injected TTY/input abstractions; no test may require a real terminal.

Checkpoint commit.

## Job 3 — Production lifecycle runner

Implement the production counterpart to run_fixture, narrowly scoped to the KDE workspace pilot.

Required order:
1. reconstruct/read the exact current live plan;
2. validate KWin version and D-Bus interface;
3. validate authorization identity/fingerprint/pre-state;
4. consume/lock the one-time authorization so parallel or repeated apply cannot reuse it;
5. create the narrow backup under .workbench/backups/;
6. recheck pre-state after backup and immediately before first mutation;
7. apply one typed operation at a time;
8. verify after each operation using live read-back;
9. perform independent final runtime/config verification;
10. on any apply/verification failure, automatically attempt rollback from the transaction backup;
11. independently verify rollback;
12. write a private local result record without private values in public output.

Additional safety:
- use a lock under ignored .workbench/ to prevent concurrent Workbench mutations;
- signal/interruption handling must not silently report success; once mutation begins, either complete verification or enter rollback/recovery-required handling;
- duplicate apply of an already consumed authorization must fail;
- a successful apply must retain its backup for later explicit rollback until the pilot is accepted;
- no automatic cleanup of recovery material at process exit.

Public CLI output may expose transaction ID, fingerprint, status, safe step labels, backup ID, and failure categories, but not private backup values/IDs/names.

Exercise this runner only with a fake live backend/runner in this batch.

Add failure injection before backup, after backup, after rename, after each create, during final verify, during rollback, and for interruption/concurrency cases.

Checkpoint commit.

## Job 4 — Operator CLI: preflight, authorize, apply, verify, rollback

Expose a narrow operator workflow without creating a generic unsafe apply surface.

Suggested commands may be adjusted for clarity, but must preserve separate acts:

    ./workbench workspace-pilot preflight
    ./workbench workspace-pilot authorize <fingerprint>
    ./workbench workspace-pilot apply <fingerprint>
    ./workbench workspace-pilot verify
    ./workbench workspace-pilot rollback <backup-id>

Semantics:
- preflight is read-only and prints a sanitized current plan/fingerprint/risk summary;
- authorize is interactive-only and creates the one-time local production authorization;
- apply requires that exact local authorization and performs the lifecycle runner;
- verify is read-only;
- rollback restores only from a matching valid pilot backup and validates current state sufficiently to avoid clobbering unrelated/new state;
- rollback must not become a generic arbitrary KDE config restore command.

Do not add broad package/service/desktop apply commands.

CLI help and docs must state that generating preflight or running this batch is not authorization.

All live mutating commands must refuse execution in clearly unsupported/non-KDE/non-user-session contexts.

Tests must prove the CLI cannot apply with no auth, wrong fingerprint, stale auth, consumed auth, noninteractive fake authorization, unsupported KWin, or drifted pre-state.

Do not invoke authorize/apply/rollback against the real session in this batch.

Checkpoint commit.

## Job 5 — Fresh live read-only preflight and operator runbook

Run only:

    ./workbench workspace-pilot preflight

or its final read-only equivalent in the normal user session.

Do not authorize or apply.

Compare the newly generated transaction ID/fingerprint/runtime/config digests to the Batch 004 reviewed values.

If the fingerprint differs:
- explain the drift using only safe classifications;
- produce a new sanitized review sheet;
- require human review of the new fingerprint.

If it matches:
- record that the originally reviewed plan still matches current pre-state.

Create docs/reviews/workbench-batch-004b-workspace-pilot.md containing:
- transaction ID;
- current fingerprint;
- whether it matches Batch 004;
- KWin version/interface check result;
- proposed exact logical change;
- backup scope by logical key names only;
- verification sequence;
- rollback sequence;
- operator commands to be used after explicit approval;
- expected visible desktop effect;
- remaining live risks.

Do not include private desktop ID/name/config values.

Checkpoint commit.

## Job 6 — Batch 004B review and stop gate

Run the complete automated test suite and git diff --check.

Create docs/reviews/workbench-batch-004b-review.md containing:
- checkpoint commits;
- test totals/results;
- live backend scope and version/interface guards;
- production authorization design;
- one-time/concurrency/interruption protections;
- backup/apply/verify/rollback orchestration;
- failure-injection results;
- fresh read-only preflight result and fingerprint match/drift status;
- exact next operator steps after human approval;
- remaining risks;
- explicit confirmation that no production authorization was issued and no live mutation occurred.

Update docs/safety-model.md/AGENTS.md/roadmap only as needed to accurately describe the capability boundary.

Stop here.

Do not run workspace-pilot authorize.
Do not run workspace-pilot apply.
Do not run workspace-pilot rollback against the live session.
Do not interpret this batch request as approval.

## Expected checkpoint sequence

1. narrow live KWin backend
2. production authorization artifact
3. production lifecycle runner
4. operator CLI
5. fresh read-only live preflight + runbook
6. Batch 004B review + human authorization stop gate

If safe production execution cannot be implemented without broadening beyond the reviewed KWin 6.7.5 D-Bus/config surface, stop and report the blocker rather than weakening the gate.
