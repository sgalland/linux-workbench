# Roadmap

The roadmap begins with documentation and read-only understanding. Each later system-changing operation remains subject to the approval and safety rules in [`safety-model.md`](safety-model.md) and [`AGENTS.md`](../AGENTS.md). A roadmap item is not authorization to execute it.

## v0.1 — Constitution and architecture

Establish project intent, requirements, principles, architecture, safety rules, and repository boundaries. This initial documentation scaffold covers v0.1.

## v0.2 — Read-only system discovery and baseline

Define and perform approved read-only discovery of the initial CachyOS environment. Implement discovery as deterministic local collection code running in the normal user session; have agents analyze its sanitized output instead of relying on direct access from their execution sandbox. Record a useful baseline without changing system state. Access failures limited to an agent sandbox must not be described as failures of the underlying CachyOS session without independent evidence.

## v0.3 — State comparison and planning

Describe how desired intent and observed state can be compared, and how proposed changes can be presented for review without applying them.

## v0.4 — KDE Plasma feasibility investigation

Batch 003 completed the read-only feasibility investigation and produced a candidate KDE adapter, portable desktop intent, and [review gate](reviews/workbench-batch-003-review.md). Four named virtual desktops are the current recommendation, pending human review. No desktop configuration was changed. This boundary does not authorize v0.5.

## v0.5 — First controlled reversible mutation

Batch 004 prepared the mutation transaction model, private backup substrate,
KWin 6.7.5 workspace adapter design, fixture lifecycle proof, and a sanitized
four-workspace live dry-run. The pilot is [awaiting exact human authorization](reviews/workbench-batch-004-workspace-pilot.md).
No live desktop change has been applied. A future approved transaction must
revalidate pre-state, back up, apply, verify, and roll back on failure under
the safety lifecycle. This roadmap entry grants no authorization.


## AI capability track

AI-oriented capabilities are tracked separately in [AI Capabilities Roadmap](ai-capabilities-roadmap.md). That track is intentionally orthogonal to the numbered workstation configuration batches: read-only reasoning, diagnostics, knowledge distillation, and bounded agent orchestration may advance without un-deferring broader workstation mutation work such as Batch 005.
