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

Batch 004 established the mutation transaction model, private backup substrate,
fixture lifecycle proof, and four-workspace pilot design. Batch 004B added the
narrow production KWin 6.7.5 executor, one-time authorization store, lifecycle
runner, and operator CLI, then correctly stopped when the live D-Bus signature
did not match the declared interface metadata. Batch 004C source-verified that
KWin 6.7.5 declares `a(iss)` in its interface XML while its C++ runtime
structure marshals `a(uss)`, added exact-version regression coverage, and
completed a fresh read-only preflight.

The current reviewed pilot remains `kde-four-workspaces-v1` with fingerprint
`67b55bbe399a0eee08843d5b2ae86b83c95da3651c0a1c9f4bc0232e5b9d7963`.
The fresh Batch 004C preflight matched the original reviewed fingerprint.
See the [Batch 004C review gate](reviews/workbench-batch-004c-review.md) and
[pilot sheet](reviews/workbench-batch-004c-workspace-pilot.md).

No production authorization has been issued and no live desktop mutation has
been applied. Any future execution must still receive explicit human
authorization for the exact current transaction/fingerprint and revalidate
pre-state before backup/apply/verify/rollback.

## Batch 005 — Broader workstation reconciliation and configuration

**Status: explicitly deferred.**

Do not begin broader workstation reconciliation/configuration work merely
because v0.5 machinery exists. Resume Batch 005 only when the user explicitly
promotes it again. Read-only AI capability work may continue independently.


## AI capability track

AI-oriented capabilities are tracked separately in [AI Capabilities Roadmap](ai-capabilities-roadmap.md). That track is intentionally orthogonal to the numbered workstation configuration batches: read-only reasoning, diagnostics, knowledge distillation, and bounded agent orchestration may advance without un-deferring broader workstation mutation work such as Batch 005.
