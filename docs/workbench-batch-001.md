# Workbench Batch 001 — Inventory → Compare → Plan

Purpose: advance Linux Workbench from the current read-only v0.2 collector into a useful read-only inventory/comparison/planning loop. Complete jobs in order, make one checkpoint commit after each, continue automatically while tests are green, and stop at the final review gate.

## Batch rules

- Read AGENTS.md and the architecture, discovery, requirements, roadmap, and safety docs first.
- No sudo, package installation/removal, service changes, boot changes, networking/audio/KDE/settings mutation, or apply command.
- Never serialize secrets, arbitrary config contents, histories, account data, tokens, raw environment data, or raw probe output.
- Unknown/unavailable observations must never be treated as absence.
- Keep snapshots local under .workbench/inspections/ and ignored.
- Do not collect KScreen in this batch.
- Preserve ./workbench inspect compatibility.
- Use fixtures/tests rather than treating an agent sandbox as the real workstation.

## Job 1 — Package-managed software inventory

Extend inspect with normalized, read-only inventory for:
- explicitly installed Arch/CachyOS repository packages;
- explicitly installed foreign/AUR-style pacman packages;
- Flatpak applications.

Use fixed argv calls. Record stable package/app identifiers and source class only. Missing tools mean unknown/unavailable, never an empty installed set. Do not scan AppImages, arbitrary desktop files, Wine prefixes, game libraries, or JetBrains Toolbox internals yet.

Add parser/privacy/failure tests and update docs/discovery-format.md.

Checkpoint commit.

## Job 2 — Settings-surface inventory

Add an adapter-owned catalog of reviewed settings surfaces and discover only whether each surface exists.

Initial categories may include fish config presence, Git user-config presence, CachyOS/Arch package-management surfaces, and a small reviewed set of KDE Plasma config-file surfaces. KDE details belong in an adapter.

Record logical ID/category and present/absent/unknown only. Do not serialize home paths, file contents, arbitrary filenames, symlink targets, hashes, usernames, hostnames, or mtimes. Permission failures are unknown.

Add fixture tests proving presence-only checks never read file contents. Update architecture/discovery docs.

Checkpoint commit.

## Job 3 — Snapshot comparison

Add:

    ./workbench compare <older.json> <newer.json>

Requirements:
- validate schema versions;
- compare normalized facts only;
- classify added/removed/changed/unchanged/unknown;
- never call something removed when the newer probe is failed/unknown/not-collected;
- deterministic ordering;
- do not mutate inputs;
- constrain normal CLI inputs to .workbench/inspections/.

Test software changes, settings-surface changes, unknown-vs-removal, schema mismatch, unchanged snapshots, stable ordering, and path safety. Document semantics.

Checkpoint commit.

## Job 4 — Desired-state model

Define a machine-independent desired-state format under spec/.

It must express logical software IDs, required/optional intent, review categories, and settings surfaces intended for future management. Do not put distro package names, Flatpak IDs, KDE filenames, shell commands, or install commands in the abstract spec.

Add a CachyOS adapter mapping format from logical software IDs to repository package / foreign package / Flatpak identifiers. Data only; no installation behavior.

Use a small non-authoritative fixture/example rather than silently declaring all observed software desired. Add validation and architecture-boundary tests/docs.

Checkpoint commit.

## Job 5 — Read-only reconciliation planner

Add:

    ./workbench plan <desired-state> <snapshot>

Classify at least:
- satisfied;
- missing;
- observed-but-unmanaged;
- mapping-unavailable;
- observation-unknown;
- ambiguous/conflicting mapping.

A plan is a proposal only. Never execute package-manager mutation, change files, or add apply behavior. Unknown observation must suppress false install recommendations. Unmanaged observed software must not automatically produce removal proposals.

Add deterministic tests and document the safety boundary.

Checkpoint commit.

## Job 6 — Review gate

Run all tests and do a docs consistency pass. Confirm inspect/compare/plan are read-only and no mutation path exists.

Create docs/reviews/workbench-batch-001-review.md with:
- checkpoint commits;
- tests/results;
- implemented capabilities;
- known limitations;
- deferred inventory sources such as AppImage/manual installs, JetBrains Toolbox, Wine/game launchers;
- explicit confirmation that no system mutation occurred.

Keep HP Envy audio as a Workbench status/pointer to the dedicated research repo rather than duplicating the research.

Stop after this review gate. Do not begin KDE feasibility work or any controlled mutation without human review.
