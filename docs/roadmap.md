# Roadmap

The roadmap begins with documentation and read-only understanding. Each later system-changing operation remains subject to the approval and safety rules in [`safety-model.md`](safety-model.md) and [`AGENTS.md`](../AGENTS.md). A roadmap item is not authorization to execute it.

## v0.1 — Constitution and architecture

Establish project intent, requirements, principles, architecture, safety rules, and repository boundaries. This initial documentation scaffold covers v0.1.

## v0.2 — Read-only system discovery and baseline

Define and perform approved read-only discovery of the initial CachyOS environment. Record a useful baseline without changing system state.

## v0.3 — State comparison and planning

Describe how desired intent and observed state can be compared, and how proposed changes can be presented for review without applying them.

## v0.4 — KDE Plasma feasibility investigation

Investigate whether KDE Plasma can support the desired desktop behaviors through an adapter. Keep findings and limitations separate from the abstract specification. Do not change desktop configuration as part of investigation without explicit approval.

## v0.5 — First controlled reversible mutation

Design one small, explicitly approved system change with a backup and rollback path, then apply and verify it under the safety lifecycle. Selection of a change and any approval remain future steps; this roadmap entry grants no authorization.
