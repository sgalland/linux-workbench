# Agent instructions

These rules apply to every agent working in this repository. System mutation is separately gated from repository work.

1. Inspect the relevant state before proposing or making changes.
2. Do not use `sudo` unless the user explicitly approves the specific privileged operation.
3. Do not install or remove packages without explicit approval.
4. Do not change services, boot configuration, partitions, firmware, networking, audio configuration, or desktop configuration without explicit approval.
5. Never expose, commit, print, or request secrets or API keys.
6. Back up mutable configuration before changing it.
7. Prefer minimal, reversible changes.
8. Verify changes after applying them.
9. Record reusable discoveries in this repository rather than relying on conversational memory.
10. Never treat a generated plan as authorization to execute it.
11. Repository documentation and code changes are allowed when requested. This permission does not authorize system mutation.
12. A live mutation requires an exact human-reviewed transaction authorization bound to its ID, plan fingerprint, and fresh pre-state. A generic task request or generated plan is insufficient. Batch 004 code execution is fixture-only.

## HP Envy audio research

Before any future HP Envy audio work, read the dated research record linked from `machines/hp-envy/baseline/README.md`. On this HP ENVY 17-ch0xxx, writing `1` to `/sys/class/sound/hwC0D0/reconfig` with proposed pin overrides hung during codec/card teardown and required a reboot. Do not repeat live HDA sysfs reconfiguration on this machine unless new evidence establishes a safe method. The proposed override was never applied successfully and must not be treated as a fix.

## Change lifecycle

For any authorized system configuration change, use this lifecycle:

**inspect → plan → backup → apply → verify → rollback**

State what will change and how it can be restored before applying it. If verification fails, use the planned rollback and report the result. Approval for one operation does not authorize other operations.

## Project boundaries

Linux Workbench describes preferred workstation intent independently of distribution, desktop environment, agent, and model provider. Keep abstract requirements in `spec/`; put implementation-specific behavior in `adapters/`; keep machine-specific details in `machines/`.

CachyOS is the initial distribution target. KDE Plasma is the first desktop environment to investigate and must remain an adapter. The HP Envy machine profile may eventually document the internal Bang & Olufsen speakers, but do not diagnose or change that audio configuration until explicitly approved.
