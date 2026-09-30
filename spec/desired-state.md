# Desired-state format v1

A desired-state JSON object has `schema_version: 1`, a `software` list, and a
`settings_surfaces` list. Each entry has a portable logical `id`, an `intent`
of `required`, `optional`, or `undecided`, and a `review_category`. `undecided`
records candidates awaiting human curation and grants no authority to fulfill
a plan. Planner classifications describe evidence only. Logical IDs describe
what the user wants, not an implementation. Categories group human review;
they do not authorize changes. A settings surface expresses future management
intent only. The format contains no commands or target-specific identifiers.

[`desired-state.example.json`](desired-state.example.json) is a small
non-authoritative fixture. Observed software is never implicitly desired.
Validation is implemented by `workbenchlib.desired.validate_desired`.

[`desired-state.candidate.json`](desired-state.candidate.json) lists the
user-supplied workstation candidates with `undecided` intent. It is not the
authoritative desired state. The companion
[`candidate-curation.md`](candidate-curation.md) records the decisions needed
before promotion: whether each candidate is required, optional, or unwanted,
and whether the reviewed evidence source is sufficient.

The target-specific, data-only mapping example is in
[`../adapters/cachyos-software.example.json`](../adapters/cachyos-software.example.json).
Each mapping names a logical software ID, source (`repo`, `foreign`, `flatpak`,
or `targeted`), and the concrete identifier. A targeted identifier is a fixed
catalog evidence ID. Mappings grant no installation
authority. Multiple mappings may be supplied for review; the planner treats
conflicts conservatively.

`adapters/cachyos-software.json` is the operational mapping data read by the
CLI. Its current mappings reconcile exact catalog evidence only. The
`.example.json` file is illustrative and is not loaded by the CLI.
