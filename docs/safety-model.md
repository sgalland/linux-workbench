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

This initial scaffold documents the safety model and project intent only. The HP Envy laptop's problematic Bang & Olufsen internal-speaker configuration is explicitly deferred; do not diagnose or change it under this scaffold.
