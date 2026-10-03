# Reconcile HP Envy audio status

Update only the Linux Workbench documentation boundary for HP Envy audio.

Requirements:

- Keep `hp-envy-b-f-research` identified as the authoritative repository for current audio investigation.
- Keep `machines/hp-envy/audio-investigation-2026-09-27.md` as a historical safety record.
- Correct the status-page wording so the failed 2026-09-27 live sysfs pin-reconfiguration experiment is not presented as the current overall state of later research.
- Do not duplicate detailed findings from the dedicated research repository.
- Preserve the boundary that Linux Workbench inventory, comparison, and planning do not diagnose or change the audio configuration.
- Do not modify system configuration, kernel state, audio state, or files outside this repository.
- Prefer changing only `machines/hp-envy/README.md` unless another documentation link must be corrected for consistency.
