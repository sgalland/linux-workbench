# Workbench Batch 002 review gate

## Checkpoints

1. Job 1 — `d6bb61f` — exact, read-only software evidence catalog.
2. Job 2 — `394a4fe` — JetBrains Toolbox and IDE markers, comparison, and planning.
3. Job 3 — `a77dece` — targeted tools and explicit deferred compatibility/game sources.
4. Job 4 — `2195f64` — operational evidence mappings and candidate desired state.
5. Job 5 — `61fa4ef` — sanitized real-session reconciliation review.
6. Job 6 — this review-gate commit; its hash is in the final report.

## Verification

The complete `python3 -m unittest discover -s tests -v` suite passed: 39
tests, zero failures or errors. `git diff --check` passed. Documentation was
checked for stale claims about the operational mapping and research URL.
Fixture coverage includes exact marker matching, private-content rejection,
symlink and missing-PATH uncertainty, multiple IDEs, deferred sources,
targeted plan and comparison states, candidate/mapping consistency, and
snapshot provenance privacy. The real collector and planner ran read-only.

## Inventory and candidate status

The collector now emits fixed-catalog software evidence with stable logical
and evidence IDs, coarse source classes, and present/absent/unknown state.
It checks exact commands and desktop IDs without recording their paths or
contents. JetBrains IDEs, Insync, AnyDesk, Codex CLI, and GitHub CLI have
targeted checks. Compatibility/game candidates with no safe deterministic
source remain explicit unknown/deferred rows. Compare and plan handle these
rows without changing pacman or Flatpak behavior.

The candidate desired-state manifest contains 22 portable software IDs in
review categories. All intents are undecided; the manifest is not
authoritative. The CachyOS mapping binds each to one reviewed evidence ID,
including deferred IDs. Human review must decide which items are required,
optional, or unwanted; whether ChatGPT and Codex are separate goals; and
whether each command/launcher marker is sufficient for its installed form.

## Real reconciliation

The [sanitized reconciliation](workbench-batch-002-reconciliation.md) records
11 satisfied markers, 6 missing markers, and 5 observation-unknown candidates.
No candidate lacks a mapping or has an ambiguous mapping. The planner found
240 explicit repository and 9 explicit foreign package identifiers outside
the curated mapping, reported here only as counts. Flatpak collection was
unknown because its tool was unavailable. Missing markers are narrow evidence
results and are not proof that software is absent by every possible source.

## Privacy, safety, and remaining gaps

Raw command output was parsed in memory; the ignored local snapshot was not
committed. This batch removed inherited timestamp and source-path fields from
snapshot contents and sanitized the ignored inspection used for Job 5. The
public reviews contain only allowlisted candidate names and aggregate counts,
never a full installed-package list. No arbitrary home tree, Wine prefix,
registry, browser, account, credential, project, game data, or KScreen state
was inspected. AppImage/manual installs beyond fixed markers, ChatGPT desktop,
GOG Galaxy, ModernUO, Star Trek Fleet Command, Ultima Online, and the
unavailable Flatpak inventory remain gaps. Exact marker checks do not cover
all possible installation methods.

The HP Envy status now links to the dedicated research repository while
retaining the dated failed-reconfiguration safety record. No system mutation
occurred: no installs/removals, service, boot, network, audio, or desktop
changes. No apply functionality or KDE feasibility work began. The
pre-existing untracked experimental-kernel directory was not changed.
