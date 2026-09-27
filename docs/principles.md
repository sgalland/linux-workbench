# Principles

## Intent before implementation

The specification describes the user's desired outcomes and behavior. It should not prescribe a distribution-specific command, desktop setting, or implementation detail unless that detail is itself a requirement. Adapters translate intent into supported implementation choices.

## Portable core, replaceable edges

Keep workstation intent independent of Linux distribution, desktop environment, agent, and model provider. Put environment-specific behavior in adapters and hardware-specific behavior in machine profiles. CachyOS, KDE Plasma, and Codex are initial choices for exploration, not architectural dependencies.

## Solve once, automate reliably

Use agents for discovery and novel problems. Once a solution is understood and reviewed, encode it as deterministic automation or declarative configuration where practical. Reuse should reduce repeated reasoning and make behavior inspectable.

## Reviewable and reversible

Prefer version-controlled declarations, small changes, explicit plans, and recoverable operations. For system changes, follow **inspect → plan → backup → apply → verify → rollback**. A plan is not permission to apply it.

## Familiar interaction

Prefer conventional overlapping windows and practical Windows/Microsoft application shortcuts. Use Ctrl-centric shortcuts mainly within applications and reserve Super preferentially for workstation and window-management actions. Workspaces should be named by purpose. Desktop features should support a practical workflow without prescribing a retro appearance.

## Record durable knowledge

Capture reusable discoveries and decisions in the repository so future work does not depend on conversational memory. Keep machine-specific observations out of the shared abstract specification.
