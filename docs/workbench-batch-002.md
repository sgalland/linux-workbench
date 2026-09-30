# Workbench Batch 002 — Complete Inventory + Candidate Workstation Intent

Purpose: extend the read-only Workbench from package-only discovery into a useful inventory of this workstation's application ecosystem, then exercise the Batch 001 desired-state/planning model against a curated candidate workstation manifest. Complete jobs in order, checkpoint each job, continue automatically while tests are green, and stop at the final review gate.

## Global rules

- Read AGENTS.md, docs/reviews/workbench-batch-001-review.md, docs/discovery-format.md, spec/desired-state.md, and docs/roadmap.md first.
- No sudo, installs/removals, service changes, desktop changes, audio changes, boot changes, or apply behavior.
- Do not inspect arbitrary user files, browser data, documents, histories, credentials, tokens, Wine registry contents, save games, or arbitrary home-directory trees.
- Discovery must use fixed reviewed catalogs, fixed command argv, known vendor metadata, or narrowly scoped standard locations.
- Parse raw data in memory and serialize only normalized allowlisted identifiers/source classes.
- Paths, usernames, hostnames, timestamps, arbitrary filenames, launch arguments, URLs containing tokens, and raw metadata must not enter snapshots.
- Unknown/inaccessible observations remain unknown and never imply absence.
- Do not collect KScreen or begin KDE feasibility work.
- Do not touch the pre-existing untracked machines/hp-envy/experimental-kernel/ directory.
- Preserve all Batch 001 CLI behavior and safety semantics.

## Explicit workstation software candidates

The user has explicitly identified these applications/tools as desired or normally used on this workstation. Treat this list as input for logical IDs and review, not as proof of current installation and not as authorization to install anything:

- ChatGPT / Codex tooling
- Spotify
- Brave
- Blender
- Krita
- Inkscape
- Visual Studio Code
- Obsidian
- Godot
- JetBrains Toolbox
- PyCharm
- Rider
- CLion
- WebStorm
- AnyDesk
- GitHub CLI
- Insync
- ModernUO
- Ultima Online
- Star Trek Fleet Command
- GOG Galaxy

Do not invent required/optional intent where it is not established. Capture unresolved intent explicitly for human review.

## Job 1 — Targeted manual-software discovery framework

Add a read-only, adapter-owned catalog for software that may not appear in pacman/Flatpak inventory.

Supported evidence kinds should be narrowly scoped and fixture-testable, for example:
- known executable/command presence, retaining only present/absent/unknown;
- known desktop application IDs, matched against reviewed IDs only;
- known standard application markers or vendor directories, checked by exact reviewed relative location;
- vendor metadata parsers where a later job requires them.

Do not serialize executable paths, desktop Exec lines, arbitrary desktop-entry fields, directory listings, or unmatched application names.

Represent normalized results with stable logical/evidence IDs and a source class such as manual, vendor, launcher, or command. Keep evidence separate from desired intent.

Add privacy/path-safety/failure fixtures. Update docs/discovery-format.md.

Checkpoint commit.

## Job 2 — JetBrains Toolbox and IDE inventory

Implement targeted discovery for JetBrains Toolbox plus the user's usual IDEs:
- PyCharm
- Rider
- CLion
- WebStorm

Prefer Toolbox/vendor metadata if safely available; otherwise use reviewed exact product markers. Normalize only product identity, installed/not-installed/unknown, and a coarse source class. Version may be retained only if it is a normal public product version and parser tests prove paths/build metadata/private fields are discarded.

Do not crawl arbitrary JetBrains directories or serialize install paths, project lists, recent projects, account information, settings, plugins, license data, or Toolbox authentication data.

Integrate these observations into compare/plan semantics without breaking package/Flatpak behavior. Add fixtures for multiple IDEs, missing Toolbox, malformed metadata, and privacy rejection.

Checkpoint commit.

## Job 3 — Targeted compatibility/game/manual application inventory

