# Architecture

Linux Workbench separates desired workstation behavior from the mechanisms and machine details used to realize it.

## Repository layers

- **`spec/`** — machine-independent user intent and desired behavior. It should avoid assuming a particular distribution, desktop, agent, or provider.
- **`adapters/`** — implementation mappings for distributions, desktop environments, and other tools. The initial investigation targets are CachyOS and KDE Plasma. Plasma-specific implementation remains here, outside the abstract specification.
- **`machines/`** — machine-specific profiles and documented hardware or local constraints. The first planned profile is for the HP Envy laptop. Its Bang & Olufsen internal-speaker issue is recorded as deferred work; no diagnosis or fix is planned in this scaffold.
- **`docs/`** — human-readable project decisions, principles, safety model, and staged roadmap.

## Agent-managed workflow

Agents can inspect current state, help develop a plan, and investigate unfamiliar behavior. Once an approach is understood, reusable steps should be represented declaratively or as deterministic automation where practical. Agents are replaceable interfaces to this workflow; the project does not depend on Codex or any model or provider.

## Read-only discovery design

Discovery uses deterministic local collection code intended for the normal user session. The collector summarizes and sanitizes relevant system, desktop, device, and session facts into reviewable output. Agents should analyze that sanitized output rather than depend on their own execution sandbox having direct access to every desktop, audio, USB, or user-session facility. Collection remains read-only and does not imply authorization to apply a plan.

Reviewed settings-surface paths and categories live in `adapters/surfaces.py`,
including the small KDE Plasma set. The collector only checks metadata for
those fixed paths and emits logical IDs and presence states. Desktop file
details do not enter the machine-independent specification.

Reviewed application evidence lives in `adapters/software.py`. It checks only
fixed commands and exact desktop markers; compatibility and game sources
without safe deterministic markers remain unknown. The operational CachyOS
mapping binds portable IDs to this read-only evidence. The 22-item candidate
manifest remains undecided pending human review.

Portable desired-state IDs, intent, and review categories are defined in
`spec/desired-state.md`. CachyOS software identifiers live in a separate
adapter mapping. Neither file is an apply mechanism; observed state is never
automatically promoted into desired intent.

The candidate desktop outcomes in `spec/desktop-intent.candidate.json` use
portable logical IDs and four human-facing workspace names. KDE mechanisms,
support classifications, alternatives, future surfaces, and verification
strategies live only in `adapters/kde-desktop.candidate.json`. Both are
validation-only candidate data; neither implements a desktop change.

## System change lifecycle

Any separately authorized system configuration change follows **inspect → plan → backup → apply → verify → rollback**. Store reusable plans and discoveries in the repository, but never treat a generated plan as authorization to execute it.
