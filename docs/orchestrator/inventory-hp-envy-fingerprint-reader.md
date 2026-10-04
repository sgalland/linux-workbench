# Inventory HP Envy fingerprint reader

Investigate the HP Envy fingerprint reader as a bounded, read-only hardware-support task and record durable findings in Linux Workbench.

## Goal

Determine exactly what fingerprint hardware is present, how the current CachyOS/Linux stack sees it, whether the device is supported by the installed or current upstream fingerprint stack, and what the safest next step should be.

## Requirements

- Treat this as an investigation first, not a driver-installation or system-modification task.
- Identify the exact fingerprint device/controller using read-only local inspection. Record stable identifiers such as USB or PCI vendor/product IDs when available.
- Record relevant kernel/udev enumeration, loaded-driver state, and useful diagnostic output without dumping unrelated machine information.
- Inspect the installed fingerprint software stack where available, including relevant `libfprint` / `fprintd` package versions and whether the device is recognized.
- Determine whether support appears to be:
  - already available but not configured;
  - available in a newer packaged/upstream version;
  - dependent on firmware or an out-of-tree driver;
  - unsupported/unknown.
- Use repository-local evidence and read-only host commands first. Internet research may be summarized only when it can be tied to the exact hardware identifier; clearly separate local observations from external/upstream claims.
- Do **not** enroll fingerprints, alter PAM, change login policy, install/remove packages, load/unload kernel modules, write udev rules, patch drivers, change firmware, or otherwise modify host configuration.
- Do not use `sudo` for mutating operations. If a useful diagnostic requires privilege, document it as a proposed follow-up rather than performing it.
- Do not modify files outside this repository.
- Preserve user privacy: do not record fingerprint templates, biometric data, serial numbers, usernames beyond what is already public in the repository, or unrelated hardware identifiers.

## Deliverables

- Create `machines/hp-envy/fingerprint-investigation.md` containing:
  - hardware identification;
  - local software/driver state;
  - observed support status;
  - evidence and commands used;
  - remaining uncertainties;
  - recommended next step.
- Update `machines/hp-envy/README.md` with a concise link/status entry if appropriate.
- If the device is unsupported and an upstream or third-party driver effort exists, identify it and describe the likely integration path, but do not implement it in this task.
- If evidence is insufficient, say so explicitly rather than guessing.

## Acceptance

The task is successful when the repository contains enough evidence for a human reviewer to decide the next fingerprint-reader action without rerunning basic hardware discovery, and no host configuration has been changed.
