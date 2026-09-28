# HP Envy baseline

Read-only discovery baseline for the initial CachyOS machine profile. Collected 2026-09-27. Facts below summarize command output; raw command dumps are intentionally not retained.

## Collection limits

- Commands ran unprivileged in the Codex execution environment. Failures to reach live-session or device facilities below describe limits of this run only. There is no independent evidence here that the CachyOS user session itself has the same failures.
- `kscreen-doctor -o` aborted in this execution environment and reported a core dump. This does not establish a failure of the CachyOS display session. The dump was not inspected or removed. No XWayland display query was attempted, per the approved collection plan.
- `lsusb` could not initialize libusb in this execution environment. `lsusb -t` did expose USB topology. This is not evidence that host USB enumeration fails.
- PipeWire/WirePlumber session queries could not access the user service/audio session from this environment. `/proc/asound` and relevant kernel messages were readable. `aplay -l` and `arecord -l` reported no soundcards from this environment, which is not evidence that the CachyOS host session has no ALSA devices.
- No configuration was changed and no diagnosis or repair of the known internal-speaker problem was attempted.

## Files

- [`system.md`](system.md) — OS, kernel, platform, memory, storage, and EFI summary.
- [`devices.md`](devices.md) — PCI, graphics, USB, and network hardware summary.
- [`desktop.md`](desktop.md) — session type, Plasma version, and display-query outcome.
- [`audio.md`](audio.md) — ALSA, SOF/HDA, related buses, session API availability, and relevant kernel observations.
- [`audio-investigation-2026-09-27.md`](../audio-investigation-2026-09-27.md) — speaker observations, failed live sysfs reconfiguration, recovery, and safety constraints.
- [`development.md`](development.md) — requested tool availability and versions.

All files are summarized for a public repository. Unique identifiers, serials, UUIDs, network addresses/names, user-specific mount paths, and unrelated log lines were omitted.