Extend the reviewed catalog for the explicit non-package candidates that need it, including where feasible:
- Insync
- AnyDesk
- ModernUO
- Ultima Online
- Star Trek Fleet Command
- GOG Galaxy
- ChatGPT/Codex desktop or CLI presence if not already represented by package inventory.

Use only narrow evidence appropriate to each application: known command names, known desktop IDs, reviewed application markers, or narrowly scoped launcher/vendor metadata.

For Wine/compatibility-managed software, do not enumerate arbitrary prefixes or inspect Wine registries. If a specific application's presence cannot be determined safely and deterministically, represent that source as unknown/deferred rather than broadening collection.

Document which candidates are deterministically discoverable and which remain unresolved. Add tests.

Checkpoint commit.

## Job 4 — Operational CachyOS mappings and candidate desired state

Populate real data structures without granting mutation authority.

Create or update the operational CachyOS software mapping for logical IDs whose implementation mapping is confidently known from existing repository evidence or normalized local observations. Mapping sources may be extended beyond repo/foreign/flatpak only when the planner can reconcile them against the targeted read-only evidence introduced in this batch.

Create a candidate workstation desired-state document separate from the non-authoritative example. It should include the explicit software candidates above using portable logical IDs and sensible review categories such as development, creative, productivity, communication, cloud, and gaming.

Do not guess required versus optional. Where intent cannot be derived from repository/user-supplied input, encode the uncertainty in a companion review/curation document rather than silently choosing.

The candidate manifest must not contain distro package names, desktop filenames, install commands, user paths, or launcher implementation details.

Add validation/mapping tests and document how this candidate becomes authoritative only after human review.

Checkpoint commit.

## Job 5 — Real read-only workstation reconciliation run

On the user's normal CachyOS session, run the expanded read-only collector and then the planner against the candidate desired state.

Do not commit the raw .workbench/inspections snapshot.

Produce a sanitized review artifact under docs/reviews/ that summarizes only:
- which logical candidates are satisfied;
- which are missing;
- which are observation-unknown;
- which lack or have ambiguous mappings;
- which installed software is observed-but-unmanaged at a category/count level where listing all identifiers would add noise or privacy risk;
- inventory sources that remain deferred.

Before recording a specific software result in the committed review, ensure it is appropriate for this public repository and comes from an allowlisted logical ID. Do not publish a raw full installed-package list.

No remediation is allowed in this job. A missing desired item remains a planning result only.

Checkpoint commit.

## Job 6 — Machine-profile linkage and Batch 002 review gate

Update the HP Envy Workbench status to point to the dedicated research repository:

https://github.com/sgalland/hp-envy-b-f-research

Keep Workbench's audio material as a status/safety pointer; do not duplicate ongoing codec research or modify audio.

Review the pre-existing tracked HP Envy audio documentation for stale wording only as needed to make ownership boundaries clear. Do not touch the untracked experimental-kernel directory.

Run the complete automated suite and perform a documentation consistency pass.

Create docs/reviews/workbench-batch-002-review.md recording:
- checkpoint commits;
- tests and results;
- new inventory capabilities;
- candidate desired-state status and unresolved human-curation decisions;
- real read-only reconciliation summary;
- privacy/safety audit;
- remaining inventory gaps;
- confirmation that no system mutation occurred.

Stop after the review gate. Do not begin KDE feasibility work, settings-value capture, installation/removal, or apply/rollback implementation.

## Expected checkpoint sequence

1. targeted manual-software discovery framework
2. JetBrains Toolbox/IDE inventory
3. targeted compatibility/game/manual application inventory
4. operational mappings + candidate desired state
5. real read-only reconciliation run
6. machine-profile linkage + Batch 002 review gate

If safe deterministic discovery is not possible for a candidate, preserve unknown/deferred status. Do not solve uncertainty by broad filesystem scanning or privacy-sensitive inspection.
