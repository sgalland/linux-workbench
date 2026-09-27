# Discovery snapshot format

`./workbench inspect` writes one sanitized JSON snapshot to
`.workbench/inspections/`. That directory is ignored by Git. The collector
does not stage or update the curated machine baseline. These ephemeral files
include exact collection timestamps for local state comparison and are not
intended for publication or automatic promotion into the public machine
baseline.

## Snapshot fields

- `schema_version` and `collector_version` identify the data and parser
  contract.
- `collected_at` is a UTC timestamp.
- `completeness` reports the probe count, successful probe count, IDs with an
  unavailable/error/not-collected/unknown result, and an overall complete
  flag.
- `probes` contains one record per fixed probe.

Each probe record separates:

- `status`: whether the probe ran and was parsed (`ok`, `missing_tool`,
  `access_denied`, `timeout`, `command_error`, `probe_error`, `parse_error`, `unavailable`,
  `read_error`, or `not_collected`).
- `observation`: `present`, `not_present`, or `unknown`.
- `facts`: normalized values permitted for that probe.
- `provenance`: fixed command arguments or source paths and parser identity.
- `exit_code`, when a process returned an exit code.

An unavailable or failed probe has `observation: unknown` and empty facts.
That state must never be compared as absence or removal. `not_present` is only
used when a successful probe can establish that the relevant collection is
empty. A snapshot with any non-`ok` status or unknown observation is marked
incomplete.

## Initial probe set

The current collector gathers basic OS/kernel/CPU/memory/firmware/storage/PCI
facts; coarse user-session and Plasma/KWin versions; normalized PipeWire
audio endpoints and controls; ALSA card/PCM roles and capabilities; direct
child names and driver links for audio-related sysfs paths; and USB
descriptions/topology. Exact
commands and parsers are defined in `workbenchlib/inspect.py`.

Detailed KScreen state is intentionally `not_collected` until a separately
approved normal-session experiment. EFI inventory is deferred. The collector
does not inspect logs or journal contents.

## Privacy contract

Probe output is processed in memory and never written as raw stdout/stderr.
Only parser allowlists are serialized. The snapshot omits credentials,
environment values other than coarse session facts, serials, UUIDs, MAC/IP
addresses, SSIDs, PCI/USB bus addresses and unique IDs, disk names and mount
paths, display IDs/EDID, audio client/stream identity, arbitrary PipeWire
properties, and persistent PipeWire device identifiers. PipeWire object IDs
may be retained only as within-snapshot relationship keys. Audio mute and
volume controls may be retained in normalized form. USB model descriptions,
hardware class/description, model/vendor fields, and selected device facts
are retained because they support a useful hardware baseline.

This is an initial conservative contract, not a claim that arbitrary future
probes are safe. Each new probe needs a reviewed parser and fixture tests
before it is added.
