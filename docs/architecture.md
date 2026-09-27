# Architecture

Linux Workbench separates desired workstation behavior from the mechanisms and machine details used to realize it.

## Repository layers

- **`spec/`** — machine-independent user intent and desired behavior. It should avoid assuming a particular distribution, desktop, agent, or provider.
- **`adapters/`** — implementation mappings for distributions, desktop environments, and other tools. The initial investigation targets are CachyOS and KDE Plasma. Plasma-specific implementation remains here, outside the abstract specification.
- **`machines/`** — machine-specific profiles and documented hardware or local constraints. The first planned profile is for the HP Envy laptop. Its Bang & Olufsen internal-speaker issue is recorded as deferred work; no diagnosis or fix is planned in this scaffold.
- **`docs/`** — human-readable project decisions, principles, safety model, and staged roadmap.

## Agent-managed workflow

Agents can inspect current state, help develop a plan, and investigate unfamiliar behavior. Once an approach is understood, reusable steps should be represented declaratively or as deterministic automation where practical. Agents are replaceable interfaces to this workflow; the project does not depend on Codex or any model or provider.

## System change lifecycle

Any separately authorized system configuration change follows **inspect → plan → backup → apply → verify → rollback**. Store reusable plans and discoveries in the repository, but never treat a generated plan as authorization to execute it.
