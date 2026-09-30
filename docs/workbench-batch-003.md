# Workbench Batch 003 — KDE Plasma Feasibility + Desktop Intent Mapping

Purpose: complete roadmap v0.4 as a strictly read-only investigation of whether KDE Plasma can realize the workstation interaction requirements in docs/requirements.md. Produce an evidence-backed KDE adapter design and candidate desktop intent. Do not change the desktop.

Complete jobs in order, make one clean checkpoint commit after each job, continue automatically while tests remain green, and stop at the final review gate.

## Global rules

- Read AGENTS.md, docs/requirements.md, docs/architecture.md, docs/roadmap.md, docs/discovery-format.md, and the Batch 001/002 reviews before implementation.
- No sudo, package installation/removal, service changes, desktop changes, shortcut writes, panel/widget changes, activity/virtual-desktop changes, KWin reloads/restarts, audio/network/boot changes, or apply behavior.
- Do not invoke D-Bus methods or helper commands that mutate Plasma/KWin state.
- Do not edit or rewrite KDE configuration files.
- Do not collect KScreen state in this batch.
- Read only reviewed, allowlisted KDE values needed for feasibility. Never serialize complete config files, arbitrary groups/keys, screen IDs, geometry tied to physical displays, activity UUIDs, recent-document data, application histories, widget private data, or arbitrary D-Bus payloads.
- Prefer official current KDE documentation for capability claims. Record version applicability and distinguish documented capability from local observation and project inference.
- Treat missing tools, inaccessible values, and unsupported safe probes as unknown, not as absence.
- Keep KDE-specific mechanisms under adapters/. Keep portable workstation outcomes under spec/ or docs/requirements.md.
- Do not touch the pre-existing untracked machines/hp-envy/experimental-kernel/ directory.
- Preserve existing inspect/compare/plan behavior and privacy guarantees.

## Target desktop outcomes

Evaluate these existing requirements without silently changing them:

- conventional overlapping windows;
- Windows/Microsoft-like application shortcuts where practical;
- Ctrl-centric shortcuts primarily inside applications;
- Super/Meta-centric workstation and window-management shortcuts where practical;
- purpose-oriented named workspaces: Development, General, Office, Creative;
- persistent side dock or control area;
- grouped application drawers/launchers;
- useful system monitors;
- application/system menu from desktop right-click;
- no requirement for retro visual styling.

## Job 1 — KDE evidence model and safe feasibility probes

Create an adapter-owned KDE feasibility/evidence model.

Define a small set of read-only probe types suitable for Plasma/KWin, such as:
- component/version/tool availability;
- exact allowlisted configuration key reads;
- exact allowlisted D-Bus property/introspection reads where demonstrably non-mutating;
- fixed capability declarations backed by official KDE documentation.

Use narrow parsers. Raw command output or full KDE config contents must not enter snapshots.

Record evidence provenance in a normalized form that distinguishes:
- official-documentation capability;
- local read-only observation;
- unknown;
- project inference.

If current Plasma/KWin versions are already safely available from the collector, reuse them rather than adding duplicate probes.

Add fixture/privacy/failure tests and document the feasibility evidence contract.

Checkpoint commit.

## Job 2 — Workspace model feasibility

Evaluate the four named-workspace requirement against:
- KWin virtual desktops;
- Plasma Activities;
- a combination of Activities and virtual desktops.

Do not assume one model is preferred before evaluating it.

At minimum investigate:
- stable human-readable naming;
- keyboard switching;
- window grouping/placement semantics;
- whether desktop widgets/panels can differ by context;
- persistence across login/reboot;
- interaction between Activities and virtual desktops;
- whether current Plasma can remember virtual desktop per Activity;
- automation/configuration surfaces that would eventually be required;
- rollback complexity and portability implications.

Produce an evidence-backed decision record recommending the KDE adapter representation for Development, General, Office, and Creative. The recommendation may use virtual desktops, Activities, both, or explicitly defer if evidence is insufficient.

Do not create, rename, delete, switch, or reconfigure Activities or virtual desktops as part of this job.

Add tests for any new data model or parser.

Checkpoint commit.

## Job 3 — Shortcut and window-interaction feasibility

Map the interaction requirements to KDE mechanisms.

