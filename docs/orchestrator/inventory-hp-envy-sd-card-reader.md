# Inventory HP Envy SD card reader

Investigate the HP Envy SD card reader as a bounded, read-only hardware-support task and record durable findings in Linux Workbench.

## Goal

Determine exactly what SD/card-reader hardware is present, how the current CachyOS/Linux stack enumerates it, what driver or subsystem is responsible, and why inserted media may not currently be usable.

## Requirements

- Treat this as an investigation first, not a driver-installation or system-modification task.
- Identify the exact card-reader controller/device using read-only local inspection. Record stable PCI/USB/vendor/product identifiers when available.
- Determine whether the reader is exposed through PCI, USB, MMC/SDHCI, Realtek/Ricoh/O2Micro/Genesys or another subsystem; do not assume the transport in advance.
- Record relevant kernel driver binding, loaded-module state, udev enumeration, block-device/MMC state, and concise current-boot kernel messages related to the reader or card insertion.
- Where possible, distinguish:
  - reader/controller not enumerated;
  - controller enumerated but no driver bound;
  - driver bound but no media detected;
  - media detected but no block device/filesystem exposed;
  - known kernel quirk/firmware/platform issue;
  - hardware or support state still unknown.
- If an SD card is currently inserted, use only read-only inspection and do not mount, format, repair, write to, benchmark, or modify the card.
- Use repository-local evidence and read-only host commands first. Internet/upstream research may be summarized only when tied to the exact hardware identifier or observed driver; clearly separate local observations from external claims.
- Do **not** install/remove packages, load/unload modules, change module parameters, write udev rules, change firmware/BIOS settings, patch the kernel, mount filesystems, or alter host configuration.
- Do not use `sudo` for mutating operations. If a useful diagnostic requires privilege, document the proposed command for follow-up instead of performing it.
- Do not modify files outside this repository.
- Preserve privacy: omit storage serial numbers, filesystem contents, user data, and unrelated hardware identifiers.

## Suggested read-only evidence

Use only commands that are applicable to the observed hardware. Examples include:

- `lspci -nnk`
- `lsusb` / `lsusb -t`
- `lsblk`
- `lsmod`
- `udevadm info`
- `journalctl -k -b` filtered to the identified controller/driver or MMC/SD events
- relevant `/sys` inspection under PCI, USB, MMC, block, or driver paths
- installed kernel/package version metadata when useful

Do not run commands merely to create a large generic machine dump.

## Deliverables

- Create `machines/hp-envy/sd-card-reader-investigation.md` containing:
  - hardware/controller identification;
  - local kernel/driver state;
  - media-detection observations;
  - evidence and commands used;
  - observed support/failure classification;
  - relevant upstream/kernel findings if exact-hardware research is needed;
  - remaining uncertainties;
  - recommended next step.
- Update `machines/hp-envy/README.md` with a concise link/status entry if appropriate.
- If the evidence indicates a likely kernel quirk, module parameter, firmware dependency, or out-of-tree patch, describe the proposed remediation and rollback considerations but do not apply it in this task.
- If no card is inserted and insertion is required to distinguish controller support from media detection, record that as a human follow-up rather than guessing.

## Acceptance

The task is successful when the repository contains enough evidence for a human reviewer to decide the next SD-card-reader action without rerunning basic controller/driver discovery, and no host or removable-media configuration has been changed.
