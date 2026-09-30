# Desired-state format v1

A desired-state JSON object has `schema_version: 1`, a `software` list, and a
`settings_surfaces` list. Each entry has a portable logical `id`, an `intent`
of `required` or `optional`, and a `review_category`. Logical IDs describe
what the user wants, not an implementation. Categories group human review;
they do not authorize changes. A settings surface expresses future management
intent only. The format contains no commands or target-specific identifiers.

[`desired-state.example.json`](desired-state.example.json) is a small
non-authoritative fixture. Observed software is never implicitly desired.
Validation is implemented by `workbenchlib.desired.validate_desired`.

The target-specific, data-only mapping example is in
[`../adapters/cachyos-software.example.json`](../adapters/cachyos-software.example.json).
Each mapping names a logical software ID, source (`repo`, `foreign`, or
`flatpak`), and the concrete identifier. Mappings grant no installation
authority. Multiple mappings may be supplied for review; the planner treats
conflicts conservatively.

`adapters/cachyos-software.json` is the operational mapping data read by the
CLI. It starts empty. The `.example.json` file is illustrative and is not
loaded by the CLI.
