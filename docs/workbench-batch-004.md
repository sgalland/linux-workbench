# Workbench Batch 004 — Controlled Mutation Framework + Four-Workspace Pilot

Purpose: design and implement the v0.5 mutation framework, prove its safety lifecycle with fixtures/sandboxes, and prepare one exact live KDE pilot: changing the current single KWin virtual desktop into four named desktops — Development, General, Office, Creative.

**This batch does not authorize or perform the live desktop change.** It ends at a human authorization gate with an exact plan, backup scope, verification procedure, and rollback procedure.

Complete jobs in order, make one clean checkpoint commit after each job, continue automatically while tests remain green, and stop at the final authorization gate.

## Global rules

- Read AGENTS.md, docs/safety-model.md, docs/roadmap.md, docs/reviews/workbench-batch-003-review.md, docs/reviews/workbench-batch-003-kde-feasibility.md, spec/desktop-intent.candidate.json, and adapters/kde-desktop.candidate.json first.
- No sudo.
- No package installation/removal.
- No service, boot, networking, audio, panel, widget, shortcut, Activity, KScreen, or other unrelated desktop changes.
- Do not change the live virtual-desktop count, names, rows, current desktop, window placement, or KWin configuration during this batch.
- Do not reload/restart KWin or Plasma during this batch.
- Do not invoke a live mutating D-Bus/KWin API, kwriteconfig write, config edit, or equivalent against the real user session.
- Repository code/documentation changes are allowed. Mutation behavior may be exercised only against fixtures, temporary files, mock adapters, or explicitly isolated test state that is not the live desktop.
- The existing read-only inspect/compare/plan commands must remain safe and compatible.
- Never treat generation of a plan, existence of an apply-capable code path, or execution of this batch as authorization to mutate the system.
- Do not touch the pre-existing untracked machines/hp-envy/experimental-kernel/ directory.

## Pilot target

The candidate pilot is one coherent KDE configuration transaction:

Current observed state:
- one KWin virtual desktop;
- existing desktop name(s) not yet read;
- no live mutation authorized.

Proposed target:
1. Development
2. General
3. Office
4. Creative

The pilot must not change Activities, panels, widgets, shortcuts, KScreen, window rules, application settings, or unrelated KWin behavior.

KDE officially documents adding/removing/renaming virtual desktops. KWin's current scripting API also exposes virtual desktop objects and create/remove desktop capabilities. Do not assume either is the correct Workbench mutation mechanism until Job 3 establishes a supported, reversible method for the locally observed KDE/KWin version.

## Job 1 — Mutation transaction model

Implement a target-independent transaction model for the lifecycle:

inspect → plan → backup → apply → verify → rollback

The model must represent at minimum:
- stable transaction/pilot ID;
- target adapter;
- exact logical outcomes being changed;
- preconditions;
- planned operations;
- backup specification;
- verification checks;
- rollback operations;
- authorization state;
- transaction/result status.

Required status distinctions should include at least:
- planned;
- authorization-required;
- authorized;
- backup-created;
- applied;
- verified;
- verification-failed;
- rolled-back;
- rollback-failed;
- aborted.

Design conservatively: failed preconditions or unknown required state must block mutation.

Do not make arbitrary shell command strings the mutation model. Operations should be typed adapter actions with separately validated parameters.

Add validation/state-transition tests, including invalid transitions and unknown-precondition blocking.

Checkpoint commit.

## Job 2 — Local backup and rollback substrate

Implement the generic backup substrate needed by future adapters.

Requirements:
- backups live only under an ignored .workbench/backups/ area;
- create backup directories/files with restrictive user-only permissions where supported;
- back up only explicitly allowlisted state needed for the transaction;
- preserve the distinction between a key/value being present and absent;
- never print backup values to normal CLI output;
- never commit backups;
- include transaction metadata sufficient to select the correct rollback material without exposing private values;
- reject symlink/path escape attacks and paths outside the approved backup root;
- backup failure must block apply;
- rollback must be idempotent where practical and report partial/failure states honestly.

Do not copy an entire KDE configuration file merely because it is convenient. For the workspace pilot, the eventual backup must be limited to the exact virtual-desktop state required for restoration.

Exercise backup/restore only against fixtures or temporary files in this job.

Add permission, path-safety, missing-value, corrupted-backup, double-rollback, and failure-injection tests.

Checkpoint commit.

## Job 3 — KDE virtual-desktop mutation adapter design

Establish the exact KDE mechanism for changing and restoring named virtual desktops on the locally relevant Plasma/KWin generation.

Use current official KDE documentation and, where needed, current KDE/KWin source/API evidence. Clearly distinguish documented public API from implementation detail.

