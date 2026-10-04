# HP Envy Workbench status

The dedicated [HP Envy B&F research repository](https://github.com/sgalland/hp-envy-b-f-research)
is authoritative for the current audio investigation, findings, and status.

Workbench retains the [2026-09-27 safety record](audio-investigation-2026-09-27.md)
of a failed live HDA sysfs pin-reconfiguration experiment. It documents that
experiment and its recovery, not the state of later research. Read it before
future audio work; the proposed pin override was never applied successfully.

Workbench inventory, comparison, and planning do not diagnose or change this
audio configuration.

The [fingerprint-reader investigation](fingerprint-investigation.md) identifies
the ELAN `04f3:0c4c` USB reader. Stock support appears absent; an experimental
`libfprint` driver exists. Recognition by the installed `fprintd` remains
unconfirmed because the read-only D-Bus query was blocked in this environment.

The [SD card-reader investigation](sd-card-reader-investigation.md) identifies
the Realtek `10ec:5228` PCIe reader and a confirmed kernel/module-tree mismatch.
The reader detected media under the stale `7.2.8-1-cachyos` kernel but could not
load modular `mmc_block`; after rebooting into installed `7.2.9-1-cachyos`,
`mmcblk0` and both card partitions appeared. The reader is confirmed working.
