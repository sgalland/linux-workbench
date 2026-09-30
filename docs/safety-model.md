# Safety model

Linux Workbench treats system mutation as a separately gated activity. A request to inspect, document, or plan does not authorize applying changes. The repository rules in [`AGENTS.md`](../AGENTS.md) apply to all agents.

## Required lifecycle

Every authorized system configuration change follows:

**inspect → plan → backup → apply → verify → rollback**

Inspect the relevant state, describe the intended change and recovery path, back up mutable configuration, apply only the approved operation, verify the result, and roll back if verification fails. Keep changes minimal and reversible.

## Approval boundaries

Explicit approval is required for the specific privileged operation before using `sudo`. Explicit approval is also required before installing or removing packages, or changing services, boot configuration, partitions, firmware, networking, audio configuration, or desktop configuration. Approval is operation-specific. A plan, generated command, or prior approval for another operation does not authorize execution.

Repository documentation and code changes may be made when requested. This does not grant permission to mutate the operating system.

## Data handling and durable records

Never expose, commit, print, or request secrets or API keys. Back up mutable configuration before changing it. Verify applied changes and record reusable discoveries in the repository. Keep shared intent in `spec/`, implementation details in `adapters/`, and machine-specific details in `machines/`.

## Current scope

The current Workbench commands are read-only inspection, comparison, and
planning. The HP Envy laptop's problematic Bang & Olufsen internal-speaker
configuration remains deferred; do not diagnose or change it under this batch.

`./workbench plan` classifies portable intent against a sanitized snapshot
using data-only adapter mappings. Its output is a proposal for review, not
authorization. `missing` describes an observed gap, including for optional
intent; it is not an install instruction. Unknown observations suppress that
classification, and unmanaged installed software produces no removal action.
Batch 004 adds fixture-only transaction machinery. A dry-run returns a plan
fingerprint and narrow backup scope without mutation. Fixture authorization
binds one transaction ID, the exact plan fingerprint, and a digest of the
observed pre-state. Drift invalidates it. The fixture runner rejects any
backend that is not explicitly marked fixture-only. No production
authorization issuer, live apply command, or live backend is present. An
agent's receipt of a batch instruction or generated plan is never live
authorization. A later live executor would require a separate human-issued
approval bound to the exact reviewed transaction and a fresh pre-state check.