Evaluate candidate mechanisms such as:
- supported KWin virtual-desktop APIs;
- KDE configuration tooling plus a documented/safe reconfigure mechanism;
- another KDE-supported interface.

Do not use undocumented config-key assumptions without source evidence. Do not write live config while investigating.

Select one mechanism only if it can satisfy:
- exact pre-state capture;
- deterministic creation/count/name ordering;
- safe handling of the currently active desktop;
- preservation of unrelated KWin settings;
- verification from an independent read path where feasible;
- exact rollback to the pre-state;
- no KWin/Plasma restart unless the final authorized plan explicitly requires it and explains the consequence.

Implement the KDE adapter behind the generic transaction interface, but exercise it only with mocks/fixtures/test doubles in this batch.

Record version applicability and assumptions. If no sufficiently safe supported mechanism is established, stop the batch at this job and report the blocker rather than implementing a speculative mutator.

Checkpoint commit.

## Job 4 — Explicit authorization and dry-run gate

Add the command/control boundary for mutation.

Required behavior:
- existing inspect/compare/plan commands remain read-only;
- planning a mutation produces an immutable/reviewable transaction description or fingerprint;
- live apply cannot occur implicitly from plan generation;
- authorization must be explicit, transaction-specific, and tied to the exact reviewed plan so a changed plan invalidates prior authorization;
- stale pre-state invalidates authorization and requires re-planning;
- dry-run performs precondition/backup-scope/verification planning without mutation;
- non-interactive automation must not be able to convert a generic “run the batch” instruction into authorization for a live change.

Do not use a reusable global “yes to all” flag.

If an apply command is introduced, it must refuse to run without the exact transaction-specific authorization material and must not be invoked against the live session in this batch.

Add tests for:
- no authorization;
- wrong/stale authorization;
- plan fingerprint mismatch;
- pre-state drift after authorization;
- dry-run;
- duplicate apply;
- authorization cannot cross transaction IDs.

Update AGENTS.md and docs/safety-model.md as needed so the repository rule matches the implementation.

Checkpoint commit.

## Job 5 — Four-workspace pilot plan and fixture proof

Create the concrete pilot definition for:
- Development
- General
- Office
- Creative

Using only read-only live probes, capture the minimum allowlisted pre-state needed to construct the plan. If the current desktop names are required for exact rollback and may contain user-private text, keep them only in the ignored local transaction/backup material; public committed docs should state counts/status without exposing private names.

Run the entire transaction lifecycle against a fixture or mock KDE backend:
1. inspect;
2. plan;
3. backup;
4. authorize using test-only authorization;
5. apply to fixture;
6. verify;
7. rollback;
8. verify restoration.

Include failure injection after partial application and prove rollback behavior.

For the real workstation, run **dry-run only**. Generate a sanitized live pilot report describing:
- observed compatible KDE/KWin version/state;
- exact logical change;
- mutation mechanism;
- state that will be backed up;
- whether a restart/reconfigure is required;
- verification checks;
- rollback trigger and procedure;
- any expected effect on existing windows/current desktop;
- risks and unresolved unknowns.

Do not apply the live change.

Checkpoint commit.

## Job 6 — Batch 004 review + human authorization gate

Run the complete automated suite and git diff --check.

Create docs/reviews/workbench-batch-004-review.md containing:
- checkpoint commits;
- tests and failure-injection coverage;
- transaction-state model summary;
- backup privacy/path-safety summary;
- chosen KDE mutation mechanism and evidence;
- exact four-workspace pilot scope;
- sanitized live dry-run result;
- verification and rollback design;
- remaining risks/unknowns;
- explicit statement that the live desktop was not changed.

Create a separate sanitized authorization document, for example docs/reviews/workbench-batch-004-workspace-pilot.md, that is concise enough for human review before approval. It must identify the exact transaction/pilot version or fingerprint but must not contain secrets or private backup values.

Update docs/roadmap.md only to reflect that v0.5 machinery and the pilot are prepared but **not yet executed**.

Stop at the authorization gate.

Do not run live apply.
Do not rename/add/remove live virtual desktops.
Do not interpret this batch request as approval of the pilot.
Do not begin any other KDE mutation.

## Expected checkpoint sequence

1. mutation transaction model
2. local backup/rollback substrate
3. KDE virtual-desktop mutation adapter
4. transaction-specific authorization + dry-run gate
5. four-workspace fixture proof + live dry-run
6. Batch 004 review + human authorization gate

If the adapter cannot demonstrate exact rollback without relying on speculative KDE internals, stop before live planning and report that v0.5 needs a different pilot.
