# Linux Workbench

Linux Workbench defines a preferred Linux workstation and a safe, repeatable way to manage its configuration. Its workstation intent is independent of any particular Linux distribution, desktop environment, AI agent, or model provider.

CachyOS is the initial target distribution. KDE Plasma is the first desktop environment to investigate, through an adapter that implements the abstract specification rather than defining it.

## Repository map

- [`AGENTS.md`](AGENTS.md) defines agent safety and working rules.
- [`docs/`](docs/) contains the project vision, requirements, principles, architecture, safety model, and roadmap.
- [`spec/`](spec/) is for machine-independent workstation intent.
- [`adapters/`](adapters/) is for distribution, desktop, and other implementation adapters.
- [`machines/`](machines/) is for machine-specific profiles.

The initial local Git repository convention on this CachyOS installation is `~/Projects`.

## Safety

The lifecycle for any future system configuration change is **inspect → plan → backup → apply → verify → rollback**. Agents must follow [`AGENTS.md`](AGENTS.md). Documentation and code changes in this repository may be made when requested; system changes require separate, explicit authorization as described there.

No system-changing implementation is part of this initial documentation scaffold.

## Read-only commands

`./workbench inspect` writes a sanitized local snapshot under
`.workbench/inspections/`. `./workbench compare <older.json> <newer.json>`
classifies changes. `./workbench plan <desired-state> <snapshot>` classifies
portable intent using `adapters/cachyos-software.json`. Compare and plan read
local snapshots only. See `docs/discovery-format.md` and
`spec/desired-state.md` for formats and limits. None of these commands applies
changes.
