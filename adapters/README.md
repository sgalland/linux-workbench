# Adapters

This directory holds implementation-specific mappings from the abstract workstation specification to supported distributions, desktop environments, and tools.

CachyOS is the initial distribution target. KDE Plasma is the first desktop environment to investigate. Keep Plasma-specific settings and mechanisms here; they must not become assumptions in the abstract specification. Linux Workbench may take inspiration from Omarchy's agentic ideas without depending on Omarchy. Agents and model providers are replaceable; Codex is only the initial local agent.

Any system change remains subject to [`../AGENTS.md`](../AGENTS.md) and the lifecycle in [`../docs/safety-model.md`](../docs/safety-model.md).
