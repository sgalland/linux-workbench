# A1 deterministic explanation formatter

Implement the first deterministic human-readable consumer of the A1 explanation evidence bundle.

Requirements:

- Consume the existing `workbenchlib.explanation_evidence.build_bundle()` output or its schema.
- Produce a deterministic human-readable text summary suitable for terminal or CLI display.
- Keep observations, unknown/incomplete evidence, comparison changes, and proposals clearly distinguishable.
- Preserve provenance in the rendered output where the bundle provides it.
- Never turn unknown or inaccessible evidence into absence, success, failure, or another inferred conclusion.
- Preserve stable ordering so equivalent bundles render identically.
- Do not probe the live system, inspect arbitrary user files, invoke shell commands, mutate workstation state, or call any AI/model provider.
- Add focused unit tests for stable ordering, unknown rendering, provenance rendering, missing sections, and malformed bundle input.
- A small read-only CLI surface may be added only if it fits the existing CLI architecture cleanly and consumes explicit bundle/input data.
- Update A1 documentation only enough to describe this formatter substrate.
- Do not claim A1 Explain/Advise is complete.
- Keep this slice intentionally small and deterministic.
