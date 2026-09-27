# Requirements

This document records current workstation intent. It describes desired behavior, not a binding choice of implementation or configuration mechanism.

## Portability and management

- Keep core workstation intent independent of distribution, desktop environment, AI agent, and model provider.
- Treat CachyOS as the initial target distribution.
- Investigate KDE Plasma first, but implement its specifics through an adapter.
- Support agent-managed configuration, drawing inspiration from Omarchy's agentic ideas without depending on Omarchy.
- Make agents replaceable. Codex is the initial local agent; the project must not depend on Codex, ChatGPT, Mistral, or any particular provider or model.
- Prefer deterministic automation after a solution is understood. Encode successful solutions so routine application does not require repeated AI reasoning.
- Prefer declarative, version-controlled configuration where practical.
- Separate shared workstation intent from machine-specific profiles.

## Desktop interaction

- Prefer conventional overlapping windows.
- Where practical, application keybindings should follow familiar Windows/Microsoft conventions.
- Keep Ctrl-centric shortcuts primarily within applications. Prefer Super for workstation and window-management shortcuts to reduce conflicts.
- Use purpose-oriented, named workspaces. Initial concepts are Development, General, Office, and Creative.
- Provide a persistent side dock or control area.
- Provide grouped application drawers.
- Provide useful system monitors.
- Provide an application/system menu from the desktop right-click action.

These desktop concepts express behavior inspired by older Unix and NeXT-style workflows. They do not require a retro visual design.

## Initial environment and profile

- The initial target distribution is CachyOS.
- KDE Plasma is the first desktop environment to investigate and remains an adapter.
- The local Git repository convention on this CachyOS installation is `~/Projects`.
- The first machine profile will eventually cover this HP Envy laptop, including its problematic Bang & Olufsen internal-speaker configuration. Audio diagnosis and changes are explicitly deferred.
