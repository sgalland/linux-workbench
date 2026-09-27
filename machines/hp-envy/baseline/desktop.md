# Desktop and display baseline

- Session type: Wayland.
- Current desktop identifier: KDE.
- KDE session generation: 6.
- KWin version: 6.7.5. The `plasmashell --version` check did not return a version in the Codex execution environment; this does not establish a host Plasma failure.
- `kscreen-doctor -o` was the approved authoritative display query for this Wayland Plasma session, but it aborted in the Codex execution environment with a core-dump message. This is a collection limitation, not evidence of a CachyOS display failure. No display count, connector, mode, or scaling facts could be recorded from it.
- `xrandr` was not run because no specific need to inspect the XWayland view was identified.

The Codex execution environment exposed a Plasma Wayland session marker, but display details remain unverified. No KDE or desktop configuration was read or changed.
