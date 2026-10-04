# Verify HP Envy fingerprint reader with desktop fprintd

Perform the one remaining read-only verification from the prior HP Envy fingerprint-reader investigation: determine whether the installed desktop-session `fprintd` service currently exposes the ELAN `04f3:0c4c` reader.

## Goal

Close the local-runtime uncertainty left by the initial investigation without changing authentication, PAM, packages, drivers, firmware, or biometric state.

## Requirements

- Treat `machines/hp-envy/fingerprint-investigation.md` as the authoritative prior investigation.
- Reconfirm the exact reader remains ELAN USB `04f3:0c4c` before interpreting any `fprintd` result.
- From the normal host environment, perform only read-only queries needed to determine whether `fprintd` exposes the reader.
- Prefer the D-Bus manager `GetDevices` query documented in the prior investigation. Equivalent read-only inspection is acceptable if the exact call is unavailable.
- Record whether the result is:
  - reader exposed by installed `fprintd`;
  - service reachable but no reader exposed;
  - service unavailable/not running;
  - query blocked/insufficiently observable.
- Do not enroll, verify, delete, or list fingerprints.
- Do not modify PAM, login policy, packages, services, udev rules, drivers, kernel modules, firmware, or host configuration.
- Do not use mutating `sudo` commands.
- Do not modify files outside this repository.
- Preserve privacy: do not record biometric data, fingerprint templates, serial numbers, or unrelated device identifiers.

## Deliverables

- Update `machines/hp-envy/fingerprint-investigation.md` with a short follow-up section containing:
  - the exact read-only query used;
  - observed `fprintd` result;
  - resulting support classification;
  - the next recommended action.
- Update `machines/hp-envy/README.md` only if the status meaningfully changes.

## Decision guidance

- If `fprintd` exposes `04f3:0c4c`, stop and document that stock runtime recognition exists; do not enroll.
- If `fprintd` is reachable but exposes no device, record that local stock runtime recognition is absent and recommend a separate human-reviewed evaluation of the experimental `elanmoc2`/patched-libfprint path.
- If the query is still blocked or inconclusive, record the limitation and do not guess.

## Acceptance

The task is successful when the repository clearly records whether the installed desktop `fprintd` stack exposes the ELAN `04f3:0c4c` reader, or clearly records why that question remains unobservable, with no host or biometric state changed.