Investigate separately:
- KWin/global shortcuts;
- Plasma/global shortcuts;
- KDE standard application shortcuts;
- application-owned shortcuts that Workbench cannot safely generalize.

Evaluate Windows-like expectations including common window-management operations, launcher/menu activation, desktop/workspace switching, maximize/minimize, tiling/snap behavior, and other requirements already implied by docs/requirements.md.

Build a collision-aware candidate shortcut map that:
- reserves Ctrl-centric combinations primarily for applications;
- prefers Meta/Super for workstation/window actions where supported;
- records defaults/conflicts/limitations;
- never claims control over application-specific shortcuts that KDE cannot centrally guarantee.

Read current shortcut state only through narrow allowlisted mechanisms. Do not dump or commit the complete kglobalshortcutsrc.

No shortcut changes are allowed.

Checkpoint commit.

## Job 4 — Plasma shell, side control area, launchers, monitors, and desktop menu

Evaluate the remaining desktop-shell requirements:

- persistent side dock/control area;
- grouped application drawers/launchers;
- useful system monitors;
- desktop right-click application/system menu;
- conventional overlapping-window workflow.

Investigate built-in Plasma panels/widgets and other KDE-native mechanisms first. Third-party components may be documented as alternatives, but do not install them and do not make them a dependency without strong justification.

For each requirement, classify:
- supported directly;
- supported with limitations;
- workaround/extension required;
- unsupported/unknown.

Record the responsible KDE component, safe configuration surface, expected persistence, and rollback complexity. Do not inspect arbitrary widget state or change panels, widgets, launchers, wallpaper, menus, or window rules.

Checkpoint commit.

## Job 5 — KDE adapter and candidate desktop intent

Turn the feasibility findings into reusable project data.

Create a machine-independent candidate desktop-intent representation for the existing requirements. Keep implementation-neutral logical IDs such as workspace behavior, window interaction, launcher/control-area behavior, monitoring, and desktop-menu behavior.

Create the KDE/Plasma adapter mapping from those logical IDs to the evidence-backed KDE mechanisms from Jobs 2–4.

The adapter must distinguish:
- supported;
- supported-with-limitations;
- workaround-required;
- unsupported;
- unknown.

For configurable items, record the future configuration surface/mechanism and verification strategy, but not mutation commands unless they are clearly marked as non-executable design notes. Do not add apply behavior.

Where multiple viable mechanisms remain, preserve the alternatives and decision rationale rather than hiding ambiguity.

Add validation and architecture-boundary tests.

Checkpoint commit.

## Job 6 — Real read-only KDE audit and Batch 003 review gate

Run the safe read-only KDE feasibility probes in the user's normal CachyOS Plasma session.

Do not commit raw inspection snapshots or complete KDE configuration.

Create docs/reviews/workbench-batch-003-kde-feasibility.md containing a sanitized capability matrix for every target desktop outcome. Include:
- portable requirement;
- KDE mechanism;
- evidence type;
- supported/limited/workaround/unsupported/unknown classification;
- relevant local-state observation when safely available;
- remaining decision or limitation.

Create docs/reviews/workbench-batch-003-review.md containing:
- checkpoint commits;
- complete tests/results;
- KDE/Plasma versions relevant to the investigation;
- workspace-model recommendation and rationale;
- shortcut-model recommendation and unresolved collisions;
- panel/control-area, launcher, system-monitor, and desktop-menu findings;
- candidate desktop-intent/adapter status;
- read-only/privacy audit;
- explicit list of deferred questions;
- confirmation that no desktop or system mutation occurred.

Update docs/roadmap.md only to reflect the actual completed v0.4 boundary; do not mark v0.5 as authorized.

Run the complete automated suite and git diff --check.

Stop after the review gate. Do not begin Batch 004, do not implement backup/apply/rollback, and do not make even a small KDE configuration change without human review and explicit authorization.

## Expected checkpoint sequence

1. KDE evidence model + safe probes
2. workspace-model feasibility
3. shortcut/window-interaction feasibility
4. Plasma shell/control-area/launcher/monitor/menu feasibility
5. KDE adapter + candidate desktop intent
6. real read-only audit + Batch 003 review gate

If a requested behavior cannot be verified safely, preserve unknown status. Do not solve uncertainty by dumping private KDE state or by temporarily changing the desktop.
